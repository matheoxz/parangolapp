import threading
import numpy as np
from signal_data.three_axis_buffer import  ThreeAxisBuffer
from callbacks.acc_features import skewness, kurtosis

class AccelerationCallbacks:
    """
    Static handlers and buffers for accelerometer OSC signals.
    """
    PLOT_LEN = 200
    acc_data_top = np.zeros((PLOT_LEN, 3))
    acc_data_bottom = np.zeros((PLOT_LEN, 3))
    acc_lock = threading.Lock()
    latest_acc_y = None
    top_buffer = ThreeAxisBuffer(PLOT_LEN)
    bottom_buffer = ThreeAxisBuffer(PLOT_LEN)
    # Buffers for computed features over time
    skew_data = np.zeros((PLOT_LEN, 3))
    kurt_data = np.zeros((PLOT_LEN, 3))

    @classmethod
    def handle_top_acc(cls, address, *args):
        print(f"[OSC] {address}: {args}")
        if len(args) >= 3:
            x, y, z = args[:3]
            with cls.acc_lock:
                cls.acc_data_top[:] = np.roll(cls.acc_data_top, -1, axis=0)
                cls.acc_data_top[-1] = [x, y, z]
            cls.latest_acc_y = y
            cls.top_buffer.add(x, y, z)

    @classmethod
    def handle_bottom_acc(cls, address, *args):
        print(f"[OSC] {address}: {args}")
        if len(args) >= 3:
            x, y, z = args[:3]
            with cls.acc_lock:
                # update raw data buffer
                cls.acc_data_bottom[:] = np.roll(cls.acc_data_bottom, -1, axis=0)
                cls.acc_data_bottom[-1] = [x, y, z]
                # add to ThreeAxisBuffer
                cls.bottom_buffer.add(x, y, z)
                # update skewness buffer
                cls.skew_data[:] = np.roll(cls.skew_data, -1, axis=0)
                cls.skew_data[-1] = skewness(cls.bottom_buffer)
                # update kurtosis buffer
                cls.kurt_data[:] = np.roll(cls.kurt_data, -1, axis=0)
                cls.kurt_data[-1] = kurtosis(cls.bottom_buffer)

    