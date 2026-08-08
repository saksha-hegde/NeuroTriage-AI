"""
CT window/level (windowing) - turns raw Hounsfield-unit pixel data into a
displayable 8-bit grayscale image.

Kept separate from dicom_conversion.py because windowing is now a *display*
concern applied per-request (see GET /studies/{id}/slices/{n} in
app/api/routes_studies.py), not a one-time conversion step - the raw HU data
survives conversion untouched (app/services/dicom_conversion.py) so the
window/level can change without ever re-touching the source DICOM.
"""

from dataclasses import dataclass
from typing import Literal

import numpy as np

# Offset applied when encoding/decoding HU values into a 16-bit PNG (which
# can only store non-negative integers). Realistic head-CT HU values run
# roughly -1024..+3000 (higher with metal/artifact) - this offset keeps all
# of that comfortably positive with full uint16 headroom to spare.
HU_ENCODING_OFFSET = 1024


@dataclass(frozen=True)
class WindowPreset:
    center: float
    width: float


# Standard "brain" (soft tissue) window - the conventional default view for
# CT Brain W/O Contrast, and this app's default preset.
BRAIN = WindowPreset(center=40.0, width=80.0)

# Wider/brighter window tuned for hemorrhage conspicuity - acute blood reads
# denser (higher HU) than surrounding brain tissue, so a slightly higher
# center/width than the brain window makes it easier to appreciate.
BLOOD = WindowPreset(center=50.0, width=100.0)

PresetName = Literal["brain", "blood", "dicom"]


def resolve_preset(name: PresetName, dicom_default: WindowPreset | None) -> WindowPreset:
    """Maps a requested preset name to the WindowPreset to actually apply.
    "dicom" means "use this study's own DICOM WindowCenter/WindowWidth" -
    falls back to the Brain preset if the source DICOM didn't carry one."""
    if name == "brain":
        return BRAIN
    if name == "blood":
        return BLOOD
    return dicom_default or BRAIN


def encode_hu_to_uint16(hu: np.ndarray) -> np.ndarray:
    """Raw Hounsfield-unit float array -> lossless uint16 for on-disk
    storage (PNG can't represent negative values or floats). Reversed by
    decode_uint16_to_hu."""
    shifted = np.clip(hu + HU_ENCODING_OFFSET, 0, 65535)
    return shifted.astype(np.uint16)


def decode_uint16_to_hu(encoded: np.ndarray) -> np.ndarray:
    """Inverse of encode_hu_to_uint16."""
    return encoded.astype(np.float64) - HU_ENCODING_OFFSET


def apply_window(hu: np.ndarray, preset: WindowPreset) -> np.ndarray:
    """Windows a raw HU array to 8-bit grayscale for display. Same
    normalize/clip/scale math the old bake-at-conversion-time step used
    (app/services/dicom_conversion.py, pre-windowing pipeline) - just now
    invoked per-request against preserved HU data instead of once against
    the source DICOM."""
    width = max(preset.width, 1.0)  # guard against a degenerate zero-width window
    low = preset.center - width / 2
    normalized = (hu - low) / width
    clipped = np.clip(normalized, 0.0, 1.0)
    return (clipped * 255).astype(np.uint8)
