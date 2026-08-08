"""
One-time conversion step: real DICOM -> preserved-HU-data slices for the CT
viewer.

Usage (from backend/, with the venv active):

    python -m scripts.convert_dicom

What it expects:
    app/data/dicom_source/{study_id}/*.dcm   <- you place your files here
        e.g. app/data/dicom_source/STU-001/*.dcm
    Extensionless files are also picked up if they're valid DICOM - detected
    by attempting to read them, not by filename - since some scanner/PACS
    exports drop the .dcm extension. Files with any other extension are
    ignored.

What it produces:
    app/data/images/{study_id}/slice_000.png, slice_001.png, ... - 16-bit
        grayscale PNGs holding raw Hounsfield-unit data, NOT a pre-windowed
        8-bit image. Window/level (brain/blood/DICOM-default) is applied
        per-request by the API instead - see app/services/windowing.py -
        so it can change without ever re-running this script.
    app/data/images/{study_id}/window_default.json - the source DICOM's own
        WindowCenter/WindowWidth, if it had one.
    app/data/seed_studies.json - `slice_count` updated for each converted
        study, and any ICH overlay_region.slice_index clamped into bounds
        if the real slice count is smaller than the placeholder assumed.

Safe to re-run: each study's output folder is cleared and rewritten, and
the JSON patch only touches `slice_count` / `overlay_region.slice_index`
for studies that were actually converted - everything else is untouched.

What it does NOT do: pick which slice shows the hemorrhage, or where on
that slice. overlay_region's x/y/width/height are still the original
placeholder values - review the converted PNGs and adjust them by hand
(app/data/seed_studies.json) so the highlight lines up with what's actually
visible once real images are in place.
"""

import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.dicom_conversion import convert_study  # noqa: E402

DICOM_SOURCE_ROOT = BACKEND_ROOT / "app" / "data" / "dicom_source"
IMAGES_ROOT = BACKEND_ROOT / "app" / "data" / "images"
SEED_FILE = BACKEND_ROOT / "app" / "data" / "seed_studies.json"


def main() -> None:
    if not DICOM_SOURCE_ROOT.exists():
        print(f"No DICOM source folder found at {DICOM_SOURCE_ROOT}")
        print("Create it and add per-study subfolders, e.g.:")
        print(f"  {DICOM_SOURCE_ROOT / 'STU-001'}/*.dcm")
        return

    study_dirs = sorted(p for p in DICOM_SOURCE_ROOT.iterdir() if p.is_dir())
    if not study_dirs:
        print(f"{DICOM_SOURCE_ROOT} exists but has no study subfolders yet.")
        return

    converted: dict[str, int] = {}
    for study_dir in study_dirs:
        study_id = study_dir.name
        count = convert_study(study_dir, IMAGES_ROOT / study_id)
        if count == 0:
            print(f"  {study_id}: no .dcm files found, skipped")
            continue
        converted[study_id] = count
        print(f"  {study_id}: converted {count} slices -> {IMAGES_ROOT / study_id}")

    if not converted:
        print("Nothing converted.")
        return

    _patch_seed_file(converted)
    print(f"\nUpdated slice_count for {len(converted)} stud{'y' if len(converted) == 1 else 'ies'} in {SEED_FILE}")
    print(
        "Reminder: overlay_region coordinates are still placeholders - review "
        "the converted images and adjust x/y/width/height by hand for any "
        "Suspected ICH study so the highlight matches what's actually visible."
    )


def _patch_seed_file(converted: dict[str, int], seed_file: Path = SEED_FILE) -> None:
    if not seed_file.exists():
        print(f"Warning: {seed_file} not found, skipping slice_count update.")
        return

    studies = json.loads(seed_file.read_text(encoding="utf-8"))
    touched = False
    for study in studies:
        new_count = converted.get(study["id"])
        if new_count is None:
            continue

        study["slice_count"] = new_count
        touched = True

        prediction = study.get("prediction")
        overlay = prediction.get("overlay_region") if prediction else None
        if overlay is not None:
            overlay["slice_index"] = min(overlay["slice_index"], new_count - 1)

    if touched:
        seed_file.write_text(json.dumps(studies, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
