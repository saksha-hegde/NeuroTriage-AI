"""Tests for DICOM -> preserved-HU-data conversion, using small synthetic
(fabricated) DICOM datasets - no real patient data is needed or used here."""

import json
from pathlib import Path

import numpy as np
import pydicom
import pytest
from PIL import Image
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid

from app.services.dicom_conversion import WINDOW_DEFAULT_FILENAME, convert_study
from app.services.windowing import decode_uint16_to_hu

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


def read_hu(png_path: Path) -> np.ndarray:
    encoded = np.array(Image.open(png_path))
    return decode_uint16_to_hu(encoded)


class TestHounsfieldConversion:
    def test_applies_rescale_slope_and_intercept(self, tmp_path: Path) -> None:
        make_fake_dicom(
            tmp_path / "s1.dcm",
            stored_pixel_value=stored_value_for_hu(40, slope=2.0, intercept=-1024.0),
            rescale_slope=2.0,
            rescale_intercept=-1024.0,
        )
        out_dir = tmp_path / "out"

        count = convert_study(tmp_path, out_dir)

        assert count == 1
        hu = read_hu(out_dir / "slice_000.png")
        assert hu[0, 0] == pytest.approx(40.0, abs=0.5)

    def test_preserves_full_precision_no_baked_window(self, tmp_path: Path) -> None:
        # A value that would clip to black/white under the old brain window
        # (40/80 -> visible range 0..80) must still round-trip exactly, since
        # windowing is no longer applied at conversion time.
        make_fake_dicom(tmp_path / "s1.dcm", stored_pixel_value=stored_value_for_hu(500))
        out_dir = tmp_path / "out"

        convert_study(tmp_path, out_dir)

        hu = read_hu(out_dir / "slice_000.png")
        assert hu[0, 0] == pytest.approx(500.0, abs=0.5)


class TestWindowDefaultSidecar:
    def test_captures_dicom_window_center_and_width(self, tmp_path: Path) -> None:
        make_fake_dicom(
            tmp_path / "s1.dcm",
            stored_pixel_value=stored_value_for_hu(40),
            window_center=45.0,
            window_width=90.0,
        )
        out_dir = tmp_path / "out"

        convert_study(tmp_path, out_dir)

        sidecar = json.loads((out_dir / WINDOW_DEFAULT_FILENAME).read_text(encoding="utf-8"))
        assert sidecar == {"center": 45.0, "width": 90.0}

    def test_omitted_when_dicom_has_no_window_tags(self, tmp_path: Path) -> None:
        make_fake_dicom(
            tmp_path / "s1.dcm",
            stored_pixel_value=stored_value_for_hu(40),
            window_center=None,
            window_width=None,
        )
        out_dir = tmp_path / "out"

        convert_study(tmp_path, out_dir)

        assert not (out_dir / WINDOW_DEFAULT_FILENAME).exists()

    def test_rerun_clears_stale_sidecar(self, tmp_path: Path) -> None:
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        (out_dir / WINDOW_DEFAULT_FILENAME).write_text('{"center": 1, "width": 1}', encoding="utf-8")

        make_fake_dicom(
            tmp_path / "s1.dcm",
            stored_pixel_value=stored_value_for_hu(40),
            window_center=None,
            window_width=None,
        )
        convert_study(tmp_path, out_dir)

        assert not (out_dir / WINDOW_DEFAULT_FILENAME).exists()


class TestExtensionlessDicomDiscovery:
    def test_discovers_extensionless_valid_dicom(self, tmp_path: Path) -> None:
        # No ".dcm" suffix at all - mirrors a real scanner/PACS export that
        # dropped the extension.
        make_fake_dicom(tmp_path / "IM0001", stored_pixel_value=stored_value_for_hu(40))
        out_dir = tmp_path / "out"

        count = convert_study(tmp_path, out_dir)

        assert count == 1
        hu = read_hu(out_dir / "slice_000.png")
        assert hu[0, 0] == pytest.approx(40.0, abs=0.5)

    def test_mixes_dcm_and_extensionless_files_in_instance_order(self, tmp_path: Path) -> None:
        # Same series, one slice exported with the extension and one
        # without - both must be discovered and ordered correctly together.
        make_fake_dicom(tmp_path / "b.dcm", stored_pixel_value=stored_value_for_hu(40), instance_number=2)
        make_fake_dicom(tmp_path / "IM0001", stored_pixel_value=stored_value_for_hu(80), instance_number=1)
        out_dir = tmp_path / "out"

        count = convert_study(tmp_path, out_dir)

        assert count == 2
        first = read_hu(out_dir / "slice_000.png")[0, 0]
        second = read_hu(out_dir / "slice_001.png")[0, 0]
        assert first == pytest.approx(80.0, abs=0.5)  # instance 1 (extensionless)
        assert second == pytest.approx(40.0, abs=0.5)  # instance 2 (.dcm)

    def test_skips_non_dicom_extensionless_file_without_raising(self, tmp_path: Path) -> None:
        (tmp_path / "README").write_text("not a DICOM file", encoding="utf-8")
        make_fake_dicom(tmp_path / "a.dcm", stored_pixel_value=stored_value_for_hu(40), instance_number=1)
        out_dir = tmp_path / "out"

        count = convert_study(tmp_path, out_dir)

        # Only the real .dcm file was converted - the bogus extensionless
        # file was probed, found not to be DICOM, and quietly ignored.
        assert count == 1

    def test_ignores_files_with_other_extensions(self, tmp_path: Path) -> None:
        (tmp_path / "notes.txt").write_text("not a DICOM file", encoding="utf-8")
        make_fake_dicom(tmp_path / "a.dcm", stored_pixel_value=stored_value_for_hu(40), instance_number=1)
        out_dir = tmp_path / "out"

        count = convert_study(tmp_path, out_dir)

        assert count == 1

    def test_extensionless_only_directory_with_no_dicom_returns_zero(self, tmp_path: Path) -> None:
        (tmp_path / "README").write_text("not a DICOM file", encoding="utf-8")
        out_dir = tmp_path / "out"

        assert convert_study(tmp_path, out_dir) == 0


class TestSlicingAndOrdering:
    def test_orders_by_instance_number_not_filename(self, tmp_path: Path) -> None:
        # Filenames deliberately out of order vs. InstanceNumber.
        make_fake_dicom(tmp_path / "c.dcm", stored_pixel_value=stored_value_for_hu(0), instance_number=3)
        make_fake_dicom(tmp_path / "a.dcm", stored_pixel_value=stored_value_for_hu(80), instance_number=1)
        make_fake_dicom(tmp_path / "b.dcm", stored_pixel_value=stored_value_for_hu(40), instance_number=2)
        out_dir = tmp_path / "out"

        count = convert_study(tmp_path, out_dir)

        assert count == 3
        first = read_hu(out_dir / "slice_000.png")[0, 0]
        second = read_hu(out_dir / "slice_001.png")[0, 0]
        third = read_hu(out_dir / "slice_002.png")[0, 0]
        assert first == pytest.approx(80.0, abs=0.5)  # instance 1
        assert second == pytest.approx(40.0, abs=0.5)  # instance 2
        assert third == pytest.approx(0.0, abs=0.5)  # instance 3

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
def test_output_is_always_valid_16bit_grayscale(tmp_path: Path, hu: float) -> None:
    make_fake_dicom(tmp_path / "s1.dcm", stored_pixel_value=stored_value_for_hu(hu))
    out_dir = tmp_path / "out"

    convert_study(tmp_path, out_dir)

    image = Image.open(out_dir / "slice_000.png")
    assert image.mode == "I;16"
    assert image.size == (COLS, ROWS)
    array = np.array(image)
    assert array.dtype == np.uint16
    assert array.min() >= 0
    assert array.max() <= 65535
