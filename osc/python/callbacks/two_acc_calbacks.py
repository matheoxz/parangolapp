import threading
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
        self.bpm            = 120  # default BPM
        self.note_length    = 0.5  # default note length (in beats)
        # raw accelerometer buffers
        self.top_buffer    = AccelerometerData(buffer_len)
        self.bottom_buffer = AccelerometerData(buffer_len)
        # arpeggio settings
        self.chord_idx = 0
        self.note_idx  = 0
        self.drum_flag = True
        self.arp_mode = ArpeggiatorMode.THIRD_OCTAVE
        self.chord_list = [ (msc.Note.C, msc.Chord.MAJ, 4),
                            (msc.Note.A, msc.Chord.MIN, 4),
                            (msc.Note.F, msc.Chord.MAJ, 4),
                            (msc.Note.G, msc.Chord.MAJ, 4)]
        self.chords = ArpeggiatorUtils.create_arpeggio(self.chord_list, self.arp_mode)

    def handle_arp_style(self, address, *args):
        """OSC /arp/style — print the style string."""
        style = args[0] if args else None
        print(f"[OSC] /arp/style → {style}")
        if style == "up":
            self.arp_mode = ArpeggiatorMode.UP
        elif style == "down":
            self.arp_mode = ArpeggiatorMode.DOWN
        elif style == "up down":
            self.arp_mode = ArpeggiatorMode.UP_DOWN
        elif style == "down up":
            self.arp_mode = ArpeggiatorMode.DOWN_UP
        elif style == "random":
            self.arp_mode = ArpeggiatorMode.RANDOM
        elif style == "third octaved":
            self.arp_mode = ArpeggiatorMode.THIRD_OCTAVE
        else:
            print(f"[OSC] /arp/style → unknown style: {style}")
        
        self.chords = ArpeggiatorUtils.create_arpeggio(self.chord_list, self.arp_mode)
    
    def handle_chords(self, address, *args):
        """OSC /chords — print the chord list string."""
        chord_list_str = args[0] if args else None
        print(f"[OSC] /chords → {chord_list_str}")
        try:
            chord_list = msc.parse_chord_list(chord_list_str)
            self.chord_list = chord_list
            self.chords = ArpeggiatorUtils.create_arpeggio(self.chord_list, self.arp_mode)
            print(f"[CHORDS] Set to {self.chord_list}")
        except Exception as e:
            print(f"[OSC] /chords → invalid chord list: {chord_list_str} ({e})")

    def handle_slider(self, address, *args):
        """OSC /slider — map to MIDI CC."""
        try:
            print(f"[OSC] slider → {args}")
            cc = int(args[0])
            val = int(args[1])
            val = max(0, min(127, val))
            # CC message: 0xB0 = control change on channel 0
            self.midi_player.midi_queues[2].put((0, [0xB0, 11 + cc, val]))
        except (IndexError, ValueError):
            print(f"[OSC] /slider → invalid value: {args}")

    def handle_note_length(self, address, *args):
        try:
            print(f"[OSC] /note/length → {args}")
            length_str = args[0]
            # parse into number of beats
            if "/" in length_str:
                num, den = length_str.split("/", 1)
                beats = float(num) / float(den)
            else:
                beats = float(length_str)
            # convert beats → seconds using current bpm
            seconds = beats * 60.0 / self.bpm
            self.note_length = seconds
            self.midi_player.duration = self.note_length
            print(f"[NOTE LENGTH] Set to {self.note_length} beats")
        except (IndexError, ValueError):
            print(f"[OSC] /note/length → invalid value: {args}")

    def handle_bpm(self, address, *args):
        """OSC /bpm."""
        try:
            print(f"[OSC] /bpm → {args}")
            self.bpm = int(args[0])
            self.midi_player.set_bpm(self.bpm)
            print(f"[BPM] Set to {self.bpm}")
        except (IndexError, ValueError):
            print(f"[OSC] /bpm → invalid value: {args}")

    def handle_drums(self,address, *args):
        """OSC /drums — just print whatever was received."""
        if args[0] == 'on':
            self.drum_flag = True
        else:
            self.drum_flag = False
        print(f"[OSC] /drums → {args}")



    def acc_play_drum(self, midi_port=1):
        if not self.drum_flag:
            return
        #check orientation and remove gravity
        linear_accel = self.top_buffer.remove_gravity()
        x, y, z = linear_accel[-1]

        # Simple threshold-based drum triggering
        threshold = 12.0  # adjust as needed
        if z > threshold:
            # Low tom
            if self.midi_player.midiouts[midi_port]:
                print(f"[MIDI] Playing Low Tom")
                self.midi_player.play_async_note(41, 100, channel=10, duration=0.1, midi_port=midi_port)
        elif z < -threshold:
            # Tom drum
            if self.midi_player.midiouts[midi_port]:
                print(f"[MIDI] Playing Tom Drum")
                self.midi_player.play_async_note(45, 100, channel=10, duration=0.1, midi_port=midi_port)

        if y > threshold:
            # Snare drum
            if self.midi_player.midiouts[midi_port]:
                print(f"[MIDI] Playing Snare Drum")
                self.midi_player.play_async_note(38, 100, channel=10, duration=0.1, midi_port=midi_port)
        elif y < -threshold:
            # Hi-hat
            if self.midi_player.midiouts[midi_port]:
                print(f"[MIDI] Playing Hi-Hat")
                self.midi_player.play_async_note(42, 100, channel=10, duration=0.1, midi_port=midi_port)

        if x > threshold:
            # Kick drum
            if self.midi_player.midiouts[midi_port]:
                print(f"[MIDI] Playing Kick Drum")
                self.midi_player.play_async_note(36, 100, channel=10, duration=0.1, midi_port=midi_port, sync=True)
        elif x < -threshold:
            # Open hi-hat
            if self.midi_player.midiouts[midi_port]:
                print(f"[MIDI] Playing Open Hi-Hat")
                self.midi_player.play_async_note(46, 100, channel=10, duration=0.1, midi_port=midi_port, sync=True)

    def handle_top_acc(self, address, *args):
        #print(f"[OSC] {address}: {args}")
        if len(args) >= 3:
            x, y, z = args[:3]
            with self.acc_lock:
                self.top_buffer.add(x, y, z)
                self.acc_play_drum(midi_port=1)
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
                vel = MIDIUtils.map_to_velocity(en)

                if self.midi_player.midiouts[0] and en > 5:
                    print(f"[MIDI] Arpeggiating chord {self.chord_idx}, note {note}")
                    self.midi_player.play_sync_note(note, vel)
                    self.note_idx += 1
                    if self.note_idx >= len(chord):
                        self.note_idx = 0
                        self.chord_idx = (self.chord_idx + 1) % len(self.chords)
                else:
                    if self.midi_player.midiouts[0]:
                        last_chord = self.chords[(self.chord_idx - 1) % len(self.chords)]
                        for n in last_chord:
                            self.midi_player.midiouts[0].send_message([0x80, n, 0])
                    while not self.midi_player.midi_queues[0].empty():
                        self.midi_player.midi_queues[0].get()

        #print(f"bottom last signal data: {self.bottom_buffer.getLastSample()}")
        #print(f"bottom buffers: {self.bottom_buffer.get().tolist()}")