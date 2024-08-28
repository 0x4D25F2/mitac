from adofai import ADOFAI
from read_midi import read_midi
from tqdm import tqdm

DT = 0.1

def merge_freq(hl, length):
    l = [0]
    for i in range(1, int(length // min(hl) + 1)):
        for j in hl:
            if j * i <= length:
                l.append(j * i)
    l.sort()
    for i in range(len(l) - 1):
        l[i] = l[i + 1] - l[i]
    return l[:-1]

def add_note(chart, hz, length, bpm, twist=False, change_bpm=-1, midspin=False):
    multi = len(hz) != 1 if isinstance(hz, list) else False
    if multi:
        cbpm = chart.get_metadata("bpm") if change_bpm < 0 else change_bpm
        fx = lambda x: cbpm / (60 * x) * 180
        iter = merge_freq(list(map(fx, hz)), int(length * 4 * (60 / bpm) / (60 / cbpm) * 180))
    else:
        hz = hz[0] if isinstance(hz, list) else hz
        cbpm = chart.get_metadata("bpm")
        rep = int(hz * length * 4 * (60 / bpm))
        iter = range(rep)
    if hz == 0:
        e = chart.get_event(-1, "SetSpeed")
        if e:
            cbpm = e["beatsPerMinute"]
        chart.add_pause(-1, length * 4 * (60 / bpm) / (60 / cbpm))
        chart.add_angle_data(chart.get_last_angle(), midspin)
        return
    is_twist = False
    if change_bpm != -1:
        chart.set_speed_bpm(-1, change_bpm, True)
        cbpm = change_bpm
    for i in iter:
        if multi:
            delta = 180 - i
            if i < DT:
                delta = 180 - DT
        else:
            delta = 180 - cbpm / (60 * hz) * 180
        if midspin:
            delta = - (180 - delta)
        if is_twist and twist:
            delta = -delta
        chart.add_angle_data(chart.get_last_angle() + delta, midspin)
        if twist:
            chart.add_twirl(-1)
            is_twist = not is_twist
    if is_twist:
        chart.add_twirl(-1, True)
    if change_bpm != -1:
        chart.set_speed_bpm(-1, chart.get_metadata("bpm"))


if __name__ == "__main__":
    print("MITAC - MIDI to ADOFAI Converter")
    path = input("请输入MIDI文件路径 >")
    path_output = input("请输入谱面文件保存路径 >")
    chart_bpm = float(input("请输入谱面的初始BPM >"))
    is_twist = input("是否为每个砖块加上旋转(Y/n)？ >") not in ["N", "n"]
    is_midspin = input("是否使用中旋(y/N)？ >") in ["Y", "y"]
    print()
    print("正在读取MIDI文件...")
    notes, bpm = read_midi(path)
    print("正在生成谱面...")
    chart = ADOFAI()
    chart.set_metadata("bpm", chart_bpm)
    for i in tqdm(range(len(notes))):
        add_note(chart, notes[i][0], notes[i][1], bpm, is_twist, -1, is_midspin)
    chart.save("output.adofai")
    
