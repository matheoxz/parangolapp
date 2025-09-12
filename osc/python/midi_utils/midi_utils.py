import threading
import numpy as np
import queue
import time
from music_data.music_structures import Note, Scale, Chord


class MIDIPlayer:

    """Class to handle MIDI playback."""
    
    # MIDI output port name
    midi_port_name = "Parangolapp Virtual Port"
    # Optional MIDI output instance, to be set by main script
    midiout = None
    # Duration for each arpeggiated note (seconds)
    duration = 0.125
    # Queue and thread for non-blocking MIDI events
    midi_queue = queue.Queue()
    midi_thread = None
    stop_thread = False
    
    @classmethod
    def start_midi_thread(cls):
        """Start background thread to process MIDI queue."""
        if cls.midi_thread is None and cls.midiout:
            def worker():
                while not cls.stop_thread:
                    try:
                        delay, msg = cls.midi_queue.get(timeout=0.1)
                        if delay > 0:
                            time.sleep(delay)
                        cls.midiout.send_message(msg)
                    except queue.Empty:
                        continue
            cls.midi_thread = threading.Thread(target=worker, daemon=True)
            cls.midi_thread.start()
    
    @classmethod
    def stop_midi_thread(cls):
        """Stop the MIDI processing thread."""
        cls.stop_thread = True
        if cls.midi_thread:
            cls.midi_thread.join()
            cls.midi_thread = None

    @classmethod
    def play_note(cls, note: int, velocity: int, channel: int = 0, duration: float = None):
        """Queue a MIDI note on and note off event."""
        duration = duration if duration is not None else cls.duration
        if cls.midiout:
            # Note on
            cls.midi_queue.put((0, [0x90 | channel, note, velocity]))
            # Note off after duration
            cls.midi_queue.put((duration, [0x80 | channel, note, 0]))

    @classmethod
    def play_chord(cls, chord: Chord, velocity: int):
        """Queue MIDI note on and note off events for a chord."""
        if cls.midiout:
            # Note on for all notes
            for note in chord.value:
                cls.midi_queue.put((0, [0x90, note, velocity]))
            # Note off after duration
            for note in chord.value:
                cls.midi_queue.put((cls.duration, [0x80, note, 0]))


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