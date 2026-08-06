"""Tests for the seed-file-patching half of scripts/convert_dicom.py (the
conversion itself is covered by test_dicom_conversion.py)."""

import json
from pathlib import Path

from scripts.convert_dicom import _patch_seed_file


def make_seed_file(tmp_path: Path) -> Path:
    seed_file = tmp_path / "seed_studies.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "id": "STU-001",
                    "slice_count": 30,
                    "prediction": {
                        "assessment": "Suspected ICH",
                        "overlay_region": {"slice_index": 16, "x": 0.5, "y": 0.5, "width": 0.1, "height": 0.1},
                    },
                },
                {
                    "id": "STU-004",
                    "slice_count": 29,
                    "prediction": {
                        "assessment": "No Suspicious Findings",
                        "overlay_region": None,
                    },
                },
            ]
        ),
        encoding="utf-8",
    )
    return seed_file


def test_updates_slice_count_for_converted_studies(tmp_path: Path) -> None:
    seed_file = make_seed_file(tmp_path)

    _patch_seed_file({"STU-001": 12}, seed_file=seed_file)

    studies = json.loads(seed_file.read_text(encoding="utf-8"))
    stu_001 = next(s for s in studies if s["id"] == "STU-001")
    assert stu_001["slice_count"] == 12


def test_leaves_unconverted_studies_untouched(tmp_path: Path) -> None:
    seed_file = make_seed_file(tmp_path)

    _patch_seed_file({"STU-001": 12}, seed_file=seed_file)

    studies = json.loads(seed_file.read_text(encoding="utf-8"))
    stu_004 = next(s for s in studies if s["id"] == "STU-004")
    assert stu_004["slice_count"] == 29  # unchanged


def test_clamps_overlay_slice_index_into_new_bounds(tmp_path: Path) -> None:
    seed_file = make_seed_file(tmp_path)

    # Real conversion only produced 10 slices - the placeholder overlay
    # pointed at slice 16, which no longer exists.
    _patch_seed_file({"STU-001": 10}, seed_file=seed_file)

    studies = json.loads(seed_file.read_text(encoding="utf-8"))
    stu_001 = next(s for s in studies if s["id"] == "STU-001")
    assert stu_001["prediction"]["overlay_region"]["slice_index"] == 9


def test_does_not_touch_seed_file_when_nothing_converted(tmp_path: Path) -> None:
    seed_file = make_seed_file(tmp_path)
    original_text = seed_file.read_text(encoding="utf-8")

    _patch_seed_file({}, seed_file=seed_file)

    assert seed_file.read_text(encoding="utf-8") == original_text


def test_missing_seed_file_does_not_raise(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.json"
    _patch_seed_file({"STU-001": 5}, seed_file=missing)  # should not raise
