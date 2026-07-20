#!/usr/bin/env python3
"""Crop a buffered horizontal candidate into a safe renderer input."""
import argparse
from pathlib import Path

from PIL import Image, ImageOps


TEMPLATES = {
    "channel": (1041, 225),
    "categoryBanner": (1041, 217),
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--template", choices=TEMPLATES, default="channel")
    parser.add_argument("--step", type=int, default=2)
    return parser.parse_args()


def luma(pixel):
    red, green, blue = pixel[:3]
    return (red * 299 + green * 587 + blue * 114) / 1000


def near_white(pixel):
    red, green, blue = pixel[:3]
    return red >= 246 and green >= 246 and blue >= 246


def first_content_y(image):
    pixels = image.load()
    step = max(1, image.width // 900)
    threshold = max(8, int((image.width / step) * 0.012))
    for y in range(image.height):
        if sum(not near_white(pixels[x, y]) for x in range(0, image.width, step)) >= threshold:
            return y
    return 0


def channel_boundary_y(image):
    """Find the first sustained, full-width transition out of the blank buffer."""
    pixels = image.load()
    step = max(1, image.width // 900)
    samples = len(range(0, image.width, step))
    minimum_coverage = 0.55
    lookahead = max(4, image.height // 180)
    coverage = [
        sum(not near_white(pixels[x, y]) for x in range(0, image.width, step)) / samples
        for y in range(image.height)
    ]
    for y in range(0, image.height - lookahead + 1):
        if all(value >= minimum_coverage for value in coverage[y : y + lookahead]):
            return y
    return None


def is_subject(pixel):
    red, green, blue = pixel[:3]
    value = luma(pixel)
    chroma = max(red, green, blue) - min(red, green, blue)
    return (value < 178 and chroma > 24) or (value < 232 and chroma > 72)


def subject_bounds(image):
    pixels = image.load()
    left, step = int(image.width * 0.36), max(2, image.width // 800)
    samples = len(range(left, image.width, step))
    active_threshold = max(2, int(samples * 0.045))
    active_rows = []
    for y in range(image.height):
        count = sum(is_subject(pixels[x, y]) for x in range(left, image.width, step))
        if count >= active_threshold:
            active_rows.append(y)
    if not active_rows:
        return None
    return active_rows[0], active_rows[-1] + 1


def crop_geometry(width, height, target_width, target_height):
    target_ratio = target_width / target_height
    if width / height >= target_ratio:
        crop_height = height
        crop_width = round(height * target_ratio)
        left = round((width - crop_width) / 2)
    else:
        crop_width = width
        crop_height = round(width / target_ratio)
        left = 0
    return left, min(crop_width, width), min(crop_height, height)


def choose_top(image, crop_height, content_y, step):
    minimum_top = min(max(content_y, 0), image.height - crop_height)
    maximum_top = image.height - crop_height
    bounds = subject_bounds(image)
    if not bounds:
        return minimum_top, None
    subject_top, subject_bottom = bounds
    subject_center = (subject_top + subject_bottom) / 2
    target_top = round(subject_center - crop_height / 2)
    top = max(minimum_top, min(target_top, maximum_top))
    return top, subject_center


def main():
    args = parse_args()
    source = Path(args.input)
    target = Path(args.out)
    if not source.exists():
        raise SystemExit(f"Input image not found: {source}")
    width, height = TEMPLATES[args.template]
    image = ImageOps.exif_transpose(Image.open(source)).convert("RGBA")
    left, crop_width, crop_height = crop_geometry(image.width, image.height, width, height)
    content_y = first_content_y(image)
    if args.template == "channel":
        boundary_y = channel_boundary_y(image)
        bounds = subject_bounds(image)
        if boundary_y is None:
            raise SystemExit("Channel requires a sustained full-width blank/content boundary.")
        if bounds and bounds[0] < boundary_y:
            raise SystemExit("Channel main visual protrudes above the horizontal blank/content boundary.")
        content_y = boundary_y
    top, subject_center = choose_top(image, crop_height, content_y, args.step)
    output = image.crop((left, top, left + crop_width, top + crop_height))
    output = output.resize((width, height), Image.Resampling.LANCZOS)
    target.parent.mkdir(parents=True, exist_ok=True)
    output.save(target)
    print(
        f"Prepared {args.template} {width}x{height} content_y={content_y} "
        f"subject_center={subject_center} crop={left},{top},{crop_width},{crop_height}"
    )


if __name__ == "__main__":
    main()
