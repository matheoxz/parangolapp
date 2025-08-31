from collections import deque

class ThreeAxisBuffer:
    """
    Generic buffer for three-axis signals (e.g., accelerometer, gyroscope).
    """
    def __init__(self, size):
        self.x = deque(maxlen=size)
        self.y = deque(maxlen=size)
        self.z = deque(maxlen=size)

    def add(self, xv, yv, zv):
        """Add a new sample to the buffer."""
        self.x.append(xv)
        self.y.append(yv)
        self.z.append(zv)

    def get(self):
        """Retrieve all buffered samples as lists."""
        return list(self.x), list(self.y), list(self.z)
