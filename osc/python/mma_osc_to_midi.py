import sys
import rtmidi
import matplotlib
matplotlib.use('Qt5Agg')

from osc_server import GenericOSCServer
from callbacks.saia_arp_callbacks import TwoAccArpeggiatorCallbacks
from signal_utils.plotter import GenericPlotter
from midi_utils.midi_utils import MIDIPlayer, MIDIUtils
from midi_utils.arp_utils import ArpeggiatorMode, ArpeggiatorUtils
import music_data.music_structures as msc

# MIDI setup
midiout = rtmidi.MidiOut()
ports = midiout.get_ports()
idx = next((i for i, p in enumerate(ports) if "loopMIDI" in p and ("1" in p or "Port 1" in p)), None)
if idx is None:
    print("LoopMIDI port 1 not found. Available ports:", ports)
    sys.exit(1)
midiout.open_port(idx)

# configure MIDIPlayer and start its thread
MIDIPlayer.midiout = midiout
MIDIPlayer.start_midi_thread()

# create arpeggiator callback instance
buffer_len = 200

arp = TwoAccArpeggiatorCallbacks(MIDIPlayer, buffer_len)

# OSC server setup with instance methods
handlers = [
    ("/top/acc",    arp.handle_top_acc),
    ("/bottom/acc", arp.handle_bottom_acc),
    ("/arp/style",            arp.handle_arp_style),
    ("/instrument/effect/1",  arp.handle_instrument_effect_1),
    ("/instrument/effect/2",  arp.handle_instrument_effect_2),
    ("/drums",                arp.handle_drums),
]
server = GenericOSCServer("parangole_mma_to_midi", "0.0.0.0", 8000, handlers)
server.start()

# Plotting code
def plot_window():
    P = arp.buffer_len
    configs = [
        {
            'data': arp.top_buffer.get(),
            'lock': arp.acc_lock,
            'title': 'Top Accelerometer (/top/acc)',
            'labels': ['x', 'y', 'z'],
            'ylim': (-50, 50),
        },
        {
            'data': arp.bottom_buffer.get(),
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
