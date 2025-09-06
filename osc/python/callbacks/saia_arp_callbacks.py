import threading
import numpy as np
import queue
import time
from signal_data.three_axis_buffer import ThreeAxisBuffer
from callbacks.acc_features import energy, skewness
import music_data.music_structures as msc

class AccelerationCallbacks:
    """
    Static handlers and buffers for accelerometer OSC signals.
    """
    PLOT_LEN = 200

    acc_data_top = np.zeros((PLOT_LEN, 3))
    acc_data_bottom = np.zeros((PLOT_LEN, 3))
    acc_lock = threading.Lock()

    top_buffer = ThreeAxisBuffer(PLOT_LEN)
    bottom_buffer = ThreeAxisBuffer(PLOT_LEN)

    # Buffers for computed features over time
    skew_data = np.zeros((PLOT_LEN, 3))
    kurt_data = np.zeros((PLOT_LEN, 3))
    energy_data = np.zeros((PLOT_LEN, 3))

    # Chords for arpeggiation
    chords = [msc.midi_chord_octave_third('C', 'maj', 4),
              msc.midi_chord_octave_third('A', 'min', 4),
              msc.midi_chord_octave_third('F', 'maj', 4),
              msc.midi_chord_octave_third('G', 'maj', 4)]

    chord_idx = 0
    note_idx = 0
    # Optional midi output instance, to be set by main script
    midiout = None
    # Duration for each arpeggiated note (seconds)
    arpeg_duration = 0.1
    # history of mean absolute energy (scalar) over time
    energy_mag_hist = np.zeros(PLOT_LEN)
    # Queue and thread for non-blocking MIDI events
    midi_queue = queue.Queue()
    midi_thread = None
    
    @staticmethod
    def map_to_velocity(val: float,
                        in_min: float = 10.0,
                        in_max: float = 100.0,
                        out_min: int = 1,
                        out_max: int = 127) -> int:
        """Map a float from [in_min, in_max] to an integer in [out_min, out_max] for MIDI velocity."""
        # normalize into [0,1]
        if in_max - in_min == 0:
            ratio = 0.0
        else:
            ratio = (val - in_min) / (in_max - in_min)
        # clamp
        ratio = max(0.0, min(1.0, ratio))
        # scale and return
        vel = int(round(out_min + ratio * (out_max - out_min)))
        print(f"[VELOCITY] {vel}")
        return vel

    @classmethod
    def start_midi_thread(cls):
        """Start background thread to process MIDI queue."""
        if cls.midi_thread is None and cls.midiout:
            def worker():
                while True:
                    delay, msg = cls.midi_queue.get()
                    if delay > 0:
                        time.sleep(delay)
                    cls.midiout.send_message(msg)
            cls.midi_thread = threading.Thread(target=worker, daemon=True)
            cls.midi_thread.start()

    @classmethod
    def handle_top_acc(cls, address, *args):
        print(f"[OSC] {address}: {args}")
        if len(args) >= 3:
            x, y, z = args[:3]
            with cls.acc_lock:
                cls.acc_data_top[:] = np.roll(cls.acc_data_top, -1, axis=0)
                cls.acc_data_top[-1] = [x, y, z]
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
                # compute energy of top buffer for magnitude
                en = np.sqrt(np.square(x) + np.square(y) + np.square(z)) - 9.7005
                print(f"[DEBUG] Energy mag: {en:.3f}")
                # update mean-abs-energy history
                cls.energy_mag_hist[:] = np.roll(cls.energy_mag_hist, -1)
                cls.energy_mag_hist[-1] = en
                # arpeggiate if threshold exceeded
                if cls.midiout and en > 10:
                    # select next note in current chord
                    chord = cls.chords[cls.chord_idx]
                    note = chord[cls.note_idx]
                    vel = cls.map_to_velocity(en)
                    print(f"[MIDI] Arpeggiating chord {cls.chord_idx}, note {note}")
                    # enqueue note-on then note-off
                    cls.midi_queue.put((0, [0x90, note, vel]))
                    cls.midi_queue.put((cls.arpeg_duration, [0x80, note, 0]))
                    # advance note index; cycle chords when chord complete
                    cls.note_idx += 1
                    if cls.note_idx >= len(chord):
                        cls.note_idx = 0
                        cls.chord_idx = (cls.chord_idx + 1) % len(cls.chords)
                else:
                    # stop midi playing: send note-off for last chord and clear queue
                    if cls.midiout:
                        last_idx = (cls.chord_idx - 1) % len(cls.chords)
                        for n in cls.chords[last_idx]:
                            cls.midiout.send_message([0x80, n, 0])
                    # clear pending MIDI events
                    while not cls.midi_queue.empty():
                        cls.midi_queue.get()