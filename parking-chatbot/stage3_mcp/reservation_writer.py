import os
import threading
from datetime import datetime
from typing import Optional

RESERVATIONS_FILE = "confirmed_reservations.txt"
HEADER = "Name | Car Number | Reservation Period | Approval Time"
SEPARATOR = "-" * 72

# Module-level lock ensures thread-safe writes within the same process
_write_lock = threading.Lock()


class ReservationWriter:
    """
    MCP-style server (Stage 3) that writes confirmed reservations to a text file.

    File entry format:
        Name | Car Number | Reservation Period | Approval Time

    Features:
    - Creates the file with a header on first use.
    - Thread-safe writes via a module-level lock.
    - read_all() returns all data entries (skips header lines).
    """

    def __init__(self, file_path: str = RESERVATIONS_FILE):
        self.file_path = file_path
        self._init_file()

    def _init_file(self):
        """Create the file with a header row if it does not exist."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(HEADER + "\n")
                f.write(SEPARATOR + "\n")

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def write_reservation(
        self,
        name: str,
        surname: str,
        car_number: str,
        start_date: str,
        end_date: str,
        approval_time: Optional[str] = None,
    ) -> bool:
        """
        Append one confirmed reservation to the file.

        Args:
            name, surname     : Customer name
            car_number        : Vehicle registration plate
            start_date        : Reservation start (YYYY-MM-DD)
            end_date          : Reservation end   (YYYY-MM-DD)
            approval_time     : ISO timestamp; defaults to now

        Returns:
            True on success, False on error.
        """
        if approval_time is None:
            approval_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        full_name = f"{name} {surname}"
        period = f"{start_date} to {end_date}"
        entry = f"{full_name} | {car_number} | {period} | {approval_time}\n"

        try:
            with _write_lock:
                with open(self.file_path, "a", encoding="utf-8") as f:
                    f.write(entry)
            print(f"[ReservationWriter] Written: {entry.strip()}")
            return True
        except OSError as exc:
            print(f"[ReservationWriter] Error writing reservation: {exc}")
            return False

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def read_all(self) -> list:
        """Return all confirmed reservation entries (skips the 2-line header)."""
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Skip header row and separator row
        return [line.strip() for line in lines[2:] if line.strip()]
