from enum import Enum
import random
import music_data.music_structures as msc
from midi_utils.midi_utils import MIDIUtils

class ArpeggiatorMode(Enum):
    UP = lambda chord: chord
    DOWN = lambda chord: chord[::-1]
    UP_DOWN = lambda chord: chord + (chord[::-1][1:-1])
    DOWN_UP = lambda chord: chord[::-1] + chord[1:-1]
    RANDOM = lambda chord: random.sample(chord, len(chord))
    THIRD_OCTAVE = lambda chord: [chord[0], chord[2], chord[1] + 12] * 3

class ArpeggiatorUtils:
    """Utility functions for arpeggiator."""

    @staticmethod
    def create_arpeggio(chords: list[(msc.Note, list[msc.Note], int)], pattern: lambda x: x) -> list[int]:
        """Create an arpeggio from a list of chords and a pattern."""
        arpeggio = []
        for chord in chords:
            midi_chord = MIDIUtils.midi_chord(chord[0], chord[1], chord[2])
            indices = pattern(midi_chord)
            arpeggio.append(indices)
        return arpeggio
