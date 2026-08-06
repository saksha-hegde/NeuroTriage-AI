"""
Locates converted CT slice images on disk.

Deliberately just a filesystem lookup - scripts/convert_dicom.py (backed by
app/services/dicom_conversion.py) already did the real work of turning raw
DICOM into plain, sequentially-numbered PNGs. This module is the read side
of that seam: routes ask it for a path, it doesn't know or care that the
source was ever DICOM.
"""

from pathlib import Path

IMAGES_ROOT = Path(__file__).resolve().parent.parent / "data" / "images"


def get_slice_path(study_id: str, slice_index: int) -> Path | None:
    """Returns the PNG path for a study's slice, or None if it hasn't been
    converted/placed yet (e.g. real images not added for this study, or a
    simulated study that was never converted)."""
    path = IMAGES_ROOT / study_id / f"slice_{slice_index:03d}.png"
    return path if path.is_file() else None
