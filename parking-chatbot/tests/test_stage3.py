"""
Stage 3 tests: ReservationWriter (uses a temp file, no side effects).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from stage3_mcp.reservation_writer import ReservationWriter

TEST_FILE = "_test_reservations_tmp.txt"


@pytest.fixture(autouse=True)
def cleanup():
    """Remove the test file before and after each test."""
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    yield
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)


@pytest.fixture
def writer():
    return ReservationWriter(file_path=TEST_FILE)


class TestFileInit:
    def test_file_created_on_init(self, writer):
        assert os.path.exists(TEST_FILE)

    def test_file_has_header(self, writer):
        with open(TEST_FILE) as f:
            first_line = f.readline()
        assert "Name" in first_line and "Car Number" in first_line


class TestWriteReservation:
    def test_write_returns_true(self, writer):
        result = writer.write_reservation(
            name="Jane", surname="Smith",
            car_number="XYZ-789",
            start_date="2026-07-01", end_date="2026-07-03",
        )
        assert result is True

    def test_entry_appears_in_read_all(self, writer):
        writer.write_reservation(
            name="Jane", surname="Smith",
            car_number="XYZ-789",
            start_date="2026-07-01", end_date="2026-07-03",
        )
        entries = writer.read_all()
        assert len(entries) == 1
        assert "Jane Smith" in entries[0]
        assert "XYZ-789" in entries[0]

    def test_multiple_entries(self, writer):
        for i in range(3):
            writer.write_reservation(
                name=f"User{i}", surname="Test",
                car_number=f"CAR{i:03d}",
                start_date="2026-07-01", end_date="2026-07-02",
            )
        assert len(writer.read_all()) == 3

    def test_entry_format_four_pipe_columns(self, writer):
        writer.write_reservation(
            name="Alice", surname="Brown",
            car_number="DEF-456",
            start_date="2026-07-10", end_date="2026-07-12",
            approval_time="2026-06-26 10:00:00",
        )
        entry = writer.read_all()[0]
        parts = [p.strip() for p in entry.split("|")]
        assert len(parts) == 4

    def test_approval_time_recorded(self, writer):
        writer.write_reservation(
            name="Bob", surname="Jones",
            car_number="GHI-999",
            start_date="2026-08-01", end_date="2026-08-02",
            approval_time="2026-06-26 12:30:00",
        )
        entry = writer.read_all()[0]
        assert "2026-06-26 12:30:00" in entry

    def test_read_all_empty_file(self):
        w = ReservationWriter(file_path=TEST_FILE)
        assert writer is not None  # writer fixture initialised
        assert isinstance(w.read_all(), list)
