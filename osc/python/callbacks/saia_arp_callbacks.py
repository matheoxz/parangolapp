import threading
import numpy as np
import queue
import time
import random
from signal_data.three_axis_buffer import AccelerometerData
import music_data.music_structures as msc
from midi_utils.midi_utils import MIDIPlayer, MIDIUtils
from midi_utils.arp_utils import ArpeggiatorMode, ArpeggiatorUtils
class TwoAccArpeggiatorCallbacks:
    """
    Static handlers and buffers for accelerometer OSC signals.
    """
    def __init__(self,
                 midi_player: MIDIPlayer,
                 buffer_len: int):
        self.midi_player   = midi_player
        self.buffer_len    = buffer_len
        self.acc_lock      = threading.Lock()
        # raw accelerometer buffers
        self.top_buffer    = AccelerometerData(buffer_len)
        self.bottom_buffer = AccelerometerData(buffer_len)
        # arpeggio settings
        self.chord_idx = 0
        self.note_idx  = 0
        self.chord_list = [ (msc.Note.C, msc.Chord.MAJ, 4),
                            (msc.Note.A, msc.Chord.MIN, 4),
                            (msc.Note.F, msc.Chord.MAJ, 4),
                            (msc.Note.G, msc.Chord.MAJ, 4)]
        self.chords = ArpeggiatorUtils.create_arpeggio(self.chord_list, ArpeggiatorMode.THIRD_OCTAVE)

    def handle_arp_style(self, address, *args):
        """OSC /arp/style — print the style string."""
        style = args[0] if args else None
        print(f"[OSC] /arp/style → {style}")
        if style == "up":
            self.chords = ArpeggiatorUtils.create_arpeggio(self.chord_list, ArpeggiatorMode.UP)
        elif style == "down":
            self.chords = ArpeggiatorUtils.create_arpeggio(self.chord_list, ArpeggiatorMode.DOWN)
        elif style == "up down":
            self.chords = ArpeggiatorUtils.create_arpeggio(self.chord_list, ArpeggiatorMode.UP_DOWN)
        elif style == "down up":
            self.chords = ArpeggiatorUtils.create_arpeggio(self.chord_list, ArpeggiatorMode.DOWN_UP)
        elif style == "random":
            self.chords = ArpeggiatorUtils.create_arpeggio(self.chord_list, ArpeggiatorMode.RANDOM)
        elif style == "third octaved":
            self.chords = ArpeggiatorUtils.create_arpeggio(self.chord_list, ArpeggiatorMode.THIRD_OCTAVE)
        else:
            print(f"[OSC] /arp/style → unknown style: {style}")

    def handle_instrument_effect_1(self, address, *args):
        """OSC /instrument/effect/1 — map to MIDI CC13."""
        try:
            print(f"[OSC] /instrument/effect/1 → {args}")
            val = int(args[0])
            val = max(0, min(127, val))
            # CC message: 0xB0 = control change on channel 0
            MIDIPlayer.midi_queue.put((0, [0xB0, 13, val]))
        except (IndexError, ValueError):
            print(f"[OSC] /instrument/effect/1 → invalid value: {args}")

    def handle_instrument_effect_2(self, address, *args):
        """OSC /instrument/effect/2 — map to MIDI CC14."""
        try:
            print(f"[OSC] /instrument/effect/2 → {args}")
            val = int(args[0])
            val = max(0, min(127, val))
            MIDIPlayer.midi_queue.put((0, [0xB0, 14, val]))
        except (IndexError, ValueError):
            print(f"[OSC] /instrument/effect/2 → invalid value: {args}")

    def handle_drums(self,address, *args):
        """OSC /drums — just print whatever was received."""
        print(f"[OSC] /drums → {args}")


    def handle_top_acc(self, address, *args):
        #print(f"[OSC] {address}: {args}")
        if len(args) >= 3:
            x, y, z = args[:3]
            with self.acc_lock:
                self.top_buffer.add(x, y, z)

                en = self.top_buffer.instantEnergy() - 9.81
                vel   = MIDIUtils.map_to_velocity(en)
                note = random.randint(36, 48)
                if self.midi_player.midiout and en > 3:
                    print(f"[MIDI] Playing note {note} with velocity {vel}")
                    self.midi_player.play_note(note, vel, channel=2, duration= 1/en if en < 20 else 0.05)
                else:
                    if self.midi_player.midiout:
                        self.midi_player.midiout.send_message([0x80, note, 0])
                    while not self.midi_player.midi_queue.empty():
                        self.midi_player.midi_queue.get()
        #print(f"top last signal data: {self.top_buffer.getLastSample()}")
        #print(f"top buffers: {self.top_buffer.get().tolist()}")

    def handle_bottom_acc(self, address, *args):
        #print(f"[OSC] {address}: {args}")
        if len(args) >= 3:
            x, y, z = args[:3]
            with self.acc_lock:
                # update raw data buffer
                self.bottom_buffer.add(x, y, z)

                # compute energy and store history
                en = self.bottom_buffer.instantEnergy() - 9.81  # subtract gravity

                chord = self.chords[self.chord_idx]
                try:
                    note  = chord[self.note_idx]
                except IndexError:
                    self.note_idx = 0
                    note  = chord[self.note_idx]
                vel   = MIDIUtils.map_to_velocity(en)

                if self.midi_player.midiout and en > 5:
                    print(f"[MIDI] Arpeggiating chord {self.chord_idx}, note {note}")
                    self.midi_player.play_note(note, vel)
                    self.note_idx += 1
                    if self.note_idx >= len(chord):
                        self.note_idx = 0
                        self.chord_idx = (self.chord_idx + 1) % len(self.chords)
                else:
                    if self.midi_player.midiout:
                        last_chord = self.chords[(self.chord_idx - 1) % len(self.chords)]
                        for n in last_chord:
                            self.midi_player.midiout.send_message([0x80, n, 0])
                    while not self.midi_player.midi_queue.empty():
                        self.midi_player.midi_queue.get()
        
        #print(f"bottom last signal data: {self.bottom_buffer.getLastSample()}")
        #print(f"bottom buffers: {self.bottom_buffer.get().tolist()}")