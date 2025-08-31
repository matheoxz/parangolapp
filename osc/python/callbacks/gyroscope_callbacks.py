import threading
import time
import numpy as np

class GyroscopeCallbacks:
    """
    Static handlers and buffers for gyroscope OSC signals.
    """
    PLOT_LEN = 200
    gyr_data = np.zeros((PLOT_LEN, 3))
    gyr_lock = threading.Lock()
    latest_acc_y = None
    latest_opt = 1
    x_accum = 0.0
    y_accum = 0.0
    z_accum = 0.0
    midiout = None

    # Musical mapping constants
    MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
    OCTAVES = 5
    NOTES_PER_OCTAVE = len(MAJOR_SCALE)
    BASE_MIDI_NOTE = 36  # C2

    @classmethod
    def handle_acc(cls, address, *args):
        """Capture acceleration y for velocity mapping."""
        if len(args) >= 2:
            cls.latest_acc_y = args[1]

    @classmethod
    def handle_opt(cls, address, *args):
        """Change operating mode for gyroscope MIDI output."""
        if args:
            cls.latest_opt = args[0]
            print(f"[OSC] {address}: set mode {cls.latest_opt}")

    @classmethod
    def handle_gyr(cls, address, *args):
        """OSC handler for gyroscope data."""
        print(f"[OSC] {address}: {args}")
        if len(args) >= 3:
            x, y, z = args[:3]
            # update plot buffer
            with cls.gyr_lock:
                cls.gyr_data[:] = np.roll(cls.gyr_data, -1, axis=0)
                cls.gyr_data[-1] = [x, y, z]
            # choose mode
            mode = cls.latest_opt or 1
            if cls.midiout is None:
                return
            if mode == 1:
                cls._gyr_to_midi(x, y, z)
            elif mode == 2:
                cls._gyr_to_midi(x, y, z)
                cls._gyr_to_cc(x, y, z)
            elif mode == 3:
                cls._gyr_to_cc(x, y, z, mode='roll')
            elif mode == 4:
                cls._gyr_to_cc(x, y, z, mode='pitch')
            elif mode == 5:
                cls._gyr_to_cc(x, y, z, mode='yaw')

    @classmethod
    def _gyr_to_midi(cls, x_deg, y_deg, z_deg):
        # map pitch to scale degree and roll to octave
        pitch_norm = (y_deg + 360) / 720
        scale_degree = int(pitch_norm * cls.NOTES_PER_OCTAVE) % cls.NOTES_PER_OCTAVE
        roll_norm = (x_deg + 360) / 720
        octave = int(roll_norm * cls.OCTAVES) % cls.OCTAVES
        note = cls.BASE_MIDI_NOTE + octave*12 + cls.MAJOR_SCALE[scale_degree]
        # velocity from latest_acc_y
        vel = int(max(0, min(127, (((cls.latest_acc_y or 0) + 20)/40)*127)))
        # send note on/off
        cls.midiout.send_message([0x91, note, vel])
        time.sleep(0.125)
        cls.midiout.send_message([0x81, note, 0])
        print(f"[MIDI] note={note}, vel={vel}, roll={x_deg:.1f}, pitch={y_deg:.1f}")

    @classmethod
    def _gyr_to_cc(cls, x_deg, y_deg, z_deg, mode='all'):
        # accumulate degrees
        cls.x_accum += x_deg
        cls.y_accum += y_deg
        cls.z_accum += z_deg
        def map_cc(val):
            if abs(val) > 3600:
                val %= 3600
            return int(max(0, min(127, (val/3600)*127)))
        cc_x = map_cc(cls.x_accum)
        cc_y = map_cc(cls.y_accum)
        cc_z = map_cc(cls.z_accum)
        if mode == 'all':
            cls.midiout.send_message([0xB0, 11, cc_x])
            cls.midiout.send_message([0xB0, 12, cc_y])
            cls.midiout.send_message([0xB0, 13, cc_z])
        elif mode == 'roll':
            cls.midiout.send_message([0xB0, 11, cc_x])
        elif mode == 'pitch':
            cls.midiout.send_message([0xB1, 12, cc_y])
        elif mode == 'yaw':
            cls.midiout.send_message([0xB2, 13, cc_z])
