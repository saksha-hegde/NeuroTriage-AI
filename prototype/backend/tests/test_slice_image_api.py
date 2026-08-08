"""Tests for GET /studies/{id}/slices/{index}, including window/level
preset selection (brain / blood / dicom)."""

import io
from pathlib import Path

import app.services.image_store as image_store
import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.services.windowing import encode_hu_to_uint16

client = TestClient(app)


def write_raw_slice(images_root: Path, study_id: str, hu_value: float) -> None:
    """Writes a single-pixel-value raw HU slice, mimicking what
    convert_study would produce."""
    study_dir = images_root / study_id
    study_dir.mkdir(parents=True, exist_ok=True)
    hu_array = np.full((4, 4), hu_value, dtype=np.float64)
    encoded = encode_hu_to_uint16(hu_array)
    Image.fromarray(encoded, mode="I;16").save(study_dir / "slice_000.png")


def response_pixel(response) -> int:
    image = Image.open(io.BytesIO(response.content))
    assert image.mode == "L"
    return int(np.array(image)[0, 0])


def test_404_for_unknown_study() -> None:
    response = client.get("/api/studies/does-not-exist/slices/0")
    assert response.status_code == 404


def test_404_for_out_of_range_slice_index() -> None:
    # Deliberately way past any plausible slice_count, real or seeded, so
    # this doesn't depend on whether STU-005's real DICOM has been
    # converted on this machine.
    response = client.get("/api/studies/STU-005/slices/999999")
    assert response.status_code == 404


def test_404_with_helpful_message_when_not_converted_yet(monkeypatch, tmp_path: Path) -> None:
    # Isolated from real converted images (which may or may not exist on
    # disk depending on whether this study's real DICOM has been converted
    # on this machine) via an empty IMAGES_ROOT.
    monkeypatch.setattr(image_store, "IMAGES_ROOT", tmp_path)
    response = client.get("/api/studies/STU-005/slices/0")
    assert response.status_code == 404
    assert "not available yet" in response.json()["detail"]


def test_returns_windowed_png_once_converted(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(image_store, "IMAGES_ROOT", tmp_path)
    write_raw_slice(tmp_path, "STU-005", hu_value=40)  # brain window center -> mid-gray

    response = client.get("/api/studies/STU-005/slices/0")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert 120 <= response_pixel(response) <= 135


def test_default_preset_is_brain(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(image_store, "IMAGES_ROOT", tmp_path)
    write_raw_slice(tmp_path, "STU-005", hu_value=40)

    no_preset = client.get("/api/studies/STU-005/slices/0")
    explicit_brain = client.get("/api/studies/STU-005/slices/0", params={"preset": "brain"})

    assert response_pixel(no_preset) == response_pixel(explicit_brain)


def test_blood_preset_differs_from_brain_for_high_hu(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(image_store, "IMAGES_ROOT", tmp_path)
    # HU 90: brain window (0-80 visible range) saturates to white; blood
    # window (0-100 visible range) does not - the two presets must diverge.
    write_raw_slice(tmp_path, "STU-005", hu_value=90)

    brain = client.get("/api/studies/STU-005/slices/0", params={"preset": "brain"})
    blood = client.get("/api/studies/STU-005/slices/0", params={"preset": "blood"})

    assert response_pixel(brain) == 255
    assert response_pixel(blood) < 255


def test_dicom_preset_uses_stored_window_default(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(image_store, "IMAGES_ROOT", tmp_path)
    write_raw_slice(tmp_path, "STU-005", hu_value=90)
    (tmp_path / "STU-005" / "window_default.json").write_text(
        '{"center": 50, "width": 100}', encoding="utf-8"
    )

    dicom_preset = client.get("/api/studies/STU-005/slices/0", params={"preset": "dicom"})
    blood_preset = client.get("/api/studies/STU-005/slices/0", params={"preset": "blood"})

    assert response_pixel(dicom_preset) == response_pixel(blood_preset)


def test_dicom_preset_falls_back_to_brain_without_sidecar(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(image_store, "IMAGES_ROOT", tmp_path)
    write_raw_slice(tmp_path, "STU-005", hu_value=40)
    # No window_default.json written - source DICOM had no WC/WW tags.

    dicom_preset = client.get("/api/studies/STU-005/slices/0", params={"preset": "dicom"})
    brain_preset = client.get("/api/studies/STU-005/slices/0", params={"preset": "brain"})

    assert response_pixel(dicom_preset) == response_pixel(brain_preset)


def test_invalid_preset_is_rejected(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(image_store, "IMAGES_ROOT", tmp_path)
    write_raw_slice(tmp_path, "STU-005", hu_value=40)

    response = client.get("/api/studies/STU-005/slices/0", params={"preset": "not-a-real-preset"})

    assert response.status_code == 422
