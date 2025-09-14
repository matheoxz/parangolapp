import numpy as np

class AccelerometerData:
    """
    Buffer for accelerometer data with feature extraction methods.
    """
    def __init__(self, size: int):
        self.size        = size
        self.buffer_x    = np.zeros(size, dtype=float)
        self.buffer_y    = np.zeros(size, dtype=float)
        self.buffer_z    = np.zeros(size, dtype=float)
        self._initialized = False

    def add(self, xv: float, yv: float, zv: float):
        """Add new sample with FIFO eviction when full."""
        # on first sample, fill entire buffer so you don't see zeros
        if not self._initialized:
            self.buffer_x.fill(xv)
            self.buffer_y.fill(yv)
            self.buffer_z.fill(zv)
            self._initialized = True
            return
        # roll each 1D buffer left by one and write new value at the end
        self.buffer_x = np.roll(self.buffer_x, -1)
        self.buffer_y = np.roll(self.buffer_y, -1)
        self.buffer_z = np.roll(self.buffer_z, -1)
        self.buffer_x[-1] = xv
        self.buffer_y[-1] = yv
        self.buffer_z[-1] = zv

    def get(self) -> np.ndarray:
        """Retrieve buffered samples as an (N,3) numpy array."""
        return np.column_stack((self.buffer_x, self.buffer_y, self.buffer_z))

    @property
    def buffer(self) -> np.ndarray:
        """Alias for get(): returns current buffer as (N,3) array."""
        return self.get()

    def getLastSample(self) -> tuple[float, float, float]:
        """Return the most recent sample added."""
        idx = self.size-1
        return float(self.buffer_x[idx]), float(self.buffer_y[idx]), float(self.buffer_z[idx])
    
    def step_counter(self, threshold: float = 1.0) -> int:
        """Count steps based on threshold crossings in the z-axis."""
        arr = self.get()
        z = arr[:, 2]
        count = 0
        above_threshold = False
        for value in z:
            if value > threshold and not above_threshold:
                count += 1
                above_threshold = True
            elif value <= threshold:
                above_threshold = False
        return count

    def skewness(self) -> np.ndarray:
        """Calculate the skewness of the signal."""
        arr = self.get()
        m = arr.mean(axis=0)
        s = arr.std(axis=0)
        return (( (arr - m)**3 ).mean(axis=0)) / (s**3 + 1e-8)

    def kurtosis(self) -> np.ndarray:
        """Calculate the kurtosis of the signal."""
        arr = self.get()
        m = arr.mean(axis=0)
        s = arr.std(axis=0)
        return (( (arr - m)**4 ).mean(axis=0)) / (s**4 + 1e-8) - 3

    def energy(self) -> np.ndarray:
        """Compute the energy of the signal."""
        arr = self.get()
        return (arr**2).sum(axis=0)
    
    def orientation(self) -> np.ndarray:
        """Estimate device orientation (pitch, roll, yaw) from latest sample."""
        x, y, z = self.getLastSample()
        pitch = np.arctan2(x, np.sqrt(y**2 + z**2)) * (180.0 / np.pi)
        roll  = np.arctan2(y, np.sqrt(x**2 + z**2)) * (180.0 / np.pi)
        yaw   = np.arctan2(z, np.sqrt(x**2 + y**2)) * (180.0 / np.pi)
        return np.array([pitch, roll, yaw])
    
    def remove_gravity(self) -> np.ndarray:
        """Estimate linear acceleration by removing gravity using a simple high-pass filter."""
        alpha = 0.8  # smoothing factor
        gravity = np.zeros(3)
        linear_accel = np.zeros((self.size, 3))
        arr = self.get()
        for i in range(self.size):
            gravity = alpha * gravity + (1 - alpha) * arr[i]
            linear_accel[i] = arr[i] - gravity
        return linear_accel
    
    def instantEnergy(self) -> np.ndarray:
        """Compute the instantaneous energy of the latest sample."""
        sample = self.getLastSample()
        return np.sqrt(np.sum(np.array(sample)**2))

    def mean(self) -> np.ndarray:
        """Calculate the mean value of the signal."""
        return self.get().mean(axis=0)

    def median(self) -> np.ndarray:
        """Calculate the median value of the signal."""
        return np.median(self.get(), axis=0)

    def variance(self) -> np.ndarray:
        """Compute the variance of the signal."""
        return self.get().var(axis=0)

    def std(self) -> np.ndarray:
        """Calculate the standard deviation of the signal."""
        return self.get().std(axis=0)

    def rms(self) -> np.ndarray:
        """Compute the root mean square value of the signal."""
        return np.sqrt((self.get()**2).mean(axis=0))

    def zero_crossing_rate(self) -> np.ndarray:
        """Calculate the zero-crossing rate of the signal."""
        arr = self.get()
        def zcr(a):
            s = np.sign(a)
            return ((s[:-1] * s[1:] < 0).sum() / max(len(a)-1, 1))
        return np.array([zcr(arr[:, i]) for i in range(3)])

    def mobility_complexity(self) -> tuple[np.ndarray, np.ndarray]:
        """Estimate the mobility and complexity of the signal."""
        arr = self.get()
        mobility = []
        complexity = []
        for i in range(3):
            x = arr[:, i]
            dx = np.diff(x)
            ddx = np.diff(dx)
            varx = x.var()
            vardx = dx.var()
            varddx = ddx.var()
            m = np.sqrt(vardx / (varx + 1e-8))
            c = np.sqrt(varddx / (vardx + 1e-8)) / (m + 1e-8)
            mobility.append(m)
            complexity.append(c)
        return np.array(mobility), np.array(complexity)

    def jerk_magnitude(self, dt: float = 1.0) -> np.ndarray:
        """Compute the magnitude of the jerk signal."""
        arr = self.get()
        diff = np.diff(arr, axis=0) / dt
        return np.linalg.norm(diff, axis=1)
