from datetime import datetime


class AdminAgent:
    """
    Human-in-the-Loop agent (Stage 2).

    Presents a reservation request to the administrator via the console
    and returns their approve / reject decision.

    In a production system this would send an email, Slack message, or
    REST API call. For this project the console is the communication channel.
    """

    def request_approval(self, reservation: dict) -> tuple[bool, str]:
        """
        Display the reservation details and prompt the admin for a decision.

        Args:
            reservation: dict with keys name, surname, car_number,
                         start_date, end_date

        Returns:
            (approved: bool, admin_note: str)
        """
        print("\n" + "=" * 60)
        print("  ADMIN APPROVAL REQUIRED")
        print("=" * 60)
        print(f"  Name       : {reservation.get('name', '')} {reservation.get('surname', '')}")
        print(f"  Car Number : {reservation.get('car_number', '')}")
        print(f"  Start Date : {reservation.get('start_date', '')}")
        print(f"  End Date   : {reservation.get('end_date', '')}")
        print("=" * 60)

        while True:
            try:
                decision = input("Decision (approve / reject): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n[AdminAgent] Input interrupted. Defaulting to reject.")
                return False, "Input interrupted"

            if decision in ("approve", "a", "yes"):
                note = input("Note for user (press Enter to skip): ").strip()
                print("[AdminAgent] Reservation APPROVED.")
                return True, note or "Approved"

            elif decision in ("reject", "r", "no"):
                note = input("Reason for rejection: ").strip()
                print("[AdminAgent] Reservation REJECTED.")
                return False, note or "Rejected by administrator"

            else:
                print("Please enter 'approve' or 'reject'.")

    def format_user_message(self, reservation: dict, approved: bool, note: str) -> str:
        """
        Generate the confirmation/rejection message shown to the end user.
        """
        status = "APPROVED" if approved else "REJECTED"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if approved:
            return (
                f"Your reservation has been {status}!\n"
                f"  Car     : {reservation.get('car_number', '')}\n"
                f"  Period  : {reservation.get('start_date', '')} "
                f"to {reservation.get('end_date', '')}\n"
                f"  Time    : {timestamp}\n"
                f"  Note    : {note}"
            )
        return (
            f"Your reservation has been {status}.\n"
            f"  Reason  : {note}\n"
            f"Please contact us for further assistance."
        )
