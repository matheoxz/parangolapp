import sys
import signal_data
import numpy as np
import rtmidi
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5.QtWidgets import QApplication
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from osc_server import GenericOSCServer
from callbacks.saia_arp_callbacks import AccelerationCallbacks
from signal_utils.plotter import GenericPlotter

from callbacks.acc_features import skewness, kurtosis, _to_array

# MIDI setup
midiout = rtmidi.MidiOut()
ports = midiout.get_ports()
idx = next((i for i, p in enumerate(ports) if "loopMIDI" in p and ("1" in p or "Port 1" in p)), None)
if idx is None:
    print("LoopMIDI port 1 not found. Available ports:", ports)
    sys.exit(1)
midiout.open_port(idx)
# inject MIDI output into callbacks for arpeggiator
AccelerationCallbacks.midiout = midiout
AccelerationCallbacks.start_midi_thread()

# OSC server setup
handlers = [
    ("/top/acc", AccelerationCallbacks.handle_top_acc),
    ("/bottom/acc", AccelerationCallbacks.handle_bottom_acc),
]
server = GenericOSCServer("parangole_mma_to_midi", "0.0.0.0", 8000, handlers)
server.start()

# Plotting code
def plot_window():
    # Configure plot data for generic plotter
    P = AccelerationCallbacks.PLOT_LEN
    configs = [
        {
            'data': AccelerationCallbacks.acc_data_top,
            'lock': AccelerationCallbacks.acc_lock,
            'title': 'Top Accelerometer (/top/acc)',
            'labels': ['x', 'y', 'z'],
            'ylim': (-50, 50),
        },
        {
            'data': AccelerationCallbacks.acc_data_bottom,
            'lock': AccelerationCallbacks.acc_lock,
            'title': 'Bottom Accelerometer (/bottom/acc)',
            'labels': ['x', 'y', 'z'],
            'ylim': (-50, 50),
        },
        {
            'data': AccelerationCallbacks.energy_mag_hist[:, None],
            'lock': AccelerationCallbacks.acc_lock,
            'title': 'Mean Abs Energy History',
            'labels': ['mag'],
            'ylim': (50, 50),
        },
    ]
    plotter = GenericPlotter(data_configs=configs, plot_len=P, interval=50)
    plotter.show()

if __name__ == '__main__':
    plot_window()
