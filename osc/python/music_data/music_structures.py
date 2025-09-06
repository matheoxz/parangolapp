scales = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'blues': [0, 3, 5, 6, 7, 10],
    'pentatonic': [0, 2, 4, 7, 9],
}

note_names = {
    'C': 0,
    'C#': 1,
    'Db': 1,
    'D': 2,
    'D#': 3,
    'Eb': 3,
    'E': 4,
    'F': 5,
    'F#': 6,
    'Gb': 6,
    'G': 7,
    'G#': 8,
    'Ab': 8,
    'A': 9,
    'A#': 10,
    'Bb': 10,
    'B': 11,
}

midi_notes = {
    'C': 12,
    'C#': 13,
    'Db': 13,
    'D': 14,
    'D#': 15,
    'Eb': 15,
    'E': 16,
    'F': 17,
    'F#': 18,
    'Gb': 18,
    'G': 19,
    'G#': 20,
    'Ab': 20,
    'A': 21,
    'A#': 22,
    'Bb': 22,
    'B': 23,
}

chords = {
    'maj': [0, 4, 7],
    'min': [0, 3, 7],
    'dim': [0, 3, 6],
    'aug': [0, 4, 8],
    'maj7th': [11],
    'dom': [0],
    '3th': [4],
    '5th': [7],
    'b3th': [3],
    'b5th': [6],
    '7th': [10],
    'm7th': [11],
    '9th': [2],
    '11th': [5],
    '13th': [9],
    '8th': [12]
}

harmonic_fields = {
    'maj': [chords[mode] for mode in ['maj', 'min', 'min', 'maj', 'maj', 'min', 'dim']],
    'min': [chords[mode] for mode in ['min', 'dim', 'maj', 'min', 'min', 'maj', 'maj']]
}

circle_of_fifths = [
    ['C', 'G', 'D', 'A', 'E', 'B', 'F#'],
    ['C', 'F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb']
]

def midi_scale(note: str, scale: str, octave: int):
    scale_notes = scales[scale]
    root = midi_notes[note] * octave - note_names[note] * (octave - 1)
    return [note + root for note in scale_notes]

def midi_scales(note: str, scale: str, octaves: list[int]):
    return [midi_scale(note, scale, octave) for octave in octaves]

def midi_chord(root: str, mode: set[str], octave: int):
    chord_notes = set().union(*(chords[m] for m in mode))
    root_note = midi_notes[root] * octave - note_names[root] * (octave - 1)
    return [note + root_note for note in chord_notes]

def midi_chords(chords: list[tuple[str, set[str]]], octaves: list[int]):
    return [midi_chord(c[0], c[1], o) for o in octaves for c in chords]

def midi_chord_octave_third(root: str, mode: str, octave: int, reps: int = 4):
    if mode not in ['maj', 'min']:
        raise ValueError("mode must be 'maj' or 'min'")
    
    chord = midi_chord(root, [mode], octave)
    return [chord[0], chord[2], chord[1] + 12] * reps