from enum import Enum

class Note(Enum):
    C        = 0
    C_SHARP  = 1
    DB       = 1
    D        = 2
    D_SHARP  = 3
    EB       = 3
    E        = 4
    F        = 5
    F_SHARP  = 6
    GB       = 6
    G        = 7
    G_SHARP  = 8
    AB       = 8
    A        = 9
    A_SHARP  = 10
    BB       = 10
    B        = 11

class Scale(Enum):
    MAJOR       = [Note.C, Note.D,  Note.E,  Note.F,  Note.G,  Note.A,  Note.B]
    MINOR       = [Note.C, Note.D,  Note.EB, Note.F,  Note.G,  Note.AB, Note.BB]
    BLUES       = [Note.C, Note.EB, Note.F,  Note.GB, Note.G,  Note.BB]
    PENTATONIC  = [Note.C, Note.D,  Note.E,  Note.G,  Note.A]

class Chord(Enum):
    MAJ       = [Note.C,  Note.E,  Note.G]
    MIN       = [Note.C,  Note.EB, Note.G]
    DIM       = [Note.C,  Note.EB, Note.GB]
    AUG       = [Note.C,  Note.E,  Note.AB]
    MAJ7TH    = [Note.B]
    DOM       = [Note.C]
    THIRD     = [Note.E]
    FIFTH     = [Note.G]
    BTHIRD    = [Note.EB]
    BFIFTH    = [Note.GB]
    SEVENTH   = [Note.A_SHARP]
    M7TH      = [Note.B]
    NINTH     = [Note.D]
    ELEVENTH  = [Note.F]
    THIRTEENTH= [Note.A]
    EIGHTH    = [Note.C]

    # overrides addition to concatenate note lists
    def __add__(self, other):
        if isinstance(other, Chord):
            self.value.extend(v for v in other.value if v not in self.value)
            return self
        return NotImplemented

harmonic_fields = {
    Scale.MAJOR: [Chord.MAJ, Chord.MIN, Chord.MIN, Chord.MAJ, Chord.MAJ, Chord.MIN, Chord.DIM],
    Scale.MINOR: [Chord.MIN, Chord.DIM, Chord.MAJ, Chord.MIN, Chord.MIN, Chord.MAJ, Chord.MAJ]
}

circle_of_fifths = [
    [Note.C, Note.G, Note.D, Note.A, Note.E, Note.B, Note.F_SHARP],
    [Note.C, Note.F, Note.BB, Note.EB, Note.AB, Note.DB, Note.GB]
]

def parse_chord_list(chord_list_str):
    """Parse a chord list string into a list of (root, chord_type, octave) tuples.
    
    Example input: "C maj,A min,F maj,G maj"
    Example output: [(Note.C, Chord.MAJ, 4), (Note.A, Chord.MIN, 4), (Note.F, Chord.MAJ, 4), (Note.G, Chord.MAJ, 4)]
    """
    chord_list = []
    for chord_str in chord_list_str.split(','):
        parts = chord_str.split(' ')
        if len(parts) != 2:
            raise ValueError(f"Invalid chord format: {chord_str}")
        root_str, chord_type_str = parts
        try:
            root = Note[root_str.upper().replace('#', '_SHARP')]
            chord_type = Chord[chord_type_str.upper()]
            chord_list.append((root, chord_type, 4))  # default octave 4
        except KeyError as e:
            raise ValueError(f"Invalid note or chord type: {e}")
    return chord_list