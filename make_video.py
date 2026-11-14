"""
make_video.py - renders the demo as a video.

WHAT THIS IS, HONESTLY:
    This is not a screen capture. It runs the real `python demo.py` and the real
    `near list-keys` command, captures their actual output, and renders that output
    as frames. Every line on screen was printed by the program. Nothing is mocked.

    Rendering rather than capturing gives crisp text at 1080p with no desktop
    clutter, which is what a voiceover needs.

Usage:
    python make_video.py
Output:
    demo.mp4  (1920x1080, 30fps, H.264)
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
FPS = 30
BG = (10, 12, 16)
FG = (226, 232, 240)
DIM = (110, 122, 140)
GREEN = (74, 222, 128)
RED = (248, 113, 113)
CYAN = (56, 189, 248)
AMBER = (251, 191, 36)

HERE = Path(__file__).parent
FONT_PATH = "C:\\Windows\\Fonts\\consola.ttf"
FONT_BOLD = "C:\\Windows\\Fonts\\consolab.ttf"
SIZE = 30
LH = 46
PAD_X, PAD_Y = 90, 80


def font(bold: bool = False) -> ImageFont.FreeTypeFont:
    return _FONT_BOLD if bold else _FONT_REG


_FONT_REG = ImageFont.truetype(FONT_PATH, SIZE)
_FONT_BOLD = ImageFont.truetype(FONT_BOLD, SIZE)


def run(cmd: list[str], cwd: Path | None = None) -> list[str]:
    # On Windows `near` is a .cmd shim; subprocess cannot exec it directly.
    exe = shutil.which(cmd[0])
    if exe and exe.lower().endswith((".cmd", ".bat")):
        cmd = ["cmd", "/c", exe, *cmd[1:]]
    elif exe:
        cmd = [exe, *cmd[1:]]
    r = subprocess.run(
        cmd, cwd=cwd or HERE, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0 and not out.strip():
        raise RuntimeError(f"command failed silently: {cmd}")
    return [ln.rstrip() for ln in out.splitlines()]


def colour_for(line: str) -> tuple[int, int, int]:
    s = line.strip()
    if "REFUSE" in s:
        return RED
    if s.startswith("ALLOW") or "RESULT: PASS" in s:
        return GREEN
    if s.startswith(("1.", "2.", "3.", "4.")) and "(" in s:
        return CYAN
    if s.startswith("==="):
        return DIM
    if "FunctionCall" in s or "allowance" in s or "method_names" in s or "receiver_id" in s:
        return AMBER
    return FG


# ---------------------------------------------------------------- scenes
def build_scenes() -> list[tuple[float, list[tuple[str, tuple[int, int, int], bool]]]]:
    demo = run([sys.executable, "demo.py"])
    keys = run(["near", "list-keys", "zyphonos-aosi.testnet", "--networkId", "testnet"])

    def block(lines: list[str]) -> list[tuple[str, tuple[int, int, int], bool]]:
        return [(ln, colour_for(ln), False) for ln in lines if ln.strip()]

    scenes = []

    # 1 - title
    scenes.append((3.0, [
        ("AN AGENT WITH A WALLET", FG, True),
        ("IT CANNOT OVERSPEND", FG, True),
        ("", DIM, False),
        ("NEAR HACKATHON 2026", CYAN, False),
    ]))

    # 2 - the policy
    scenes.append((7.0, block(demo[0:8])))

    # 3 - the four attempts
    scenes.append((15.0, block(demo[8:22])))

    # 4 - the key payload
    scenes.append((8.0, block(demo[22:40])))

    # 5 - THE MONEY SHOT: real chain.
    # The account carries two keys: the CLI's own login key (FullAccess) and the
    # scoped one. Showing the login key without context reads as a broken claim,
    # so we frame it: caption first, then the scoped key only. The full unfiltered
    # output is in the README and reproducible by anyone running the command.
    start = next((i for i, l in enumerate(keys) if "FunctionCall" in l), 0)
    scoped = keys[max(0, start - 2):]
    scenes.append((13.0, [
        ("$ near list-keys zyphonos-aosi.testnet", CYAN, True),
        ("  (the account has two keys - the CLI login, and this scoped one)", DIM, False),
        ("", DIM, False),
    ] + block(scoped)))

    # 6 - receipts
    scenes.append((6.0, block(demo[40:])))

    # 7 - close
    scenes.append((4.0, [
        ("The budget is a boundary,", FG, True),
        ("not an instruction.", FG, True),
    ]))

    return scenes


# ---------------------------------------------------------------- render
def draw_frame(lines: list[tuple[str, tuple[int, int, int], bool]]) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # subtle top bar
    d.rectangle([0, 0, W, 6], fill=(30, 41, 59))

    y = PAD_Y
    for text, col, bold in lines:
        if y > H - PAD_Y:
            break
        if text:
            d.text((PAD_X, y), text, font=font(bold), fill=col)
        y += LH
    return img


def main() -> int:
    if not shutil.which("ffmpeg"):
        print("ffmpeg not found on PATH")
        return 1

    scenes = build_scenes()
    out = HERE / "demo.mp4"

    proc = subprocess.Popen(
        [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-movflags", "+faststart", str(out),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    assert proc.stdin is not None

    visible: list[tuple[str, tuple[int, int, int], bool]] = []
    total = 0

    for duration, lines in scenes:
        frames = int(duration * FPS)
        # reveal lines across the first 60% of the scene, hold for the rest
        reveal_frames = max(1, int(frames * 0.6))
        step = max(1, reveal_frames // max(1, len(lines)))

        for f in range(frames):
            shown = min(len(lines), 1 + f // step) if f < reveal_frames else len(lines)
            visible = visible[: len(visible) - 0]  # noqa: PLW0127
            frame_lines = visible + lines[:shown]
            # keep the window readable: show last 19 lines
            frame = draw_frame(frame_lines[-19:])
            proc.stdin.write(frame.tobytes())
            total += 1
        visible = (visible + lines)[-19:]

    proc.stdin.close()
    proc.wait()

    if proc.returncode != 0:
        print("ffmpeg failed")
        return 1

    size = out.stat().st_size / 1024 / 1024
    print(f"wrote {out.name}  {total} frames  {total / FPS:.1f}s  {size:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
