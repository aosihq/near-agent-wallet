"""verify_video.py - proves the frames actually contain readable text."""
import os
import subprocess
import tempfile

from PIL import Image

TIMES = [1.5, 6, 14, 22, 30, 34, 40, 46, 52]
ok = True

print(" t(s)   ink%   verdict   dominant colour")
print("-" * 52)
for t in TIMES:
    p = os.path.join(tempfile.gettempdir(), f"vf_{t}.png")
    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(t), "-i", "demo.mp4", "-frames:v", "1", p],
        capture_output=True,
    )
    im = Image.open(p).convert("RGB")
    small = im.resize((480, 270))
    px = list(small.getdata())
    ink = sum(1 for r, g, b in px if max(r, g, b) > 70) / len(px)

    # is there any red or green ink (the REFUSE / ALLOW lines)?
    red = sum(1 for r, g, b in px if r > 120 and g < 90 and b < 90)
    green = sum(1 for r, g, b in px if g > 120 and r < 110 and b < 110)
    tint = []
    if red > 15:
        tint.append(f"red={red}")
    if green > 15:
        tint.append(f"green={green}")

    verdict = "TEXT" if ink > 0.004 else "BLANK"
    if verdict == "BLANK":
        ok = False
    print(f"{t:5.1f}  {ink*100:5.2f}   {verdict:6}   {', '.join(tint) or '-'}")
    os.remove(p)

print()
print("RESULT:", "PASS - text present in every sampled frame" if ok else "FAIL - blank frame found")
raise SystemExit(0 if ok else 1)
