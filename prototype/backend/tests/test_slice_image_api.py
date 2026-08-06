"""Tests for GET /studies/{id}/slices/{index}."""

from pathlib import Path

import app.services.image_store as image_store
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_404_for_unknown_study() -> None:
    response = client.get("/api/studies/does-not-exist/slices/0")
    assert response.status_code == 404


def test_404_for_out_of_range_slice_index() -> None:
    # STU-005 is seeded with slice_count = 31 (indices 0-30).
    response = client.get("/api/studies/STU-005/slices/31")
    assert response.status_code == 404


def test_404_with_helpful_message_when_not_converted_yet() -> None:
    # No images/ files exist for any seed study until real DICOM is
    # converted (Milestone 6's known current state).
    response = client.get("/api/studies/STU-005/slices/0")
    assert response.status_code == 404
    assert "not available yet" in response.json()["detail"]


def test_returns_image_bytes_once_converted(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(image_store, "IMAGES_ROOT", tmp_path)
    study_dir = tmp_path / "STU-005"
    study_dir.mkdir()
    fake_png_bytes = b"\x89PNG\r\n\x1a\nfake-slice-content"
    (study_dir / "slice_000.png").write_bytes(fake_png_bytes)

    response = client.get("/api/studies/STU-005/slices/0")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content == fake_png_bytes
