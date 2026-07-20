#!/usr/bin/env python3
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
FONTS_DIR = SKILL_DIR.parent / "assets" / "fonts"
REQUIRED_FONTS = [
    "Alibaba_PuHuiTi_2.0_55_Regular_55_Regular.ttf",
]


def ok(label, value):
    print(f"OK {label}: {value}")


def missing(label):
    print(f"MISSING {label}")


all_ok = True

ok("Python", sys.version.split()[0])

try:
    import PIL

    ok("Pillow", PIL.__version__)
except ImportError:
    all_ok = False
    missing("Pillow")

for font_name in REQUIRED_FONTS:
    font_path = FONTS_DIR / font_name
    if font_path.exists():
        ok("Bundled font", font_path)
    else:
        all_ok = False
        missing(f"Bundled font {font_name}")

if not all_ok:
    print("\nInstall missing items before rendering.")
    print("Pillow install:")
    print("python3 -m pip install Pillow")
    raise SystemExit(1)
