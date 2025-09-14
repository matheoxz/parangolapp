import sys

import matplotlib
matplotlib.use('Qt5Agg')

from osc_server import GenericOSCServer
from callbacks.two_acc_calbacks import TwoAccArpeggiatorCallbacks
from signal_utils.plotter import GenericPlotter
from midi_utils.midi_utils import MIDIPlayer

# configure MIDIPlayer and start its thread
midi_player = MIDIPlayer()
midi_player.start_midi_thread()

# create arpeggiator callback instance
buffer_len = 200

arp = TwoAccArpeggiatorCallbacks(midi_player, buffer_len)

# OSC server setup with instance methods
handlers = [
    ("/top/acc", arp.handle_top_acc),
    ("/bottom/acc", arp.handle_bottom_acc),
    ("/arp/style", arp.handle_arp_style),
    ("/slider", arp.handle_slider),
    ("/note/length", arp.handle_note_length),
    ("/bpm", arp.handle_bpm),
    ("/drums", arp.handle_drums),
    ("/chords", arp.handle_chords),
]
server = GenericOSCServer("parangole_mma_to_midi", "0.0.0.0", 8000, handlers)
server.start()

# Plotting code
def plot_window():
    P = arp.buffer_len
    configs = [
        {
            'data': arp.top_buffer.get,
            'lock': arp.acc_lock,
            'title': 'Top Accelerometer (/top/acc)',
            'labels': ['x', 'y', 'z'],
            'ylim': (-50, 50),
        },
        {
            'data': arp.bottom_buffer.get,
            'lock': arp.acc_lock,
            'title': 'Bottom Accelerometer (/bottom/acc)',
            'labels': ['x', 'y', 'z'],
            'ylim': (-50, 50),
        }
    ]
    plotter = GenericPlotter(data_configs=configs, plot_len=P, interval=50)
    plotter.show()

if __name__ == '__main__':
    
    plot_window()
