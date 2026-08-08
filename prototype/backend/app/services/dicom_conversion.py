"""
DICOM -> preserved-pixel-data conversion for the Reading Experience's CT
slice viewer.

This is a one-time preprocessing step, not something the API does on every
request: run `python -m scripts.convert_dicom` (see that script) after
dropping raw DICOM files into app/data/dicom_source/{study_id}/. Files are
discovered by `*.dcm` extension, plus extensionless files that are valid
DICOM - detected by attempting to read them, not by filename, since some
real-world scanner/PACS exports drop the extension (see
`_discover_dicom_files`). The viewer never touches DICOM directly, and
converting ahead of time keeps requests fast - but unlike an earlier version
of this pipeline, conversion no longer bakes in a single window/level. It
writes:

- app/data/images/{study_id}/slice_000.png, slice_001.png, ... - each a
  16-bit grayscale PNG losslessly encoding the slice's raw Hounsfield-unit
  data (RescaleSlope/RescaleIntercept already applied - see
  app/services/windowing.py's encode_hu_to_uint16 for the encoding). NOT a
  pre-windowed 8-bit image.
- app/data/images/{study_id}/window_default.json - the study's own DICOM
  WindowCenter/WindowWidth, if it carried one. Omitted when the source
  DICOM had neither tag.

Windowing (Brain / Blood-ICH / DICOM-default presets) is applied per-request
by GET /studies/{id}/slices/{n} (app/api/routes_studies.py) against this
preserved data, so window/level can change without ever re-running this
conversion. See app/services/windowing.py for the presets and the windowing
math itself.

Kept deliberately simple for an MVP: reads each slice's pixel data and
converts to Hounsfield units via RescaleSlope/RescaleIntercept. No support
for compressed transfer syntaxes beyond what pydicom's installed pixel data
handlers cover, and no multi-frame DICOM support - real-world edge cases a
production PACS integration would need to handle, out of scope here.
"""

import json
from pathlib import Path

import numpy as np
import pydicom
from PIL import Image

from app.services.windowing import WindowPreset, encode_hu_to_uint16

WINDOW_DEFAULT_FILENAME = "window_default.json"


def _first(value: object) -> float:
    """pydicom returns MultiValue for tags that can repeat (e.g. more than
    one window preset). We only need one window center/width per study."""
    if isinstance(value, (list, pydicom.multival.MultiValue)):
        return float(value[0])
    return float(value)


def _slice_to_hu(dataset: pydicom.Dataset) -> np.ndarray:
    """Raw stored pixel values -> Hounsfield units. Windowing does NOT
    happen here anymore - see app/services/windowing.py, applied per-request
    against the preserved HU data this function returns."""
    pixels = dataset.pixel_array.astype(np.float64)
    slope = float(getattr(dataset, "RescaleSlope", 1.0))
    intercept = float(getattr(dataset, "RescaleIntercept", 0.0))
    return pixels * slope + intercept


def _dicom_window(dataset: pydicom.Dataset) -> WindowPreset | None:
    """The DICOM's own WindowCenter/WindowWidth, if present - preserved to
    disk so the "dicom" preset can use it later, since the raw .dcm file
    isn't re-read after conversion."""
    if not (hasattr(dataset, "WindowCenter") and hasattr(dataset, "WindowWidth")):
        return None
    return WindowPreset(center=_first(dataset.WindowCenter), width=_first(dataset.WindowWidth))


def _sort_key(path_and_dataset: tuple[Path, pydicom.Dataset]) -> tuple[int, str]:
    path, dataset = path_and_dataset
    instance_number = getattr(dataset, "InstanceNumber", None)
    # (0, n) sorts before (1, name) - files with InstanceNumber always come
    # first, in numeric order; files without it fall back to filename order.
    if instance_number is not None:
        return (0, f"{int(instance_number):09d}")
    return (1, path.name)


def _try_read_as_dicom(path: Path) -> pydicom.Dataset | None:
    """Best-effort DICOM read for a file with no extension to go on.

    Some real-world scanner/PACS exports drop the .dcm extension entirely,
    and some of those also omit the standard 128-byte preamble that
    `pydicom.dcmread` requires by default - hence `force=True`. Since that
    makes dcmread far more permissive (it'll happily "parse" a lot of
    non-DICOM binary too), we additionally require that pixel data actually
    decodes - a file that isn't really DICOM essentially never gets this
    far. Returns None (not raises) on any failure, since this is a
    speculative probe, not a file we already know is DICOM.
    """
    try:
        dataset = pydicom.dcmread(path, force=True)
        dataset.pixel_array  # noqa: B018 - access is the validation; raises if not decodable
    except Exception:
        return None
    return dataset


def _discover_dicom_files(dicom_dir: Path) -> list[tuple[Path, pydicom.Dataset]]:
    """Finds every DICOM file in `dicom_dir`:

    - `*.dcm` files, read directly (unchanged from before) - a malformed
      .dcm file still raises rather than being silently skipped.
    - extensionless files that are valid DICOM, detected by attempting to
      read them (see `_try_read_as_dicom`) rather than by filename. Files
      with any other extension are ignored, same as before.
    """
    dcm_paths = sorted(dicom_dir.glob("*.dcm"))
    loaded = [(path, pydicom.dcmread(path)) for path in dcm_paths]

    extensionless_paths = sorted(p for p in dicom_dir.iterdir() if p.is_file() and p.suffix == "")
    for path in extensionless_paths:
        dataset = _try_read_as_dicom(path)
        if dataset is not None:
            loaded.append((path, dataset))

    return loaded


def convert_study(dicom_dir: Path, output_dir: Path) -> int:
    """Converts every DICOM file in `dicom_dir` - `*.dcm`, plus extensionless
    files that are valid DICOM (see `_discover_dicom_files`) - into a
    sequentially-named, 16-bit HU-encoded PNG in `output_dir`
    (slice_000.png, slice_001.png, ...), ordered by InstanceNumber where
    available. Also writes window_default.json if the source DICOM carried
    its own WindowCenter/WindowWidth. Returns the number of slices written.

    Clears `output_dir` first so re-running conversion after fixing a
    source file doesn't leave stale slices (or a stale window default)
    behind.
    """
    loaded = _discover_dicom_files(dicom_dir)
    if not loaded:
        return 0

    loaded.sort(key=_sort_key)

    output_dir.mkdir(parents=True, exist_ok=True)
    for stale in output_dir.glob("slice_*.png"):
        stale.unlink()
    window_default_path = output_dir / WINDOW_DEFAULT_FILENAME
    window_default_path.unlink(missing_ok=True)

    dicom_window: WindowPreset | None = None
    for index, (_, dataset) in enumerate(loaded):
        hu = _slice_to_hu(dataset)
        encoded = encode_hu_to_uint16(hu)
        image = Image.fromarray(encoded, mode="I;16")
        image.save(output_dir / f"slice_{index:03d}.png")

        if dicom_window is None:
            # A DICOM series' WindowCenter/WindowWidth is normally constant
            # across slices - the first slice that has one wins.
            dicom_window = _dicom_window(dataset)

    if dicom_window is not None:
        window_default_path.write_text(
            json.dumps({"center": dicom_window.center, "width": dicom_window.width}),
            encoding="utf-8",
        )

    return len(loaded)
