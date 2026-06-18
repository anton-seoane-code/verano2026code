"""Enjoy the Silence by Depeche Mode — pyo offline render."""

from pyo import *

s = Server(duplex=0, audio="offline").boot()
s.recordOptions(dur=65, filename="pyo/enjoy_the_silence.wav")

BPM = 112
BEAT = 60.0 / BPM
MIDI_OFFSET = 69


def mtof(m):
    return 440.0 * 2.0 ** ((m - MIDI_OFFSET) / 12.0)


master = Metro(time=BEAT / 4).play()
beat = [0]

BASS_DETUNE = 0.15

# ─── BASS ────────────────────────────────────────────────────────────────
bass_freq = SigTo(value=mtof(39), time=0.005, init=mtof(39))
bass_osc = SuperSaw(freq=bass_freq, detune=BASS_DETUNE, mul=0.5)
bass_adsr = Adsr(attack=0.005, decay=0.08, sustain=0.12, release=0.03, dur=BEAT * 1.5)
(ButLP(bass_osc * bass_adsr, freq=500) * 0.6).out()

# ─── PAD ─────────────────────────────────────────────────────────────────
pad_freqs = [SigTo(value=mtof(39), time=0.2) for _ in range(3)]
pad_oscs = [RCOsc(freq=f, mul=0.1) for f in pad_freqs]
pad_adsr = Adsr(attack=0.6, decay=0.4, sustain=0.5, release=1.8, dur=BEAT * 4.5)
Freeverb(pad_oscs[0] * pad_adsr * 0.45, size=0.82, damp=0.35).out()
Freeverb(pad_oscs[1] * pad_adsr * 0.45, size=0.82, damp=0.35).out()
Freeverb(pad_oscs[2] * pad_adsr * 0.45, size=0.82, damp=0.35).out()

# ─── LEAD ────────────────────────────────────────────────────────────────
lead_freq = SigTo(value=mtof(54), time=0.01, init=mtof(54))
lead_osc = RCOsc(freq=lead_freq, mul=0.25)
lead_adsr = Adsr(attack=0.015, decay=0.15, sustain=0.25, release=0.2, dur=BEAT)
lead_sig = lead_osc * lead_adsr
(lead_sig * 0.6).out()
Delay(lead_sig, delay=BEAT / 8, feedback=0.25, mul=0.5).out()

# ─── SUB KICK ────────────────────────────────────────────────────────────
kick_freq = SigTo(value=80, time=0.002, init=80)
kick_osc = Sine(freq=kick_freq, mul=1.0)
kick_adsr = Adsr(attack=0.001, decay=0.18, sustain=0, release=0.01, dur=0.5)
(ButLP(kick_osc * kick_adsr, freq=180) * 0.7).out()

# ─── SNARE ───────────────────────────────────────────────────────────────
snare_noise = Noise(mul=0.35)
snare_adsr = Adsr(attack=0.001, decay=0.07, sustain=0, release=0.01, dur=0.25)
(ButBP(snare_noise * snare_adsr, freq=190, q=0.6) * 0.55).out()

# ─── HIHAT ────────────────────────────────────────────────────────────────
hat_noise = Noise(mul=0.12)
hat_adsr = Adsr(attack=0.001, decay=0.025, sustain=0, release=0.005, dur=0.1)
(ButHP(hat_noise * hat_adsr, freq=7500) * 0.3).out()

# ─── PATTERNS ────────────────────────────────────────────────────────────

bass_pat = [
    (0, 39), (4, 39), (8, 34), (12, 38),
    (16, 37), (20, 39), (24, 39), (28, 34),
    (32, 38), (36, 37), (40, 39), (44, 39),
]

chord_pat = [
    (0, [39, 46, 51]),       # E♭m
    (16, [34, 41, 49]),      # B♭m
    (32, [38, 45, 50]),      # G♭
    (48, [37, 44, 51]),      # D♭
]

lead_pat = [
    (6, 54), (10, 53), (14, 51),
    (22, 49), (26, 51), (30, 53),
    (38, 54), (42, 56), (46, 54),
    (54, 53), (58, 51), (62, 49),
]


def seq():
    pos = beat[0] % 64

    for off, note in bass_pat:
        if pos == off:
            bass_freq.value = mtof(note)
            bass_adsr.play()

    for off, notes in chord_pat:
        if pos == off:
            for i, n in enumerate(notes):
                pad_freqs[i].value = mtof(n)
            pad_adsr.play()

    for off, note in lead_pat:
        if pos == off:
            lead_freq.value = mtof(note)
            lead_adsr.play()

    if pos % 4 == 0:
        kick_freq.value = 100
        kick_adsr.play()

    if pos % 8 == 4:
        snare_adsr.play()

    if pos % 2 == 0:
        hat_adsr.play()

    beat[0] += 1


trig = TrigFunc(master, seq)

# ─── RENDER ──────────────────────────────────────────────────────────────
print("Rendering...")
s.start()
s.shutdown()
print("Done — enjoy_the_silence.wav")
