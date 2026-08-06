"""
DICOM -> PNG conversion for the Reading Experience's CT slice viewer.

This is a one-time preprocessing step, not something the API does on every
request: run `python -m scripts.convert_dicom` (see that script) after
dropping raw DICOM files into app/data/dicom_source/{study_id}/. It writes
plain PNGs into app/data/images/{study_id}/, which the API then serves as
static files (app/api/routes_studies.py) - the viewer never touches DICOM
directly, and converting ahead of time keeps requests fast.

Kept deliberately simple for an MVP: reads each slice's pixel data, converts
to Hounsfield units via RescaleSlope/RescaleIntercept, applies a single
window/level (from the DICOM's own WindowCenter/WindowWidth if present,
else a standard brain window), and writes 8-bit grayscale PNGs. No support
for compressed transfer syntaxes beyond what pydicom's installed pixel data
handlers cover, and no multi-frame DICOM support - real-world edge cases a
production PACS integration would need to handle, out of scope here.
"""

from pathlib import Path

import numpy as np
import pydicom
from PIL import Image

# Standard "brain window" (soft tissue window) - reasonable default for CT
# Brain W/O Contrast when a DICOM file doesn't carry its own WindowCenter/
# WindowWidth tags.
DEFAULT_WINDOW_CENTER = 40.0
DEFAULT_WINDOW_WIDTH = 80.0


def _first(value: object) -> float:
    """pydicom returns MultiValue for tags that can repeat (e.g. more than
    one window preset). We only need one window for a flat PNG."""
    if isinstance(value, (list, pydicom.multival.MultiValue)):
        return float(value[0])
    return float(value)


def _slice_to_pixels(dataset: pydicom.Dataset) -> np.ndarray:
    """Raw stored pixel values -> windowed 8-bit grayscale array."""
    pixels = dataset.pixel_array.astype(np.float64)

    slope = float(getattr(dataset, "RescaleSlope", 1.0))
    intercept = float(getattr(dataset, "RescaleIntercept", 0.0))
    hounsfield = pixels * slope + intercept

    if hasattr(dataset, "WindowCenter") and hasattr(dataset, "WindowWidth"):
        center = _first(dataset.WindowCenter)
        width = _first(dataset.WindowWidth)
    else:
        center = DEFAULT_WINDOW_CENTER
        width = DEFAULT_WINDOW_WIDTH
    width = max(width, 1.0)  # guard against a degenerate zero-width window

    low = center - width / 2
    normalized = (hounsfield - low) / width
    clipped = np.clip(normalized, 0.0, 1.0)
    return (clipped * 255).astype(np.uint8)


def _sort_key(path_and_dataset: tuple[Path, pydicom.Dataset]) -> tuple[int, str]:
    path, dataset = path_and_dataset
    instance_number = getattr(dataset, "InstanceNumber", None)
    # (0, n) sorts before (1, name) - files with InstanceNumber always come
    # first, in numeric order; files without it fall back to filename order.
    if instance_number is not None:
        return (0, f"{int(instance_number):09d}")
    return (1, path.name)


def convert_study(dicom_dir: Path, output_dir: Path) -> int:
    """Converts every .dcm file in `dicom_dir` into a sequentially-named PNG
    in `output_dir` (slice_000.png, slice_001.png, ...), ordered by
    InstanceNumber where available. Returns the number of slices written.

    Clears `output_dir` first so re-running conversion after fixing a
    source file doesn't leave stale slices behind.
    """
    dicom_paths = sorted(dicom_dir.glob("*.dcm"))
    if not dicom_paths:
        return 0

    loaded = [(path, pydicom.dcmread(path)) for path in dicom_paths]
    loaded.sort(key=_sort_key)

    output_dir.mkdir(parents=True, exist_ok=True)
    for stale in output_dir.glob("slice_*.png"):
        stale.unlink()

    for index, (_, dataset) in enumerate(loaded):
        pixels_8bit = _slice_to_pixels(dataset)
        image = Image.fromarray(pixels_8bit, mode="L")
        image.save(output_dir / f"slice_{index:03d}.png")

    return len(loaded)
