#!/usr/bin/env python3
import argparse
from pathlib import Path

from PIL import Image, ImageEnhance

TEMPLATE_SIZES = {
    "channel": (1041, 225),
    "categoryBanner": (1041, 217),
}
DEFAULT_TEMPLATE = "channel"
DEFAULT_TITLE_TARGET = 0.53
TEMPLATE_TITLE_TARGETS = {
    "channel": DEFAULT_TITLE_TARGET,
    "categoryBanner": 0.51,
}
COPYSAFE_X_RANGE = (0.03, 0.52)
COPYSAFE_Y_RANGE = (0.20, 0.82)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Prepare buffered-horizontal material input with an optimized crop."
    )
    parser.add_argument("--input", required=True, help="Generated buffered-horizontal candidate image.")
    parser.add_argument("--out", required=True, help="Prepared output image path.")
    parser.add_argument(
        "--template",
        choices=sorted(TEMPLATE_SIZES),
        default=DEFAULT_TEMPLATE,
        help="Target template size. Default: channel.",
    )
    parser.add_argument(
        "--target-width",
        type=int,
        help="Override target crop width. Must be used with --target-height.",
    )
    parser.add_argument(
        "--target-height",
        type=int,
        help="Override target crop height. Must be used with --target-width.",
    )
    parser.add_argument(
        "--title-bbox",
        help=(
            "Optional complete title/subtitle bbox from visual QA or OCR, "
            "formatted as x1,y1,x2,y2 in source-image pixels."
        ),
    )
    parser.add_argument(
        "--title-target",
        type=float,
        default=None,
        help=(
            "Target vertical position for the title group inside the final crop, 0-1. "
            "Defaults: channel=0.53, categoryBanner=0.51."
        ),
    )
    parser.add_argument(
        "--step",
        type=int,
        default=2,
        help="Candidate cropTop scan step in pixels. Default: 2.",
    )
    return parser.parse_args()


def target_size(args):
    has_width = args.target_width is not None
    has_height = args.target_height is not None
    if has_width != has_height:
        raise SystemExit("--target-width and --target-height must be provided together")
    if has_width:
        if args.target_width <= 0 or args.target_height <= 0:
            raise SystemExit("--target-width and --target-height must be positive")
        return args.target_width, args.target_height
    return TEMPLATE_SIZES[args.template]


def title_target(args):
    if args.title_target is not None:
        return args.title_target
    return TEMPLATE_TITLE_TARGETS[args.template]


def luma(pixel):
    red, green, blue = pixel[:3]
    return (red * 299 + green * 587 + blue * 114) / 1000


def is_near_white(pixel):
    red, green, blue = pixel[:3]
    return red >= 246 and green >= 246 and blue >= 246


def is_subject_pixel(pixel):
    value = luma(pixel)
    red, green, blue = pixel[:3]
    spread = max(red, green, blue) - min(red, green, blue)
    return (value < 178 and spread > 24) or (value < 232 and spread > 72)


def first_content_y(image):
    width, height = image.size
    pixels = image.load()
    sample_step = max(1, width // 900)
    min_hits = max(8, int((width / sample_step) * 0.012))

    for y in range(height):
        hits = 0
        for x in range(0, width, sample_step):
            if not is_near_white(pixels[x, y]):
                hits += 1
        if hits >= min_hits:
            return y
    return 0


def merge_runs(rows, max_gap):
    if not rows:
        return []
    runs = []
    start = previous = rows[0]
    for row in rows[1:]:
        if row - previous <= max_gap:
            previous = row
            continue
        runs.append((start, previous))
        start = previous = row
    runs.append((start, previous))
    return runs


def title_search_box(image, content_y):
    width, height = image.size
    content_y = clamp(content_y, 0, height - 1)
    content_height = max(1, height - content_y)
    left = int(width * COPYSAFE_X_RANGE[0])
    right = int(width * COPYSAFE_X_RANGE[1])
    top = int(content_y + content_height * COPYSAFE_Y_RANGE[0])
    bottom = int(content_y + content_height * COPYSAFE_Y_RANGE[1])
    return left, top, right, max(top + 1, bottom)


def parse_title_bbox(value, image_size):
    if not value:
        return None
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise SystemExit("--title-bbox must be formatted as x1,y1,x2,y2")

    try:
        left, top, right, bottom = [int(round(float(part))) for part in parts]
    except ValueError as error:
        raise SystemExit("--title-bbox values must be numbers") from error

    width, height = image_size
    left = clamp(left, 0, width - 1)
    right = clamp(right, left + 1, width)
    top = clamp(top, 0, height - 1)
    bottom = clamp(bottom, top + 1, height)
    return (left, top, right, bottom)


def title_bbox(image, content_y, crop_height, provided_bbox=None):
    if provided_bbox:
        return {"bbox": provided_bbox, "source": "provided"}

    detected = title_bbox_from_edges(image, content_y, crop_height)
    if detected:
        return {"bbox": detected, "source": "edge"}
    return None


def title_bbox_from_edges(image, content_y, crop_height):
    width, height = image.size
    pixels = image.load()
    left, top, right, bottom = title_search_box(image, content_y)
    sample_step = max(2, width // 1200)
    row_scores = []
    row_pixels = {}

    for y in range(max(1, top), min(height - 1, bottom)):
        xs = []
        for x in range(max(sample_step, left), min(width - sample_step, right), sample_step):
            if is_text_edge_pixel(pixels, x, y, sample_step):
                xs.append(x)
        row_scores.append((y, len(xs)))
        if xs:
            row_pixels[y] = xs

    max_score = max((score for _, score in row_scores), default=0)
    if max_score < max(10, int((right - left) / sample_step * 0.04)):
        return None

    threshold = max(8, int(max_score * 0.22))
    rows = [y for y, score in row_scores if score >= threshold]
    runs = merge_runs(rows, max(6, round(crop_height * 0.035)))

    weighted = []
    for top, bottom in runs:
        score = sum(score for y, score in row_scores if top <= y <= bottom)
        run_height = bottom - top + 1
        if run_height >= 5 and score >= max_score * 1.4:
            xs = []
            for y in range(top, bottom + 1):
                xs.extend(row_pixels.get(y, []))
            if xs:
                weighted.append(
                    {
                        "top": top,
                        "bottom": bottom,
                        "score": score,
                        "left": min(xs),
                        "right": max(xs) + sample_step,
                    }
                )
    if not weighted:
        return None

    anchor = max(weighted, key=lambda item: item["score"])
    selected = [anchor]
    max_join_gap = max(28, round(crop_height * 0.16))
    changed = True
    while changed:
        changed = False
        selected_top = min(item["top"] for item in selected)
        selected_bottom = max(item["bottom"] for item in selected)
        for item in weighted:
            if item in selected:
                continue
            gap = max(item["top"] - selected_bottom, selected_top - item["bottom"], 0)
            if gap <= max_join_gap:
                selected.append(item)
                changed = True

    top = min(item["top"] for item in selected)
    bottom = max(item["bottom"] for item in selected)
    left = min(item["left"] for item in selected)
    right = max(item["right"] for item in selected)
    bbox = (left, top, right, bottom + 1)
    if is_suspicious_title_bbox(bbox, image.size, crop_height):
        return None
    return bbox


def is_text_edge_pixel(pixels, x, y, step):
    center = luma(pixels[x, y])
    edge = max(
        abs(center - luma(pixels[x - step, y])),
        abs(center - luma(pixels[x + step, y])),
        abs(center - luma(pixels[x, y - 1])),
        abs(center - luma(pixels[x, y + 1])),
    )
    return edge >= 22 and center < 245


def is_suspicious_title_bbox(bbox, image_size, crop_height):
    width, _ = image_size
    left, top, right, bottom = bbox
    bbox_width = right - left
    bbox_height = bottom - top
    if bbox_height > crop_height * 0.62:
        return True
    if bbox_height < max(10, crop_height * 0.045):
        return True
    if bbox_width > width * 0.58:
        return True
    if bbox_width < width * 0.08:
        return True
    return False


def subject_row_counts(image):
    width, height = image.size
    pixels = image.load()
    left = int(width * 0.36)
    right = width
    sample_step = max(2, width // 800)
    rows = [0] * height

    for y in range(height):
        count = 0
        for x in range(left, right, sample_step):
            if is_subject_pixel(pixels[x, y]):
                count += 1
        rows[y] = count
    total = sum(rows)
    return rows, total


def prefix_sums(values):
    sums = [0]
    current = 0
    for value in values:
        current += value
        sums.append(current)
    return sums


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def crop_geometry(width, height, target_ratio):
    image_ratio = width / height
    if image_ratio >= target_ratio:
        crop_height = height
        crop_width = round(height * target_ratio)
        crop_left = round((width - crop_width) / 2)
    else:
        crop_width = width
        crop_height = round(width / target_ratio)
        crop_left = 0
    crop_height = min(crop_height, height)
    crop_width = min(crop_width, width)
    return crop_left, crop_width, crop_height


def score_crop(top, crop_height, image_height, content_y, bbox, target, subject_prefix, subject_total):
    bottom = top + crop_height
    score = 0.0
    reasons = []

    if bbox:
        title_top, title_bottom = bbox[1], bbox[3]
        title_center = (title_top + title_bottom) / 2
        target_y = top + crop_height * target
        title_offset = abs(title_center - target_y) / crop_height
        score += title_offset * 900
        reasons.append(f"titleOffset={title_offset:.3f}")

        margin = max(8, round(crop_height * 0.035))
        if title_top < top + margin:
            score += 3000 + (top + margin - title_top) * 8
            reasons.append("titleTopClipped")
        if title_bottom > bottom - margin:
            score += 3000 + (title_bottom - (bottom - margin)) * 8
            reasons.append("titleBottomClipped")
    else:
        score += 180
        reasons.append("noTitleBBox")

    if top < content_y:
        white_px = content_y - top
        score += (white_px / crop_height) * 2000
        reasons.append(f"whiteTop={white_px}")

    if subject_total:
        above = subject_prefix[max(0, top)]
        below = subject_prefix[image_height] - subject_prefix[min(image_height, bottom)]
        outside = (above + below) / subject_total
        score += outside * 80
        reasons.append(f"subjectOutside={outside:.3f}")
        if above / subject_total > 0.025:
            score += (above / subject_total) * 120
            reasons.append("subjectTopRisk")
        if below / subject_total > 0.08:
            score += (below / subject_total) * 60
            reasons.append("subjectBottomRisk")

    # Prefer crops that stay near the real generated material, while allowing
    # title and subject constraints to override the guide boundary when needed.
    if top < content_y:
        score += ((content_y - top) / crop_height) * 90
    else:
        score += ((top - content_y) / crop_height) * 30

    if bottom > image_height:
        score += 10000
        reasons.append("outOfBounds")

    return score, ", ".join(reasons)


def choose_crop_top(image, bbox, target, step, target_ratio):
    width, height = image.size
    content_y = first_content_y(image)
    expected_y = round(height * 0.49)
    _, _, crop_height = crop_geometry(width, height, target_ratio)
    max_top = max(0, height - crop_height)
    subject_rows, subject_total = subject_row_counts(image)
    subject_prefix = prefix_sums(subject_rows)

    anchors = {max_top, content_y, expected_y, round((height - crop_height) / 2)}
    if bbox:
        title_center = (bbox[1] + bbox[3]) / 2
        anchors.add(round(title_center - crop_height * target))

    candidates = set()
    scan_step = max(1, step)
    for top in range(0, max_top + 1, scan_step):
        candidates.add(top)
    for anchor in anchors:
        anchor = clamp(anchor, 0, max_top)
        radius = max(12, round(crop_height * 0.08))
        for top in range(max(0, anchor - radius), min(max_top, anchor + radius) + 1, scan_step):
            candidates.add(top)

    best = None
    for top in candidates:
        score, reasons = score_crop(
            top, crop_height, height, content_y, bbox, target, subject_prefix, subject_total
        )
        if best is None or score < best["score"]:
            best = {"top": top, "score": score, "reasons": reasons}

    boundary_delta = content_y - expected_y
    return {
        "cropTop": best["top"],
        "cropHeight": crop_height,
        "contentY": content_y,
        "expectedY": expected_y,
        "boundaryDelta": boundary_delta,
        "score": best["score"],
        "reasons": best["reasons"],
    }


def main():
    args = parse_args()
    target = title_target(args)
    if not 0.3 <= target <= 0.7:
        raise SystemExit("--title-target must be between 0.3 and 0.7")
    width_target, height_target = target_size(args)
    target_ratio = width_target / height_target

    source_path = Path(args.input)
    source = Image.open(source_path)
    image = ImageOpsSafe.exif_transpose(source).convert("RGB")
    image = ImageEnhance.Color(image).enhance(1.02)
    width, height = image.size
    crop_left, crop_width, crop_height = crop_geometry(width, height, target_ratio)
    content_y = first_content_y(image)
    provided_bbox = parse_title_bbox(args.title_bbox, image.size)
    title = title_bbox(image, content_y, crop_height, provided_bbox)
    bbox = title["bbox"] if title else None
    decision = choose_crop_top(image, bbox, target, args.step, target_ratio)
    crop_top = decision["cropTop"]
    crop_box = (crop_left, crop_top, crop_left + crop_width, crop_top + crop_height)

    output = source.crop(crop_box)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output.save(out_path)

    print(f"Prepared {source_path.name} -> {out_path}")
    print(f"Template {args.template} target={width_target}x{height_target} ratio={target_ratio:.3f}")
    print(f"Source {width}x{height}")
    print(f"Crop {crop_box[0]},{crop_box[1]},{crop_box[2]},{crop_box[3]}")
    print(f"Crop size {output.width}x{output.height} ratio={output.width / output.height:.3f}")
    print(
        "Boundary "
        f"actualContentY={decision['contentY']} "
        f"guideY49={decision['expectedY']} "
        f"delta={decision['boundaryDelta']}"
    )
    if bbox:
        title_center = (bbox[1] + bbox[3]) / 2
        final_center = (title_center - crop_top) / crop_height
        print(
            "Title "
            f"bbox={bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]} "
            f"source={title['source']} "
            f"finalCenterPct={final_center:.3f} "
            f"target={target:.3f}"
        )
    else:
        print("WARN title bbox rejected or not detected; crop used content and subject constraints.")
    print(f"Score {decision['score']:.2f} ({decision['reasons']})")
    if abs(decision["boundaryDelta"]) > height * 0.08:
        print("WARN generated boundary differs from guide y=49%; optimized crop used visual constraints.")


class ImageOpsSafe:
    @staticmethod
    def exif_transpose(image):
        try:
            from PIL import ImageOps

            return ImageOps.exif_transpose(image)
        except Exception:
            return image


if __name__ == "__main__":
    main()
