import sys
import threading
import rtmidi
import queue
import time
from music_data.music_structures import Note, Scale, Chord


class MIDIPlayer:
    """Class to handle MIDI playback."""
    
    def __init__(self, port_name: str = "Parangolapp Virtual Port", duration: float = 0.125, bpm: int = 120):
        self.port_name = port_name
        self.duration = duration
        # per-port queues and threads
        self.midi_queues: list[queue.Queue] = []
        self.midi_threads: list[threading.Thread] = []
        self.stop_thread = False
        self.midi_clock_thread = None
        self.stop_clock = False
        self.bpm = bpm
        # discover ports and init queues
        self.find_loopmidi()

    def find_loopmidi(self):
        """Discover all loopMIDI ports and open them."""
        self.midiouts = []
        temp = rtmidi.MidiOut()
        ports = temp.get_ports()
        for idx, name in enumerate(ports):
            if "loopMIDI" in name:
                m = rtmidi.MidiOut()
                m.open_port(idx)
                self.midiouts.append(m)
        # init a queue per port
        self.midi_queues = [queue.Queue() for _ in self.midiouts]
        print(f"Found {len(self.midiouts)} loopMIDI ports.")
        if not self.midiouts:
            print("No loopMIDI ports found. Available ports:", ports)
            sys.exit(1)

    def start_midi_thread(self):
        """Start background threads to process MIDI queues and clock."""
        # spawn one worker per port
        if not self.midi_threads and self.midiouts:
            for idx, m_out in enumerate(self.midiouts):
                def make_worker(q, out):
                    def worker():
                        while not self.stop_thread:
                            try:
                                delay, msg = q.get(timeout=0.1)
                                if delay > 0:
                                    time.sleep(delay)
                                out.send_message(msg)
                            except queue.Empty:
                                continue
                    return worker
                t = threading.Thread(target=make_worker(self.midi_queues[idx], m_out), daemon=True)
                self.midi_threads.append(t)
                t.start()
            # start clock on first port
            self.start_midi_clock()

    def stop_midi_thread(self):
        """Stop MIDI processing and clock threads."""
        # stop clock first
        self.stop_midi_clock()
        self.stop_thread = True
        # join per-port threads
        for t in self.midi_threads:
            t.join()
        self.midi_threads.clear()

    def play_async_note(self, note: int, velocity: int, channel: int = 0, duration: float = None, midi_port: int = 0, sync: bool = True):
        """Play a MIDI note (on/off) asynchronously with its own timers."""
        duration = duration if duration is not None else self.duration
        if not self.midiouts:
            return
        port = midi_port if 0 <= midi_port < len(self.midiouts) else len(self.midiouts) - 1
        # calculate sync delay only for first note
        start_delay = 0.0
        if sync:
            interval = 60.0 / (self.bpm * 24)
            remainder = time.time() % interval
            start_delay = interval - remainder
        on_msg = [0x90 | channel, note, velocity]
        off_msg = [0x80 | channel, note, 0]
        threading.Timer(start_delay, lambda: self.midiouts[port].send_message(on_msg)).start()
        threading.Timer(start_delay + duration, lambda: self.midiouts[port].send_message(off_msg)).start()

    def play_sync_note(self, note: int, velocity: int, channel: int = 0, duration: float = None, midi_port: int = 0, sync: bool = True):
        """Queue a MIDI note on/off on a specific port, playing sequentially."""
        duration = duration if duration is not None else self.duration
        if not self.midiouts:
            return
        port = midi_port if 0 <= midi_port < len(self.midiouts) else len(self.midiouts) - 1
        # sync first note when queue empty
        start_delay = 0.0
        if sync and self.midi_queues[midi_port].empty():
            interval = 60.0 / (self.bpm * 24)
            start_delay = interval - (time.time() % interval)
        # enqueue sequential playback
        self.midi_queues[midi_port].put((start_delay, [0x90 | channel, note, velocity]))
        self.midi_queues[midi_port].put((start_delay + duration, [0x80 | channel, note, 0]))

    def play_chord(self, chord: Chord, velocity: int, midi_port: int = 0):
        """Play a MIDI chord (on/off) in parallel."""
        if not self.midiouts:
            return
        # trigger each chord note without sync
        for note in chord.value:
            self.play_async_note(note, velocity, midi_port=midi_port, sync=True)

    def start_midi_clock(self, midi_port: int = 0):
        """Send MIDI Clock (0xF8) at 24 ppqn on a specific port."""
        self.stop_clock = False
        if not self.midiouts:
            return
        interval = 60.0 / (self.bpm * 24)
        def _clock_worker():
            while not self.stop_clock:
                port = midi_port if 0 <= midi_port < len(self.midiouts) else len(self.midiouts) - 1
                self.midiouts[port].send_message([0xF8])
                time.sleep(interval)
        self.midi_clock_thread = threading.Thread(target=_clock_worker, daemon=True)
        self.midi_clock_thread.start()

    def stop_midi_clock(self):
        self.stop_clock = True
        if self.midi_clock_thread:
            self.midi_clock_thread.join()
            self.midi_clock_thread = None

    def set_bpm(self, bpm: int, midi_port: int = 0):
        """Update BPM and restart MIDI clock on a given port."""
        self.bpm = bpm
        self.stop_midi_clock()
        self.start_midi_clock(midi_port)

    def set_midiout(self, midiout):
        """Attach MIDI output port and start processing thread and clock."""
        self.midiouts.append(midiout)
        self.start_midi_thread()

class MIDIUtils:
    """Utility functions for MIDI note calculations."""

    @staticmethod
    def map_to_velocity(val: float,
                        in_min: float = 0.0,
                        in_max: float = 100.0,
                        out_min: int = 1,
                        out_max: int = 127) -> int:
        """Map a float value from one range to another, clamped to output range."""
        # Clamp input value to input range
        val_clamped = max(min(val, in_max), in_min)
        # Normalize input value to [0, 1]
        normalized_val = (val_clamped - in_min) / (in_max - in_min)
        # Scale to output range
        scaled_val = normalized_val * (out_max - out_min) + out_min
        return int(round(scaled_val))
    
    @staticmethod
    def midi_scale(root: Note, scale: Scale, octave: int) -> list[int]:
        notes = scale.value
        root_offset = (root.value + 12) * octave - (root.value + 12) * (octave - 1)
        return [n.value + root_offset for n in notes]

    @staticmethod
    def midi_scales(root: Note, scale: Scale, octaves: list[int]) -> list[list[int]]:
        return [MIDIUtils.midi_scale(root, scale, o) for o in octaves]

    @staticmethod
    def midi_chord(root: Note, modes: Chord, octave: int) -> list[int]:
        print(f"[MIDIUtils] Generating chord for root {root}, modes {modes.value}, octave {octave}")
        intervals = modes.value
        root_offset = (root.value + 12) * octave - (root.value) * (octave - 1)
        print(f"[MIDIUtils] Chord intervals (octave {octave}): {intervals} with root offset {root_offset}")
        print(f"[MIDIUtils] Resulting MIDI notes: {[n.value + root_offset for n in intervals]}")
        return [n.value + root_offset for n in intervals]

    @staticmethod
    def midi_chords(chord_specs: list[tuple[Note, set[Chord]]], octaves: list[int]) -> list[list[int]]:
        return [MIDIUtils.midi_chord(root, modes, o) for o in octaves for root, modes in chord_specs]

    @staticmethod
    def midi_chord_octave_third(root: Note, mode: Chord, octave: int, reps: int = 4) -> list[int]:
        if mode not in (Chord.MAJ, Chord.MIN):
            raise ValueError("mode must be Chord.MAJ or Chord.MIN")
        chord = MIDIUtils.midi_chord(root, {mode}, octave)
        return [chord[0], chord[2], chord[1] + 12] * reps