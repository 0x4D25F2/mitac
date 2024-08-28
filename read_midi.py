import musicpy as mp


def read_midi(path: str):
    midi = mp.read(path, get_off_drums=True, clear_empty_notes=True, clear_other_channel_msg=True)
    melody, bpm = mp.concat(midi.tracks, "&"), midi.bpm
    
    print(1)
    l, t, n = [], [], []
    notes = melody.notes
    interval = melody.interval
    duration = melody.get_duration()
    
    for i in range(len(melody)):
        for j in range(len(t)):
            t[j][1] -= interval[i - 1]
        for j in range(len(t) - 1, -1, -1):
            if t[j][1] <= 0:
                t.pop(j)
        t.append([mp.get_freq(notes[i]), duration[i]])
        n = [[j[0] for j in t], min(interval[i], duration[i])]
        if interval[i]:
            l.append(n)
        if duration[i] < interval[i]:
            l.append([[0], interval[i] - duration[i]])
    return l, bpm
