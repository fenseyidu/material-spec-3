#!/usr/bin/env python3
from pathlib import Path
import sys

try:
    import PIL
except ImportError:
    PIL = None

skill_dir = Path(__file__).resolve().parent.parent
fonts_dir = skill_dir.parent / "assets" / "fonts"
fonts = [
    ("Bundled Alimama ShuHeiTi", fonts_dir / "AlimamaShuHeiTi-Bold.ttf"),
    ("Bundled Alibaba PuHuiTi", fonts_dir / "Alibaba_PuHuiTi_2.0_55_Regular_55_Regular.ttf"),
]
checks = [("Python", sys.version.split()[0]), ("Pillow", getattr(PIL, "__version__", ""))]
checks.extend((name, str(font) if font.exists() else "") for name, font in fonts)
ok = True
for name, value in checks:
    print(f"{'OK' if value else 'MISSING'} {name}{': ' + value if value else ''}")
    ok = ok and bool(value)
if not ok:
    print("Install Pillow with: python3 -m pip install Pillow")
    raise SystemExit(1)
