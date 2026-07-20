#!/usr/bin/env python3
"""Print the material resource whose accepted background ratio matches an image."""
import argparse
import math
from pathlib import Path

try:
    from PIL import Image
except ImportError as error:
    raise SystemExit("Pillow is required. Install it with: python3 -m pip install Pillow") from error


EXACT_SIZES = {
    (1041, 225): "channel",
    (1041, 217): "categoryBanner",
    (1035, 390): "push",
}

RATIO_ROUTES = (
    ("channel", 1041 / 225, "4.63:1"),
    ("splash", 9 / 16, "9:16"),
)
RATIO_TOLERANCE = 0.01


parser = argparse.ArgumentParser()
parser.add_argument("--image", required=True)
args = parser.parse_args()

image_path = Path(args.image)
if not image_path.exists():
    raise SystemExit(f"Input image not found: {image_path}")

with Image.open(image_path) as image:
    size = image.size

width, height = size
ratio = width / height

for resource, expected_ratio, label in RATIO_ROUTES:
    if math.isclose(ratio, expected_ratio, rel_tol=RATIO_TOLERANCE):
        print(f"MATCH {resource} {width}x{height} ratio={label}")
        raise SystemExit(0)

resource = EXACT_SIZES.get(size)
if resource:
    print(f"MATCH {resource} {width}x{height} exact")
    raise SystemExit(0)

print(f"NO_MATCH {width}x{height}")
raise SystemExit(1)
