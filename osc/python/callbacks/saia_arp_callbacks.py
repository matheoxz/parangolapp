import threading
import numpy as np
import queue
import time
from signal_data.three_axis_buffer import AccelerometerData
import music_data.music_structures as msc
from midi_utils.midi_utils import MIDIPlayer, MIDIUtils
class TwoAccArpeggiatorCallbacks:
    """
    Static handlers and buffers for accelerometer OSC signals.
    """
    def __init__(self,
                 midi_player: MIDIPlayer,
                 buffer_len: int,
                 chords: list[list[msc.Note]]):
        self.midi_player   = midi_player
        self.buffer_len    = buffer_len
        self.acc_lock      = threading.Lock()
        # raw accelerometer buffers
        self.top_buffer    = AccelerometerData(buffer_len)
        self.bottom_buffer = AccelerometerData(buffer_len)
        # arpeggio settings
        self.chords    = chords
        self.chord_idx = 0
        self.note_idx  = 0

    def handle_top_acc(self, address, *args):
        print(f"[OSC] {address}: {args}")
        if len(args) >= 3:
            x, y, z = args[:3]
            with self.acc_lock:
                self.top_buffer.add(x, y, z)

        #print(f"top last signal data: {self.top_buffer.getLastSample()}")
        #print(f"top buffers: {self.top_buffer.get().tolist()}")

    def handle_bottom_acc(self, address, *args):
        print(f"[OSC] {address}: {args}")
        if len(args) >= 3:
            x, y, z = args[:3]
            with self.acc_lock:
                # update raw data buffer
                self.bottom_buffer.add(x, y, z)

                # compute energy and store history
                en = self.bottom_buffer.instantEnergy() - 9.81  # subtract gravity

                chord = self.chords[self.chord_idx]
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