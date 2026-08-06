"""Tests for DICOM -> PNG conversion, using small synthetic (fabricated)
DICOM datasets - no real patient data is needed or used here."""

from pathlib import Path

import numpy as np
import pydicom
import pytest
from PIL import Image
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid

from app.services.dicom_conversion import convert_study

ROWS, COLS = 8, 8


def make_fake_dicom(
    path: Path,
    *,
    stored_pixel_value: int,
    instance_number: int | None = None,
    rescale_slope: float = 1.0,
    rescale_intercept: float = -1024.0,
    window_center: float | None = 40.0,
    window_width: float | None = 80.0,
) -> None:
    """Writes a minimal-but-valid single-slice CT DICOM file to `path`."""
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.CTImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = FileDataset(str(path), {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.SOPClassUID = pydicom.uid.CTImageStorage
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.Modality = "CT"
    ds.Rows = ROWS
    ds.Columns = COLS
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 1  # signed
    ds.RescaleSlope = rescale_slope
    ds.RescaleIntercept = rescale_intercept
    if window_center is not None:
        ds.WindowCenter = window_center
    if window_width is not None:
        ds.WindowWidth = window_width
    if instance_number is not None:
        ds.InstanceNumber = instance_number

    pixels = np.full((ROWS, COLS), stored_pixel_value, dtype=np.int16)
    ds.PixelData = pixels.tobytes()

    ds.save_as(str(path), enforce_file_format=True, little_endian=True, implicit_vr=False)


def stored_value_for_hu(hu: float, slope: float = 1.0, intercept: float = -1024.0) -> int:
    return round((hu - intercept) / slope)


class TestWindowing:
    def test_center_of_window_maps_to_mid_gray(self, tmp_path: Path) -> None:
        # HU = window center (40) -> normalized 0.5 -> ~127
        make_fake_dicom(tmp_path / "s1.dcm", stored_pixel_value=stored_value_for_hu(40))
        out_dir = tmp_path / "out"

        count = convert_study(tmp_path, out_dir)

        assert count == 1
        image = Image.open(out_dir / "slice_000.png")
        pixel = np.array(image)[0, 0]
        assert 120 <= pixel <= 135

    def test_below_window_clips_to_black(self, tmp_path: Path) -> None:
        # HU well below (center - width/2) = 0 -> should clip to 0
        make_fake_dicom(tmp_path / "s1.dcm", stored_pixel_value=stored_value_for_hu(-500))
        out_dir = tmp_path / "out"

        convert_study(tmp_path, out_dir)

        pixel = np.array(Image.open(out_dir / "slice_000.png"))[0, 0]
        assert pixel == 0

    def test_above_window_clips_to_white(self, tmp_path: Path) -> None:
        # HU well above (center + width/2) = 80 -> should clip to 255
        make_fake_dicom(tmp_path / "s1.dcm", stored_pixel_value=stored_value_for_hu(500))
        out_dir = tmp_path / "out"

        convert_study(tmp_path, out_dir)

        pixel = np.array(Image.open(out_dir / "slice_000.png"))[0, 0]
        assert pixel == 255

    def test_falls_back_to_default_brain_window_when_absent(self, tmp_path: Path) -> None:
        make_fake_dicom(
            tmp_path / "s1.dcm",
            stored_pixel_value=stored_value_for_hu(40),
            window_center=None,
            window_width=None,
        )
        out_dir = tmp_path / "out"

        convert_study(tmp_path, out_dir)

        pixel = np.array(Image.open(out_dir / "slice_000.png"))[0, 0]
        assert 120 <= pixel <= 135  # same expectation as the explicit-window case


class TestSlicingAndOrdering:
    def test_orders_by_instance_number_not_filename(self, tmp_path: Path) -> None:
        # Filenames deliberately out of order vs. InstanceNumber.
        make_fake_dicom(tmp_path / "c.dcm", stored_pixel_value=stored_value_for_hu(0), instance_number=3)
        make_fake_dicom(tmp_path / "a.dcm", stored_pixel_value=stored_value_for_hu(80), instance_number=1)
        make_fake_dicom(tmp_path / "b.dcm", stored_pixel_value=stored_value_for_hu(40), instance_number=2)
        out_dir = tmp_path / "out"

        count = convert_study(tmp_path, out_dir)

        assert count == 3
        first = np.array(Image.open(out_dir / "slice_000.png"))[0, 0]
        second = np.array(Image.open(out_dir / "slice_001.png"))[0, 0]
        third = np.array(Image.open(out_dir / "slice_002.png"))[0, 0]
        assert first == 255  # instance 1 -> HU 80 -> white
        assert 120 <= second <= 135  # instance 2 -> HU 40 -> mid-gray
        assert third == 0  # instance 3 -> HU 0 -> black

    def test_returns_zero_for_empty_directory(self, tmp_path: Path) -> None:
        out_dir = tmp_path / "out"
        assert convert_study(tmp_path, out_dir) == 0

    def test_rerun_clears_stale_slices(self, tmp_path: Path) -> None:
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        (out_dir / "slice_000.png").write_bytes(b"stale")
        (out_dir / "slice_001.png").write_bytes(b"stale")

        make_fake_dicom(tmp_path / "s1.dcm", stored_pixel_value=stored_value_for_hu(40), instance_number=1)
        count = convert_study(tmp_path, out_dir)

        assert count == 1
        remaining = sorted(out_dir.glob("slice_*.png"))
        assert len(remaining) == 1
        assert remaining[0].name == "slice_000.png"


@pytest.mark.parametrize("hu", [-1024, 0, 40, 80, 3000])
def test_output_is_always_valid_8bit_grayscale(tmp_path: Path, hu: float) -> None:
    make_fake_dicom(tmp_path / "s1.dcm", stored_pixel_value=stored_value_for_hu(hu))
    out_dir = tmp_path / "out"

    convert_study(tmp_path, out_dir)

    image = Image.open(out_dir / "slice_000.png")
    assert image.mode == "L"
    assert image.size == (COLS, ROWS)
    array = np.array(image)
    assert array.dtype == np.uint8
    assert array.min() >= 0
    assert array.max() <= 255
