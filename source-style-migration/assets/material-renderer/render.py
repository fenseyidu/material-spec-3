#!/usr/bin/env python3
import json
import math
import os
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError as error:
    raise SystemExit(
        "Pillow is required for material rendering. Install it with: python3 -m pip install Pillow"
    ) from error


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent.parent
PACKAGE_ROOT = SKILL_DIR.parent
DEFAULT_TEMPLATE = "channel"
DEFAULT_COPY = {"title": "", "subtitle": "", "cta": "点击查看"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

FONTS_DIR = PACKAGE_ROOT / "assets" / "fonts"
BUTTON_FONT = FONTS_DIR / "Alibaba_PuHuiTi_2.0_55_Regular_55_Regular.ttf"
# CTA labels are rendered large; keep configured palette colors when they meet
# the WCAG large-text threshold instead of always falling back to harsh black.
MIN_BUTTON_TEXT_CONTRAST = 3.0
BUTTON_TEXT_FALLBACKS = ["#071A1D", "#0B1F24", "#111111", "#FFFFFF", "#F7FFFF"]

TEMPLATES = {
    "channel": {
        "label": "频道页中通",
        "outputName": "channel_1041x225",
        "width": 1041,
        "height": 225,
        "radius": 24,
    },
    "categoryBanner": {
        "label": "分类筛选 Banner",
        "outputName": "category_banner_1041x217",
        "width": 1041,
        "height": 217,
        "radius": 24,
    },
    "push": {
        "label": "消息页 Push",
        "outputName": "push_1035x390",
        "width": 1035,
        "height": 390,
        "radius": 24,
    },
    "feed": {
        "label": "feed",
        "outputName": "feed_503x645",
        "width": 503,
        "height": 645,
        "radius": 0,
        "button": {"x": 93, "y": 502, "width": 318, "height": 73, "radius": 36.5, "textSize": 32},
    },
    "popup": {
        "label": "弹窗",
        "outputName": "popup_885x990",
        "width": 885,
        "height": 990,
        "radius": 40,
        "button": {"x": 172, "y": 791, "width": 541, "height": 121, "radius": 65, "textSize": 56},
    },
    "splash": {
        "label": "开屏",
        "outputName": "splash_1125x1956",
        "width": 1125,
        "height": 1956,
        "radius": 0,
    },
    "miniProgramShare": {
        "label": "小程序分享图",
        "outputName": "mini_program_share_600x480",
        "width": 600,
        "height": 480,
        "radius": 0,
    },
}


def parse_args(argv):
    args = {}
    for item in argv:
        if not item.startswith("--"):
            continue
        key_value = item[2:].split("=", 1)
        args[key_value[0]] = key_value[1] if len(key_value) == 2 else "true"
    return args


def safe_folder_name(value):
    value = str(value or "").strip()
    value = re.sub(r'[\\/:*?"<>|]+', "_", value)
    value = re.sub(r"\s+", "_", value)
    return value.strip("_")


def timestamp_label():
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]


def is_inside(child, parent):
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def project_dir():
    candidates = [
        os.environ.get("MATERIAL_SPEC_PROJECT_DIR"),
        os.environ.get("CODEX_WORKSPACE_ROOT"),
        os.environ.get("CODEX_WORKSPACE"),
        os.environ.get("INIT_CWD"),
        os.environ.get("PWD"),
        os.getcwd(),
    ]
    for candidate in [Path(item).resolve() for item in candidates if item]:
        if candidate.exists() and not is_inside(candidate, PACKAGE_ROOT):
            return candidate
    return PACKAGE_ROOT.parent


def resolve_work_path(value, fallback_name):
    path = Path(value) if value and Path(value).is_absolute() else project_dir() / (value or fallback_name)
    if is_inside(path, PACKAGE_ROOT):
        return PACKAGE_ROOT.parent / path.resolve().relative_to(PACKAGE_ROOT)
    return path


def create_output_dir(args):
    root = resolve_work_path(args.get("output-dir"), "material-spec-output")
    root.mkdir(parents=True, exist_ok=True)

    requested = safe_folder_name(args.get("output-subdir") or args.get("batch") or "")
    base_name = requested or f"run_{timestamp_label()}"
    output_dir = root / base_name
    index = 2
    while output_dir.exists():
        output_dir = root / f"{base_name}_{index}"
        index += 1
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def read_material_config(input_dir):
    config_path = input_dir / "material.json"
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text(encoding="utf-8"))


def first_existing(candidates):
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return Path(candidate)
    return None


def image_for_template(input_dir, material_config, template_name, args):
    if args.get("image"):
        image_path = Path(args["image"]).resolve()
        if not image_path.exists():
            raise FileNotFoundError(f"Explicit input image not found: {image_path}")
        return image_path

    images = material_config.get("images", {})

    def image_path(value):
        if not value:
            return None
        path = Path(value)
        return path if path.is_absolute() else input_dir / path

    mapped = image_path(images.get(template_name))
    if mapped:
        if not mapped.exists():
            raise FileNotFoundError(f"Mapped input image not found for {template_name}: {mapped}")
        return mapped

    standard_candidates = []
    for ext in IMAGE_EXTENSIONS:
        standard_candidates.append(input_dir / f"{template_name}{ext}")
    return first_existing(standard_candidates)


def unique_template_names(names):
    wanted = {name for name in names if name in TEMPLATES}
    return [name for name in TEMPLATES.keys() if name in wanted]


def template_names_from_material(material_config):
    return unique_template_names(material_config.get("images", {}).keys())


def template_names_from_input_dir(input_dir):
    detected = []
    for template_name in TEMPLATES:
        if any((input_dir / f"{template_name}{ext}").exists() for ext in IMAGE_EXTENSIONS):
            detected.append(template_name)
    return unique_template_names(detected)


def resolve_template_names(args, input_dir, material_config):
    if args.get("template"):
        return [args["template"]]
    if args.get("all") != "true":
        return [DEFAULT_TEMPLATE]
    if args.get("force-all") == "true":
        return list(TEMPLATES.keys())
    from_material = template_names_from_material(material_config)
    if from_material:
        return from_material
    from_files = template_names_from_input_dir(input_dir)
    if from_files:
        return from_files
    raise FileNotFoundError("No explicit template inputs found in material.json or the input directory")


def copy_for_template(args, material_config, template_name):
    default = material_config.get("default") or {}
    scoped = material_config.get(template_name) or {}
    return {
        "cta": args.get("cta") or scoped.get("cta") or default.get("cta") or DEFAULT_COPY["cta"]
    }


def style_for_template(args, material_config, template_name):
    global_style = material_config.get("style") or {}
    scoped_style = (material_config.get(template_name) or {}).get("style") or {}
    return {
        "buttonBackground": args.get("buttonBackground")
        or scoped_style.get("buttonBackground")
        or global_style.get("buttonBackground")
        or "#111111",
        "buttonTextColor": args.get("buttonTextColor")
        or scoped_style.get("buttonTextColor")
        or global_style.get("buttonTextColor")
        or "#ffffff",
    }


def parse_hex_color(value):
    text = str(value or "").strip()
    if re.fullmatch(r"#[0-9a-fA-F]{3}", text):
        return tuple(int(char * 2, 16) for char in text[1:]) + (255,)
    if re.fullmatch(r"#[0-9a-fA-F]{6}", text):
        return tuple(int(text[index:index + 2], 16) for index in (1, 3, 5)) + (255,)
    raise ValueError(f"Unsupported color value: {value}")


def srgb_to_linear(value):
    value = value / 255
    if value <= 0.04045:
        return value / 12.92
    return ((value + 0.055) / 1.055) ** 2.4


def relative_luminance(color):
    red, green, blue = color[:3]
    return (
        0.2126 * srgb_to_linear(red)
        + 0.7152 * srgb_to_linear(green)
        + 0.0722 * srgb_to_linear(blue)
    )


def contrast_ratio(color_a, color_b):
    lum_a = relative_luminance(color_a)
    lum_b = relative_luminance(color_b)
    light = max(lum_a, lum_b)
    dark = min(lum_a, lum_b)
    return (light + 0.05) / (dark + 0.05)


def readable_text_color(background, requested_text):
    if contrast_ratio(background, requested_text) >= MIN_BUTTON_TEXT_CONTRAST:
        return requested_text

    candidates = [requested_text]
    for value in BUTTON_TEXT_FALLBACKS:
        color = parse_hex_color(value)
        if color not in candidates:
            candidates.append(color)

    return max(candidates, key=lambda color: contrast_ratio(background, color))


def load_font(size):
    if BUTTON_FONT.exists():
        return ImageFont.truetype(str(BUTTON_FONT), size)
    return ImageFont.load_default(size=size)


def cover_image(source_path, width, height):
    image = Image.open(source_path)
    image = ImageOps.exif_transpose(image).convert("RGBA")

    scale = max(width / image.width, height / image.height)
    resized = image.resize((math.ceil(image.width * scale), math.ceil(image.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - width) // 2)
    top = max(0, (resized.height - height) // 2)
    return resized.crop((left, top, left + width, top + height))


def merge_row_runs(rows, max_gap):
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


def detect_channel_text_bbox(image):
    search_left = int(image.width * 0.02)
    search_right = int(image.width * 0.62)
    search_top = 0
    search_bottom = image.height

    row_scores = []
    row_pixels = {}
    step = 2
    for y in range(search_top, search_bottom):
        pixels = []
        score = 0
        for x in range(search_left, search_right, step):
            red, green, blue, alpha = image.getpixel((x, y))
            if alpha < 16:
                continue
            luma = (red * 299 + green * 587 + blue * 114) / 1000
            chroma = max(red, green, blue) - min(red, green, blue)
            red_text = red > green + 14 and red > blue + 14 and luma < 218
            dark_text = luma < 142 and chroma > 12
            if red_text or dark_text:
                score += 1
                pixels.append(x)
        row_scores.append((y, score))
        if pixels:
            row_pixels[y] = pixels

    max_score = max((score for _, score in row_scores), default=0)
    if max_score < 12:
        return None

    threshold = max(8, int(max_score * 0.18))
    candidate_rows = [y for y, score in row_scores if score >= threshold]
    runs = merge_row_runs(candidate_rows, max(8, round(image.height * 0.02)))

    weighted_runs = []
    for top, bottom in runs:
        score = sum(score for y, score in row_scores if top <= y <= bottom)
        height = bottom - top + 1
        if height < 6 or score < max_score * 1.2:
            continue
        weighted_runs.append({"top": top, "bottom": bottom, "score": score})

    if not weighted_runs:
        return None

    anchor = max(weighted_runs, key=lambda item: item["score"])
    selected = [anchor]
    merge_gap = max(34, round(image.height * 0.12))
    changed = True
    while changed:
        changed = False
        selected_top = min(item["top"] for item in selected)
        selected_bottom = max(item["bottom"] for item in selected)
        for run in weighted_runs:
            if run in selected:
                continue
            gap = max(run["top"] - selected_bottom, selected_top - run["bottom"], 0)
            if gap <= merge_gap:
                selected.append(run)
                changed = True

    top = min(item["top"] for item in selected)
    bottom = max(item["bottom"] for item in selected)
    xs = []
    for y in range(top, bottom + 1):
        xs.extend(row_pixels.get(y, []))

    if not xs or bottom - top < 12:
        return None
    return (min(xs), top, max(xs) + step, bottom + 1)


def cover_channel_image(source_path, width, height):
    image = Image.open(source_path)
    image = ImageOps.exif_transpose(image).convert("RGBA")

    target_ratio = width / height
    source_ratio = image.width / image.height
    if abs(source_ratio - target_ratio) / target_ratio <= 0.035:
        print(
            "Channel crop prepared-ratio "
            f"source_ratio={source_ratio:.3f} target_ratio={target_ratio:.3f}"
        )
        return image.resize((width, height), Image.Resampling.LANCZOS)

    scale = max(width / image.width, height / image.height)
    resized = image.resize((math.ceil(image.width * scale), math.ceil(image.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - width) // 2)
    default_top = max(0, (resized.height - height) // 2)
    max_top = max(0, resized.height - height)

    bbox = detect_channel_text_bbox(resized)
    if bbox:
        text_center_y = (bbox[1] + bbox[3]) / 2
        top = round(text_center_y - height / 2)
        top = max(0, min(max_top, top))
        print(
            "Channel crop text-centered "
            f"text_bbox={bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]} "
            f"crop_top={top}"
        )
    else:
        top = default_top
        print(f"Channel crop fallback center crop_top={top}")

    return resized.crop((left, top, left + width, top + height))


def apply_rounded_alpha(image, radius):
    if not radius:
        return image
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, image.width - 1, image.height - 1), radius=radius, fill=255)
    output = image.copy()
    output.putalpha(mask)
    return output


def text_bbox(draw, text, font):
    return draw.textbbox((0, 0), text, font=font)


def fit_font(draw, text, max_width, size):
    font_size = size
    font = load_font(font_size)
    while font_size > 12:
        bbox = text_bbox(draw, text, font)
        if bbox[2] - bbox[0] <= max_width:
            return font
        font_size -= 1
        font = load_font(font_size)
    return font


def clamped_radius(radius, width, height):
    return max(0, min(float(radius), width / 2, height / 2))


def draw_button(image, button, text, style):
    bg = parse_hex_color(style["buttonBackground"])
    fg = readable_text_color(bg, parse_hex_color(style["buttonTextColor"]))
    x = int(button["x"])
    y = int(button["y"])
    width = int(button["width"])
    height = int(button["height"])
    radius = clamped_radius(button["radius"], width, height)
    text_size = int(button["textSize"])

    scale = 4
    layer = Image.new("RGBA", (width * scale, height * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    sw = width * scale
    sh = height * scale
    draw.rounded_rectangle((0, 0, sw, sh), radius=radius * scale, fill=bg)

    gap = max(14, round(text_size * 0.32))
    arrow_width = max(13, round(text_size * 0.42))
    arrow_height = max(18, round(text_size * 0.62))
    stroke_width = max(4, round(text_size * 0.095))
    available_text_width = width - gap - arrow_width - round(width * 0.22)
    font = fit_font(draw, text, available_text_width * scale, text_size * scale)
    bbox = text_bbox(draw, text, font)
    text_width = bbox[2] - bbox[0]

    scaled_gap = gap * scale
    scaled_arrow_width = arrow_width * scale
    scaled_arrow_height = arrow_height * scale
    scaled_stroke_width = stroke_width * scale
    group_width = text_width + scaled_gap + scaled_arrow_width
    group_left = (sw - group_width) / 2
    center_y = sh / 2
    text_x = group_left - bbox[0]
    text_y = center_y - (bbox[1] + bbox[3]) / 2

    draw.text((text_x, text_y), text, font=font, fill=fg)

    arrow_left = group_left + text_width + scaled_gap
    arrow_mid_x = arrow_left + scaled_arrow_width
    arrow_top = center_y - scaled_arrow_height / 2
    arrow_bottom = center_y + scaled_arrow_height / 2
    draw.line(
        [(arrow_left, arrow_top), (arrow_mid_x, center_y), (arrow_left, arrow_bottom)],
        fill=fg,
        width=scaled_stroke_width,
        joint="curve",
    )
    button_image = layer.resize((width, height), Image.Resampling.LANCZOS)
    image.alpha_composite(button_image, (x, y))


def render_template(template_name, args, material_config, input_dir, output_dir):
    if template_name not in TEMPLATES:
        names = ", ".join(TEMPLATES.keys())
        raise ValueError(f'Unknown template "{template_name}". Available: {names}')

    template = TEMPLATES[template_name]
    image_path = image_for_template(input_dir, material_config, template_name, args)
    if not image_path:
        raise FileNotFoundError(f"No input image found for template: {template_name}")

    if template_name in {"channel", "categoryBanner"}:
        image = cover_channel_image(image_path, template["width"], template["height"])
    else:
        image = cover_image(image_path, template["width"], template["height"])
    button = template.get("button")
    if button:
        copy = copy_for_template(args, material_config, template_name)
        style = style_for_template(args, material_config, template_name)
        draw_button(image, button, copy["cta"], style)

    image = apply_rounded_alpha(image, template.get("radius", 0))
    output_path = output_dir / f"{template['outputName']}.png"
    image.save(output_path)
    print(f"{template_name} <- {image_path.name}")
    print(f"Rendered {output_path}")
    print(f"Size {image.width}x{image.height}")
    return output_path


def validate_output(output_path, template):
    image = Image.open(output_path)
    file_ok = output_path.exists() and output_path.stat().st_size > 0
    size_ok = image.size == (template["width"], template["height"])
    mode_ok = image.mode == "RGBA"
    corners_ok = True
    if template.get("radius") and mode_ok:
        corners = [
            (0, 0),
            (image.width - 1, 0),
            (0, image.height - 1),
            (image.width - 1, image.height - 1),
        ]
        corners_ok = all(image.getpixel(point)[3] == 0 for point in corners)
    ok = file_ok and size_ok and mode_ok and corners_ok
    label = "PASS" if ok else "FAIL"
    print(f"Technical QA {label} {output_path.name}")
    return ok


def main():
    args = parse_args(sys.argv[1:])
    input_dir = resolve_work_path(args.get("input-dir"), "material-spec-input")
    material_config = read_material_config(input_dir)
    template_names = resolve_template_names(args, input_dir, material_config)
    for template_name in template_names:
        if not image_for_template(input_dir, material_config, template_name, args):
            raise FileNotFoundError(f"No explicit input image found for template: {template_name}")
    output_dir = create_output_dir(args)

    print(f"Output group {output_dir}")
    print(f"Templates {', '.join(template_names)}")

    ok = True
    for template_name in template_names:
        output_path = render_template(template_name, args, material_config, input_dir, output_dir)
        ok = validate_output(output_path, TEMPLATES[template_name]) and ok
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
