"""
Locates and loads converted CT slice data on disk.

Deliberately just a filesystem read side - scripts/convert_dicom.py (backed
by app/services/dicom_conversion.py) already did the real work of turning
raw DICOM into per-slice, lossless HU-encoded PNGs plus each study's DICOM
window default (if any). This module's job is to hand that data back to
callers (routes ask it for HU pixel data / a window default, they don't know
or care that the source was ever DICOM); app/services/windowing.py then
turns HU data into a displayable image at request time.
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image

from app.services.dicom_conversion import WINDOW_DEFAULT_FILENAME
from app.services.windowing import WindowPreset, decode_uint16_to_hu

IMAGES_ROOT = Path(__file__).resolve().parent.parent / "data" / "images"


def get_raw_slice_hu(study_id: str, slice_index: int) -> np.ndarray | None:
    """Returns a study's slice as a raw Hounsfield-unit array, or None if it
    hasn't been converted/placed yet (e.g. real images not added for this
    study, or a simulated study that was never converted)."""
    path = IMAGES_ROOT / study_id / f"slice_{slice_index:03d}.png"
    if not path.is_file():
        return None
    encoded = np.array(Image.open(path))
    return decode_uint16_to_hu(encoded)


def get_dicom_default_window(study_id: str) -> WindowPreset | None:
    """The study's own DICOM WindowCenter/WindowWidth, if conversion found
    one - used by the "dicom" preset. None if the study hasn't been
    converted, or its source DICOM carried neither tag."""
    path = IMAGES_ROOT / study_id / WINDOW_DEFAULT_FILENAME
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return WindowPreset(center=data["center"], width=data["width"])
