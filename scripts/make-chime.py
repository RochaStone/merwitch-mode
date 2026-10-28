#!/usr/bin/env python3
"""Generates the two sounds from plain sine waves. No recorded or copyrighted audio.

  python3 scripts/make-chime.py        writes sounds/chime.wav (done) and sounds/bell.wav (notify)

chime: two soft bell notes rising a fifth (E6 then B6), the way a singing bowl answers.
bell:  one quieter, lower bell note (A5) for "Claude needs you".
Each note is a few inharmonic partials with a gentle attack and a long decay. 22050 Hz, 16-bit mono.
"""
import math
import os
import struct
import wave

RATE = 22050
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTIALS = ((1.0, 1.0), (2.76, 0.35), (5.40, 0.12))   # bell-like ratios and loudness


def note(freq, start, length, gain):
    out = []
    for i in range(int(length * RATE)):
        t = i / RATE
        env = min(1.0, t / 0.012) * math.exp(-t * 4.2)
        out.append(sum(a * math.sin(2 * math.pi * freq * r * t) for r, a in PARTIALS) * env * gain)
    return int(start * RATE), out


def mix(total, notes):
    buf = [0.0] * int(total * RATE)
    for offset, samples in notes:
        for i, s in enumerate(samples):
            if offset + i < len(buf):
                buf[offset + i] += s
    tail = int(0.08 * RATE)   # fade the last moment so there is no click
    for i in range(tail):
        buf[-1 - i] *= i / tail
    return buf


def write(path, buf):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", max(-32767, min(32767, int(s * 32767)))) for s in buf))


def main():
    os.makedirs(os.path.join(ROOT, "sounds"), exist_ok=True)
    write(os.path.join(ROOT, "sounds", "chime.wav"),
          mix(1.3, [note(1318.5, 0.0, 1.1, 0.28), note(1975.5, 0.16, 1.1, 0.22)]))
    write(os.path.join(ROOT, "sounds", "bell.wav"), mix(0.9, [note(880.0, 0.0, 0.85, 0.2)]))
    print("sounds/chime.wav and sounds/bell.wav written")


if __name__ == "__main__":
    main()
