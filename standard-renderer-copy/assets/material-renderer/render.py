#!/usr/bin/env python3
"""Render standard material PNGs without a browser runtime."""
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
    raise SystemExit("Pillow is required. Install it with: python3 -m pip install Pillow") from error


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent.parent
PACKAGE_ROOT = SKILL_DIR.parent
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
DEFAULT_COPY = {"title": "国庆出游 装备焕新", "subtitle": "儿童自行车限时特惠", "cta": "点击查看"}
FONT_DIR = PACKAGE_ROOT / "assets" / "fonts"
TITLE_FONT = FONT_DIR / "AlimamaShuHeiTi-Bold.ttf"
DEFAULT_FONT = FONT_DIR / "Alibaba_PuHuiTi_2.0_55_Regular_55_Regular.ttf"
FONT_CANDIDATES = (
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
)
TEMPLATES = {
    "channel": {"output": "channel_1041x225", "width": 1041, "height": 225, "radius": 24, "position": "right center", "copy": (46, 49.5, 514, 127, "left", 6), "title": (514, 75, 62), "subtitle": (360, 46, 40)},
    "categoryBanner": {"output": "category_banner_1041x217", "width": 1041, "height": 217, "radius": 24, "position": "right center", "copy": (42, 45.5, 514, 127, "left", 6), "title": (514, 75, 62), "subtitle": (360, 46, 40)},
    "push": {"output": "push_1035x390", "width": 1035, "height": 390, "radius": 24, "position": "center", "copy": (46, 128, 563, 134, "left", 6), "title": (563, 82, 68), "subtitle": (360, 46, 40)},
    "feed": {"output": "feed_503x645", "width": 503, "height": 645, "radius": 0, "position": "center", "copy": (20, 42, 464, 116, "center", 14), "title": (464, 67, 56), "subtitle": (270, 35, 30), "button": (93, 502, 318, 73, 36.5, 32)},
    "popup": {"output": "popup_885x990", "width": 885, "height": 990, "radius": 40, "position": "center", "copy": (70.5, 75, 745, 187, "center", 16), "title": (745, 108, 90), "subtitle": (396, 51, 44), "button": (172, 791, 541, 121, 65, 56)},
    "splash": {"output": "splash_1125x1956", "width": 1125, "height": 1956, "radius": 0, "position": "center", "copy": (66, 374, 994, 259, "center", 46), "title": (994, 144, 120), "subtitle": (540, 69, 60)},
}
QA_CHECKS = {
    "channel": ("subjectFidelity", "copySafeAreaClear", "cropBufferUsable", "noBakedTemplateCopy"),
    "categoryBanner": ("subjectFidelity", "copySafeAreaClear", "bottomAreaClear", "noBakedTemplateCopy"),
    "push": ("subjectFidelity", "copySafeAreaClear", "noBakedTemplateCopy"),
    "feed": ("subjectFidelity", "mainVisualCentered", "copySafeAreaClear", "bottomAreaClear", "noBakedTemplateCopy"),
    "popup": ("subjectFidelity", "mainVisualCentered", "copySafeAreaClear", "bottomAreaClear", "noBakedTemplateCopy"),
    "splash": ("subjectFidelity", "mainVisualCentered", "copySafeAreaClear", "noBakedTemplateCopy"),
}
CENTERING_TEMPLATES = ("feed", "popup", "splash")
CENTERING_TOLERANCE = {"x": 0.05, "y": 0.07}
FIT_TEMPLATES = ("feed", "popup")
FIT_TOLERANCE = 0.03
POOL_CUE_RIGHT_BIASED = "poolCueRightBiased"
POOL_CUE_RIGHT_BIAS_RANGE = (0.58, 0.76)
POOL_CUE_TOP_ANCHOR_TOLERANCE = 0.03
EDGE_CROP_EDGES = {"top", "right", "bottom", "left"}
RETRY_TOP_ANCHORS = {"feed": 26, "popup": 28}
FIT_QA_ACCEPTANCE_BOUNDS = {
    "feed": (0, 168, 503, 575),
    "popup": (0, 277, 885, 912),
}
V4_MAIN_VISUAL_BOUNDS = {
    "feed": (0, 168, 503, 575),
    "popup": (0, 277, 885, 912),
    "splash": (0, 684, 1125, 1956),
}
VERTICAL_MASTER_TEMPLATES = ("feed", "popup", "splash")


def parse_args(argv):
    return {item[2:].split("=", 1)[0]: (item.split("=", 1)[1] if "=" in item else "true") for item in argv if item.startswith("--")}


def safe_name(value):
    return re.sub(r"_+", "_", re.sub(r"\s+", "_", re.sub(r'[\\/:*?"<>|]+', "_", str(value or "").strip()))).strip("_")


def inside(child, parent):
    try:
        Path(child).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False


def project_dir():
    for value in (os.environ.get("MATERIAL_SPEC_PROJECT_DIR"), os.environ.get("CODEX_WORKSPACE_ROOT"), os.environ.get("PWD"), os.getcwd()):
        if value and Path(value).exists() and not inside(value, PACKAGE_ROOT):
            return Path(value).resolve()
    return PACKAGE_ROOT.parent


def work_path(value, fallback):
    path = Path(value) if value and Path(value).is_absolute() else project_dir() / (value or fallback)
    if inside(path, PACKAGE_ROOT):
        return PACKAGE_ROOT.parent / Path(path).resolve().relative_to(PACKAGE_ROOT)
    return path


def output_dir(args):
    root = work_path(args.get("output-dir"), "material-spec-output")
    root.mkdir(parents=True, exist_ok=True)
    base = safe_name(args.get("output-subdir") or args.get("batch")) or f"run_{datetime.now():%Y%m%d_%H%M%S}"
    candidate, index = root / base, 2
    while candidate.exists():
        candidate, index = root / f"{base}_{index}", index + 1
    candidate.mkdir()
    return candidate


def read_json(path):
    file = path / "material.json"
    return json.loads(file.read_text(encoding="utf-8")) if file.exists() else {}


def image_for(template_name, input_dir, config, args):
    if args.get("image"):
        candidate = Path(args["image"])
        if not candidate.exists():
            raise FileNotFoundError(f"Explicit input image not found: {candidate}")
        return candidate
    images = config.get("images", {})
    values = [images.get(template_name), images.get("default"), f"{template_name}.png", f"{template_name}.jpg", f"{template_name}.jpeg", f"{template_name}.webp", "default.png", "hero.png", "main.png", "input.png"]
    for value in values:
        if not value:
            continue
        candidate = Path(value)
        candidate = candidate if candidate.is_absolute() else input_dir / candidate
        if candidate.exists():
            return candidate
    return None


def template_names(args, input_dir, config):
    if args.get("template"):
        return [args["template"]]
    if args.get("all") != "true":
        return ["channel"]
    mapped = [name for name in TEMPLATES if name in config.get("images", {})]
    detected = [name for name in TEMPLATES if any((input_dir / f"{name}{ext}").exists() for ext in IMAGE_EXTENSIONS)]
    return mapped or detected or (list(TEMPLATES) if config.get("images", {}).get("default") or args.get("force-all") == "true" else [])


def main_visual_bounds(template_name, schema_version=0):
    if schema_version >= 4 and template_name in V4_MAIN_VISUAL_BOUNDS:
        left, top, right, bottom = V4_MAIN_VISUAL_BOUNDS[template_name]
        template = TEMPLATES[template_name]
        return left / template["width"], top / template["height"], right / template["width"], bottom / template["height"]
    template = TEMPLATES[template_name]
    _, copy_y, _, copy_height, *_ = template["copy"]
    top = (copy_y + copy_height) / template["height"]
    button = template.get("button")
    bottom = (button[1] + button[3]) / template["height"] if button else 1.0
    return 0.0, top, 1.0, bottom


def crop_mapping(source_width, source_height, target_width, target_height, position):
    """Return the cover-resize and crop geometry used for one background."""
    scale = max(target_width / source_width, target_height / source_height)
    scaled_width = math.ceil(source_width * scale)
    scaled_height = math.ceil(source_height * scale)
    free_x, free_y = scaled_width - target_width, scaled_height - target_height
    text = str(position or "center").lower()
    crop_left = free_x if "right" in text else 0 if "left" in text else free_x // 2
    match = re.search(r"(?:^|\s)(\d+(?:\.\d+)?)%", text)
    crop_top = round(free_y * float(match.group(1)) / 100) if match else (free_y if "bottom" in text else 0 if "top" in text else free_y // 2)
    return {
        "scale": scale,
        "scaledWidth": scaled_width,
        "scaledHeight": scaled_height,
        "cropLeft": crop_left,
        "cropTop": max(0, min(free_y, crop_top)),
    }


def configured_background_position(template_name, args, config):
    scoped = config.get(template_name, {})
    style = {**config.get("style", {}), **scoped.get("style", {})}
    return args.get("backgroundPosition") or args.get("background-position") or scoped.get("backgroundPosition") or style.get("backgroundPosition")


def vertical_master_subject_center(template_name, config):
    scoped = config.get(template_name, {})
    master = config.get("verticalMaster", {})
    value = scoped.get("masterSubjectCenterY", master.get("subjectCenterY") if isinstance(master, dict) else None)
    if value is None:
        return None
    if template_name not in VERTICAL_MASTER_TEMPLATES:
        raise ValueError("verticalMaster.subjectCenterY is only supported for feed, popup, and splash.")
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= float(value) <= 1:
        raise ValueError("verticalMaster.subjectCenterY must be a normalized number between 0 and 1.")
    return float(value)


def automatic_master_position(template_name, source_width, source_height, subject_center_y):
    template = TEMPLATES[template_name]
    mapping = crop_mapping(source_width, source_height, template["width"], template["height"], "center")
    free_y = mapping["scaledHeight"] - template["height"]
    if free_y <= 0:
        return "center 50%"
    _, block_top, _, block_bottom = main_visual_bounds(template_name, 4)
    target_center_y = (block_top + block_bottom) / 2
    desired_crop_top = subject_center_y * mapping["scaledHeight"] - target_center_y * template["height"]
    percent = max(0, min(100, desired_crop_top / free_y * 100))
    return f"center {percent:.3f}%"


def effective_background_position(template_name, args, config, source_width, source_height):
    explicit = configured_background_position(template_name, args, config)
    if explicit:
        return str(explicit)
    subject_center_y = vertical_master_subject_center(template_name, config)
    if subject_center_y is not None:
        return automatic_master_position(template_name, source_width, source_height, subject_center_y)
    return TEMPLATES[template_name]["position"]


def normalized_bounds(value, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object.")
    keys = ("left", "top", "right", "bottom")
    if any(type(value.get(key)) not in (int, float) for key in keys):
        raise ValueError(f"{label} must contain numeric left, top, right, and bottom values.")
    left, top, right, bottom = (float(value[key]) for key in keys)
    if not all(math.isfinite(number) for number in (left, top, right, bottom)) or not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
        raise ValueError(f"{label} must use normalized bounds between 0 and 1.")
    return left, top, right, bottom


def uses_pool_cue_right_bias(record, template_name=None):
    mode = record.get("compositionMode")
    if mode is None:
        return False
    if mode != POOL_CUE_RIGHT_BIASED:
        raise ValueError(f"preRenderQA compositionMode must be {POOL_CUE_RIGHT_BIASED!r} when supplied.")
    if template_name is not None and template_name not in CENTERING_TEMPLATES:
        raise ValueError(f"preRenderQA.{template_name}.compositionMode {POOL_CUE_RIGHT_BIASED!r} is only supported for feed, popup, and splash.")
    measurement = record.get("poolCueMeasurement")
    core_subject = measurement.get("coreSubject", "") if isinstance(measurement, dict) else ""
    if not isinstance(core_subject, str) or not re.search(r"台球杆|pool cue|billiard cue", core_subject, re.IGNORECASE):
        raise ValueError(f"preRenderQA compositionMode {POOL_CUE_RIGHT_BIASED!r} requires poolCueMeasurement.coreSubject to explicitly name a pool cue.")
    return True


def reference_edge_crops(config):
    """Validate the optional reference-image edge-crop contract once per task."""
    value = config.get("referenceEdgeCrops")
    if value is None:
        return ()
    if not isinstance(value, list) or not value:
        raise ValueError("referenceEdgeCrops must be a non-empty list when supplied.")
    contracts = []
    subjects = set()
    for index, item in enumerate(value):
        label = f"referenceEdgeCrops[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"{label} must be an object.")
        subject = item.get("subject")
        if not isinstance(subject, str) or not subject.strip():
            raise ValueError(f"{label}.subject must name the actual edge-cropped subject.")
        if subject in subjects:
            raise ValueError(f"{label}.subject must not duplicate another referenceEdgeCrops subject.")
        edges = item.get("exitEdges")
        if not isinstance(edges, list) or not edges or any(edge not in EDGE_CROP_EDGES for edge in edges) or len(set(edges)) != len(edges):
            raise ValueError(f"{label}.exitEdges must be a non-empty list of unique canvas edges: top, right, bottom, left.")
        direction = item.get("exitDirection")
        if not isinstance(direction, str) or not direction.strip():
            raise ValueError(f"{label}.exitDirection must describe the reference exit direction.")
        if item.get("mustRemainContinuous") is not True:
            raise ValueError(f"{label}.mustRemainContinuous must be true.")
        if item.get("preserveRelativeOcclusion") is not True:
            raise ValueError(f"{label}.preserveRelativeOcclusion must be true.")
        subjects.add(subject)
        contracts.append({"subject": subject, "exitEdges": tuple(edges), "exitDirection": direction})
    return tuple(contracts)


def validate_reference_edge_crop_measurement(template_name, record, contracts):
    if not contracts:
        return
    label = f"preRenderQA.{template_name}.referenceEdgeCropMeasurement"
    measurement = record.get("referenceEdgeCropMeasurement")
    checks = record.get("checks", {})
    check_value = checks.get("referenceEdgeCropsPreserved") if isinstance(checks, dict) else None
    is_observation = record.get("status") == "RENDER_WITH_OBSERVATION"
    if type(check_value) is not bool:
        raise ValueError(f"preRenderQA.{template_name}.checks.referenceEdgeCropsPreserved must be boolean when referenceEdgeCrops is declared.")
    if not isinstance(measurement, dict) or type(measurement.get("preserved")) is not bool:
        raise ValueError(f"{label}.preserved must be boolean when referenceEdgeCrops is declared.")
    if measurement["preserved"] is not check_value:
        raise ValueError(f"{label}.preserved must match checks.referenceEdgeCropsPreserved.")
    if check_value is False and not is_observation:
        raise ValueError(f"{label}.preserved may be false only for RENDER_WITH_OBSERVATION.")
    items = measurement.get("items")
    if not isinstance(items, list) or len(items) != len(contracts):
        raise ValueError(f"{label}.items must record every declared reference edge crop.")
    observed = {}
    for index, item in enumerate(items):
        item_label = f"{label}.items[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"{item_label} must be an object.")
        subject = item.get("subject")
        edges = item.get("exitEdges")
        direction = item.get("exitDirection")
        if not isinstance(subject, str) or not isinstance(edges, list) or not isinstance(direction, str):
            raise ValueError(f"{item_label} must include subject, exitEdges, and exitDirection.")
        if any(edge not in EDGE_CROP_EDGES for edge in edges) or len(set(edges)) != len(edges):
            raise ValueError(f"{item_label}.exitEdges must be unique canvas edges: top, right, bottom, left.")
        if not direction.strip():
            raise ValueError(f"{item_label}.exitDirection must not be empty.")
        if type(item.get("continuous")) is not bool or type(item.get("relativeOcclusionPreserved")) is not bool:
            raise ValueError(f"{item_label} must record boolean continuity and relative occlusion results.")
        if subject in observed:
            raise ValueError(f"{item_label}.subject must not be duplicated.")
        observed[subject] = {
            "exitEdges": tuple(edges),
            "exitDirection": direction,
            "continuous": item["continuous"],
            "relativeOcclusionPreserved": item["relativeOcclusionPreserved"],
        }
    expected = {item["subject"]: {"exitEdges": item["exitEdges"], "exitDirection": item["exitDirection"]} for item in contracts}
    if set(observed) != set(expected):
        raise ValueError(f"{label}.items must record the declared edge-cropped subjects exactly once.")
    if check_value is True:
        for subject, expected_item in expected.items():
            actual = observed[subject]
            if (
                actual["exitEdges"] != expected_item["exitEdges"]
                or actual["exitDirection"] != expected_item["exitDirection"]
                or actual["continuous"] is not True
                or actual["relativeOcclusionPreserved"] is not True
            ):
                raise ValueError(f"{label}.items must exactly preserve the declared exit contract when preserved is true.")


def validate_centering_measurement(template_name, record, schema_version):
    measurement = record.get("centeringMeasurement")
    label = f"preRenderQA.{template_name}.centeringMeasurement"
    if not isinstance(measurement, dict):
        raise ValueError(f"{label} is required for qaSchemaVersion 2.")
    if not isinstance(measurement.get("coreSubject"), str) or not measurement["coreSubject"].strip():
        raise ValueError(f"{label}.coreSubject must name the actual core subject group.")
    subject_left, subject_top, subject_right, subject_bottom = normalized_bounds(measurement.get("subjectBounds"), f"{label}.subjectBounds")
    center = measurement.get("subjectCenter")
    if not isinstance(center, dict) or any(type(center.get(key)) not in (int, float) for key in ("x", "y")):
        raise ValueError(f"{label}.subjectCenter must contain numeric x and y values.")
    center_x, center_y = float(center["x"]), float(center["y"])
    if not all(math.isfinite(number) for number in (center_x, center_y)):
        raise ValueError(f"{label}.subjectCenter must use finite values.")
    calculated_x = (subject_left + subject_right) / 2
    calculated_y = (subject_top + subject_bottom) / 2
    if abs(center_x - calculated_x) > 0.01 or abs(center_y - calculated_y) > 0.01:
        raise ValueError(f"{label}.subjectCenter must match the center of subjectBounds.")
    block_left, block_top, block_right, block_bottom = main_visual_bounds(template_name, schema_version)
    offset_x = (center_x - (block_left + block_right) / 2) / (block_right - block_left)
    offset_y = (center_y - (block_top + block_bottom) / 2) / (block_bottom - block_top)
    centered = abs(offset_x) <= CENTERING_TOLERANCE["x"] and abs(offset_y) <= CENTERING_TOLERANCE["y"]
    if record["checks"].get("mainVisualCentered") is not centered:
        verdict = "true" if centered else "false"
        raise ValueError(f"preRenderQA.{template_name}.checks.mainVisualCentered must be {verdict} from centeringMeasurement.")


def validate_pool_cue_right_bias_measurement(template_name, record):
    measurement = record.get("poolCueMeasurement")
    label = f"preRenderQA.{template_name}.poolCueMeasurement"
    if not isinstance(measurement, dict):
        raise ValueError(f"{label} is required for poolCueRightBiased.")
    core_subject = measurement.get("coreSubject")
    if not isinstance(core_subject, str) or not re.search(r"台球杆|pool cue|billiard cue", core_subject, re.IGNORECASE):
        raise ValueError(f"{label}.coreSubject must explicitly name the pool cue.")
    left, top, right, bottom = normalized_bounds(measurement.get("subjectBounds"), f"{label}.subjectBounds")
    center = measurement.get("subjectCenter")
    if not isinstance(center, dict) or any(type(center.get(key)) not in (int, float) for key in ("x", "y")):
        raise ValueError(f"{label}.subjectCenter must contain numeric x and y values.")
    center_x, center_y = float(center["x"]), float(center["y"])
    if not all(math.isfinite(number) for number in (center_x, center_y)):
        raise ValueError(f"{label}.subjectCenter must use finite values.")
    if abs(center_x - (left + right) / 2) > 0.01 or abs(center_y - (top + bottom) / 2) > 0.01:
        raise ValueError(f"{label}.subjectCenter must match the center of subjectBounds.")
    right_biased = POOL_CUE_RIGHT_BIAS_RANGE[0] <= center_x <= POOL_CUE_RIGHT_BIAS_RANGE[1]
    if record["checks"].get("poolCueRightBiased") is not right_biased:
        verdict = "true" if right_biased else "false"
        raise ValueError(f"preRenderQA.{template_name}.checks.poolCueRightBiased must be {verdict} from poolCueMeasurement.")


def pixel_bounds(value, label, width, height):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object.")
    keys = ("left", "top", "right", "bottom")
    if any(type(value.get(key)) not in (int, float) for key in keys):
        raise ValueError(f"{label} must contain numeric left, top, right, and bottom values.")
    left, top, right, bottom = (float(value[key]) for key in keys)
    if not all(math.isfinite(number) for number in (left, top, right, bottom)) or not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise ValueError(f"{label} must use pixel bounds inside the final {width}x{height} frame.")
    return left, top, right, bottom


def pool_cue_title_gap_allowed(template_name, record, config):
    """The opt-in title-gap exception is limited to the documented cue mode."""
    scoped = config.get(template_name, {})
    return (
        template_name in FIT_TEMPLATES
        and record.get("compositionMode") == POOL_CUE_RIGHT_BIASED
        and scoped.get("poolCueTitleGapAllowance") is True
    )


def fit_acceptance_bounds(template_name, record, config):
    left, top, right, bottom = FIT_QA_ACCEPTANCE_BOUNDS[template_name]
    if pool_cue_title_gap_allowed(template_name, record, config):
        # The cue's diagonal head may use upper non-text space. Actual title/subtitle
        # non-overlap remains an explicit visual QA check below.
        return left, 0, right, bottom
    return left, top, right, bottom


def validate_fit_measurement(template_name, record, config):
    measurement = record.get("fitMeasurement")
    label = f"preRenderQA.{template_name}.fitMeasurement"
    if not isinstance(measurement, dict):
        raise ValueError(f"{label} is required for qaSchemaVersion 3.")
    template = TEMPLATES[template_name]
    left, top, right, bottom = pixel_bounds(measurement.get("subjectBoundsPx"), f"{label}.subjectBoundsPx", template["width"], template["height"])
    safe_left, safe_top, safe_right, safe_bottom = fit_acceptance_bounds(template_name, record, config)
    subject_width, subject_height = right - left, bottom - top
    safe_width, safe_height = safe_right - safe_left, safe_bottom - safe_top
    scale = min(1.0, safe_width / subject_width, safe_height / subject_height)
    expected_scale_percent = 100 - math.ceil((1 - scale) * 100) if scale < 1 else 100
    scale_percent = measurement.get("requiredScalePercent")
    if type(scale_percent) is not int or not 0 < scale_percent <= 100:
        raise ValueError(f"{label}.requiredScalePercent must be an integer between 1 and 100.")
    if scale_percent != expected_scale_percent:
        raise ValueError(f"{label}.requiredScalePercent must be {expected_scale_percent} from subjectBoundsPx and the button-lower-edge safe area.")
    fits = scale >= 1 - FIT_TOLERANCE
    if record["checks"].get("mainVisualFits") is not fits:
        verdict = "true" if fits else "false"
        raise ValueError(f"preRenderQA.{template_name}.checks.mainVisualFits must be {verdict} from fitMeasurement.")


def expected_scale_percent(template_name, bounds, record, config):
    template = TEMPLATES[template_name]
    left, top, right, bottom = pixel_bounds(bounds, f"{template_name}.subjectBoundsPx", template["width"], template["height"])
    safe_left, safe_top, safe_right, safe_bottom = fit_acceptance_bounds(template_name, record, config)
    scale = min(1.0, (safe_right - safe_left) / (right - left), (safe_bottom - safe_top) / (bottom - top))
    return 100 - math.ceil((1 - scale) * 100) if scale < 1 else 100, (left, top, right, bottom)


def validate_retry_plan(template_name, record, config, require_edge_crop_clause=False):
    plan = record.get("retryPlan")
    label = f"preRenderQA.{template_name}.retryPlan"
    if not isinstance(plan, dict):
        raise ValueError(f"{label} is required after a targeted retry.")
    source_image = plan.get("sourceImage")
    if not isinstance(source_image, dict) or any(type(source_image.get(key)) is not int or source_image[key] <= 0 for key in ("width", "height")):
        raise ValueError(f"{label}.sourceImage must contain positive integer width and height values.")
    template = TEMPLATES[template_name]
    position = plan.get("backgroundPosition", "center")
    if not isinstance(position, str) or not position.strip():
        raise ValueError(f"{label}.backgroundPosition must be a non-empty crop position string.")
    expected_crop = crop_mapping(source_image["width"], source_image["height"], template["width"], template["height"], position)
    crop = plan.get("coverCrop")
    if not isinstance(crop, dict) or any(key not in crop for key in expected_crop):
        raise ValueError(f"{label}.coverCrop must describe the actual cover-crop mapping.")
    if abs(float(crop["scale"]) - expected_crop["scale"]) > 0.0001 or any(crop[key] != expected_crop[key] for key in ("scaledWidth", "scaledHeight", "cropLeft", "cropTop")):
        raise ValueError(f"{label}.coverCrop must match the source image and retry-plan backgroundPosition.")
    source = plan.get("sourceMeasurement")
    if not isinstance(source, dict):
        raise ValueError(f"{label}.sourceMeasurement must be an object.")
    right_biased = uses_pool_cue_right_bias(record, template_name)
    scale_percent, (left, top, right, bottom) = expected_scale_percent(template_name, source.get("subjectBoundsPx"), record, config)
    if plan.get("targetScalePercent") != scale_percent:
        raise ValueError(f"{label}.targetScalePercent must be {scale_percent} from sourceMeasurement.subjectBoundsPx.")
    block_left, block_top, block_right, block_bottom = main_visual_bounds(template_name, 4)
    block_left, block_right = block_left * template["width"], block_right * template["width"]
    block_top, block_bottom = block_top * template["height"], block_bottom * template["height"]
    center_x, center_y = (left + right) / 2, (top + bottom) / 2
    target_x, target_y = (block_left + block_right) / 2, (block_top + block_bottom) / 2
    expected_actions = []
    if scale_percent < 97:
        expected_actions.append(f"scale:{scale_percent}")
    if right_biased:
        right_min, right_max = (ratio * template["width"] for ratio in POOL_CUE_RIGHT_BIAS_RANGE)
        if center_x < right_min:
            expected_actions.append("right")
        elif center_x > right_max:
            expected_actions.append("left")
        top_anchor = RETRY_TOP_ANCHORS[template_name] / 100 * template["height"]
        top_tolerance = POOL_CUE_TOP_ANCHOR_TOLERANCE * template["height"]
        if top < top_anchor - top_tolerance:
            expected_actions.append("down")
        elif top > top_anchor + top_tolerance:
            expected_actions.append("up")
    else:
        if center_x < target_x - (block_right - block_left) * CENTERING_TOLERANCE["x"]:
            expected_actions.append("right")
        elif center_x > target_x + (block_right - block_left) * CENTERING_TOLERANCE["x"]:
            expected_actions.append("left")
        if center_y < target_y - (block_bottom - block_top) * CENTERING_TOLERANCE["y"]:
            expected_actions.append("down")
        elif center_y > target_y + (block_bottom - block_top) * CENTERING_TOLERANCE["y"]:
            expected_actions.append("up")
    if plan.get("actions") != expected_actions:
        raise ValueError(f"{label}.actions must be {expected_actions!r} from sourceMeasurement.")
    prompt = plan.get("prompt")
    legacy_objective = "在主视觉区内水平居中和垂直居中"
    anchor_objective = f"距画面顶部约{RETRY_TOP_ANCHORS[template_name]}%的位置"
    if not isinstance(prompt, str) or (legacy_objective not in prompt and anchor_objective not in prompt):
        raise ValueError(f"{label}.prompt must include the legacy centering objective or the resource top-anchor objective.")
    action_text = {"left": "向左", "right": "向右", "up": "向上", "down": "向下"}
    for action in expected_actions:
        expected_text = f"缩小至原尺寸的{scale_percent}%" if action.startswith("scale:") else action_text[action]
        if expected_text not in prompt:
            raise ValueError(f"{label}.prompt is missing the required action: {expected_text}.")
    if require_edge_crop_clause and "参考图边缘出画关系" not in prompt:
        raise ValueError(f"{label}.prompt must preserve the reference edge-crop contract.")


def validate_pre_render_qa(config, names):
    records = config.get("preRenderQA")
    schema_version = config.get("qaSchemaVersion", 0)
    if type(schema_version) is not int:
        schema_version = 0
    if not isinstance(records, dict):
        raise ValueError("Missing preRenderQA records. Complete Pre-render QA before rendering.")
    edge_crop_contracts = reference_edge_crops(config)
    for name in names:
        record = records.get(name)
        if not isinstance(record, dict):
            raise ValueError(f"Missing preRenderQA record for {name}.")
        status = record.get("status")
        checks = record.get("checks")
        evidence = record.get("evidence")
        if not isinstance(checks, dict):
            raise ValueError(f"preRenderQA.{name}.checks must be an object.")
        if not isinstance(evidence, str) or not evidence.strip():
            raise ValueError(f"preRenderQA.{name}.evidence must describe the QA observation.")
        right_biased = uses_pool_cue_right_bias(record, name)
        if right_biased:
            cue_subject = record["poolCueMeasurement"]["coreSubject"]
            cue_contracts = [item for item in edge_crop_contracts if item["subject"] == cue_subject]
            if len(cue_contracts) != 1 or "right" not in cue_contracts[0]["exitEdges"] or "右上" not in cue_contracts[0]["exitDirection"]:
                raise ValueError(f"preRenderQA.{name}.compositionMode {POOL_CUE_RIGHT_BIASED!r} requires a matching referenceEdgeCrops contract for the same pool cue exiting toward the upper right.")
        base_checks = list(QA_CHECKS[name])
        if right_biased:
            base_checks[base_checks.index("mainVisualCentered")] = "poolCueRightBiased"
        title_gap_allowed = pool_cue_title_gap_allowed(name, record, config)
        required = tuple(base_checks) + (("mainVisualFits",) if schema_version >= 3 and name in FIT_TEMPLATES else ()) + (("poolCueTitleGapClear",) if title_gap_allowed else ()) + (("referenceEdgeCropsPreserved",) if edge_crop_contracts else ())
        missing = [key for key in required if key not in checks]
        if missing:
            raise ValueError(f"preRenderQA.{name}.checks is missing: {', '.join(missing)}.")
        if edge_crop_contracts and type(checks.get("referenceEdgeCropsPreserved")) is not bool:
            raise ValueError(f"preRenderQA.{name}.checks.referenceEdgeCropsPreserved must be boolean when referenceEdgeCrops is declared.")
        if schema_version >= 2 and name in CENTERING_TEMPLATES:
            if right_biased:
                validate_pool_cue_right_bias_measurement(name, record)
            else:
                validate_centering_measurement(name, record, schema_version)
        validate_reference_edge_crop_measurement(name, record, edge_crop_contracts)
        if schema_version >= 3 and name in FIT_TEMPLATES:
            validate_fit_measurement(name, record, config)
        if schema_version >= 4 and name in FIT_TEMPLATES and record.get("targetedRetryCount") == 1:
            validate_retry_plan(
                name,
                record,
                config,
                require_edge_crop_clause=bool(edge_crop_contracts),
            )
        if status == "PASS":
            failed = [key for key in required if checks[key] is not True]
            if failed:
                raise ValueError(f"preRenderQA.{name} is PASS but failed checks remain: {', '.join(failed)}.")
            continue
        if status == "RENDER_WITH_OBSERVATION":
            retry_count = record.get("targetedRetryCount")
            observation = record.get("observation")
            failed = [key for key in required if checks[key] is not True]
            if retry_count != 1:
                raise ValueError(f"preRenderQA.{name}.targetedRetryCount must be 1 before rendering with an observation.")
            if not failed:
                raise ValueError(f"preRenderQA.{name} has no failed check for RENDER_WITH_OBSERVATION.")
            if not isinstance(observation, str) or not observation.strip():
                raise ValueError(f"preRenderQA.{name}.observation must state the remaining issue.")
            continue
        if name == "channel" and status == "ADVISORY_FAIL":
            continue
        raise ValueError(f"preRenderQA.{name} must be PASS or RENDER_WITH_OBSERVATION after one retry; got {status!r}.")


def merged(template_name, args, config):
    scoped = config.get(template_name, {})
    default = config.get("default", {})
    style = {**config.get("style", {}), **scoped.get("style", {})}
    copy = {key: args.get(key) or scoped.get(key) or default.get(key) or DEFAULT_COPY[key] for key in DEFAULT_COPY}
    for key in ("titleColor", "subtitleColor", "titleFont", "subtitleFont", "buttonFont", "backgroundPosition"):
        value = args.get(key) or args.get(key.replace("Position", "-position")) or scoped.get(key) or style.get(key)
        if value:
            style[key] = value
    return copy, style


def font(size, requested="", default=DEFAULT_FONT):
    candidates = [requested] if requested and Path(requested).exists() else []
    candidates.append(default)
    candidates.extend(FONT_CANDIDATES)
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    raise RuntimeError("No supported Chinese font found. Expected a bundled font or STHeiti/Hiragino Sans GB.")


def cover(source, width, height, position):
    image = ImageOps.exif_transpose(Image.open(source)).convert("RGBA")
    mapping = crop_mapping(image.width, image.height, width, height, position)
    image = image.resize((mapping["scaledWidth"], mapping["scaledHeight"]), Image.Resampling.LANCZOS)
    return image.crop((mapping["cropLeft"], mapping["cropTop"], mapping["cropLeft"] + width, mapping["cropTop"] + height))


def cover_channel(source, width, height):
    image = ImageOps.exif_transpose(Image.open(source)).convert("RGBA")
    target_ratio = width / height
    source_ratio = image.width / image.height
    if abs(source_ratio - target_ratio) / target_ratio > 0.035:
        raise ValueError(
            "Horizontal input must be prepared at the final ratio. Run scripts/prepare-channel-input.py first."
        )
    return image.resize((width, height), Image.Resampling.LANCZOS)


def rgba(value, fallback):
    value = str(value or fallback).strip()
    if re.fullmatch(r"#[0-9a-fA-F]{3}", value):
        value = "#" + "".join(char * 2 for char in value[1:])
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ValueError(f"Unsupported color: {value}")
    return tuple(int(value[index:index + 2], 16) for index in (1, 3, 5)) + (255,)


def fit(draw, text, maximum, size, family, default=DEFAULT_FONT):
    for point in range(size, 11, -1):
        selected = font(point, family, default)
        box = draw.textbbox((0, 0), text, font=selected)
        if box[2] - box[0] <= maximum:
            return selected
    return font(12, family, default)


def draw_text(draw, text, x, y, width, height, size, align, color, family, default=DEFAULT_FONT):
    selected = fit(draw, text, width, size, family, default)
    box = draw.textbbox((0, 0), text, font=selected)
    text_width = box[2] - box[0]
    left = x if align == "left" else x + (width - text_width) / 2
    top = y + (height - (box[3] - box[1])) / 2 - box[1]
    draw.text((round(left), round(top)), text, font=selected, fill=color)


def cta_colors(title_color):
    value = str(title_color or "#111111").strip().lower()
    if value in {"#111", "#111111", "#000", "#000000"}:
        return rgba(value, "#111111"), rgba("#ffffff", "#ffffff")
    if value in {"#fff", "#ffffff"}:
        return rgba(value, "#ffffff"), rgba("#111111", "#111111")
    raise ValueError("feed and popup titleColor must be deep/black or white so the CTA can match it.")


def draw_button(image, data, text, style):
    x, y, width, height, radius, size = data
    background, foreground = cta_colors(style.get("titleColor"))
    scale, layer = 4, Image.new("RGBA", (width * 4, height * 4))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle((0, 0, width * scale, height * scale), radius=radius * scale, fill=background)
    selected = fit(draw, text, (width - size * 1.5) * scale, size * scale, style.get("buttonFont", ""))
    box = draw.textbbox((0, 0), text, font=selected)
    gap, arrow = round(size * .32) * scale, round(size * .42) * scale
    group = box[2] - box[0] + gap + arrow
    left, middle = (width * scale - group) / 2, height * scale / 2
    draw.text((left - box[0], middle - (box[1] + box[3]) / 2), text, font=selected, fill=foreground)
    arrow_x, arrow_h, stroke = left + box[2] - box[0] + gap, round(size * .62) * scale, max(2, round(size * .095)) * scale
    draw.line(((arrow_x, middle - arrow_h / 2), (arrow_x + arrow, middle), (arrow_x, middle + arrow_h / 2)), fill=foreground, width=stroke, joint="curve")
    image.alpha_composite(layer.resize((width, height), Image.Resampling.LANCZOS), (x, y))


def rounded(image, radius):
    if not radius:
        return image
    mask = Image.new("L", image.size)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, image.width - 1, image.height - 1), radius=radius, fill=255)
    image.putalpha(mask)
    return image


def render(name, args, config, input_dir, output):
    if name not in TEMPLATES:
        raise ValueError(f"Unknown template {name}. Available: {', '.join(TEMPLATES)}")
    template, source = TEMPLATES[name], image_for(name, input_dir, config, args)
    if not source:
        raise FileNotFoundError(f"No input image found for template: {name}")
    copy, style = merged(name, args, config)
    if name in {"channel", "categoryBanner"}:
        image, position = cover_channel(source, template["width"], template["height"]), template["position"]
    else:
        with Image.open(source) as source_image:
            position = effective_background_position(name, args, config, source_image.width, source_image.height)
        image = cover(source, template["width"], template["height"], position)
    draw = ImageDraw.Draw(image)
    x, y, copy_width, _, align, gap = template["copy"]
    title_width, title_height, title_size = template["title"]
    subtitle_width, subtitle_height, subtitle_size = template["subtitle"]
    draw_text(draw, copy["title"], x, y, title_width, title_height, title_size, align, rgba(style.get("titleColor"), "#111111"), style.get("titleFont", ""), TITLE_FONT)
    draw_text(draw, copy["subtitle"], x, y + title_height + gap, subtitle_width if align == "left" else copy_width, subtitle_height, subtitle_size, align, rgba(style.get("subtitleColor"), "#111111"), style.get("subtitleFont", ""))
    if template.get("button"):
        draw_button(image, template["button"], copy["cta"], style)
    file = output / f"{template['output']}.png"
    rounded(image, template["radius"]).save(file)
    result = Image.open(file)
    valid = result.size == (template["width"], template["height"]) and result.mode == "RGBA"
    if template["radius"]:
        valid = valid and all(result.getpixel(point)[3] == 0 for point in ((0, 0), (result.width - 1, 0), (0, result.height - 1), (result.width - 1, result.height - 1)))
    print(f"{'PASS' if valid else 'FAIL'} {name} <- {source.name} ({position}) -> {file}")
    record = config["preRenderQA"][name]
    if record.get("status") == "RENDER_WITH_OBSERVATION":
        print(f"OBSERVATION {name}: {record['observation']}")
    return valid


def main():
    args = parse_args(sys.argv[1:])
    input_dir = work_path(args.get("input-dir"), "material-spec-input")
    config, names = read_json(input_dir), template_names(args, input_dir, read_json(input_dir))
    if not names:
        raise SystemExit("No template inputs found in material.json or input directory")
    for name in names:
        if name not in TEMPLATES:
            raise ValueError(f"Unknown template {name}. Available: {', '.join(TEMPLATES)}")
        source = image_for(name, input_dir, config, args)
        if not source:
            raise FileNotFoundError(f"No input image found for template: {name}")
        if name in {"channel", "categoryBanner"}:
            cover_channel(source, TEMPLATES[name]["width"], TEMPLATES[name]["height"])
    validate_pre_render_qa(config, names)
    output = output_dir(args)
    print(f"Output group {output}")
    if not all(render(name, args, config, input_dir, output) for name in names):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
