"""
Booking Service Module
Handles all booking-related operations including CRUD and booking execution.
"""
from typing import List, Dict, Optional, Any
from datetime import date as date_type
from src.services.database import DatabaseService


class BookingService:
    """Service for managing booking operations"""

    def __init__(self, db_service: DatabaseService):
        self.db = db_service

    def create_booking(
        self,
        account_id: int,
        booking_date: str,  # 'YYYY-MM-DD'
        time_slots: List[str],  # ['06:00', '07:00']
        location: str,
        sub_location: Optional[str] = None,
        retry_interval: int = 60,  # For future scheduler integration
        auto_retry: bool = False,  # For future scheduler integration
    ) -> List[Dict[str, Any]]:
        """
        Create new booking(s) for the specified time slots.
        Returns a list of created booking records.
        """
        created_bookings = []

        for time_slot in time_slots:
            # Create booking record with pending status
            booking_data = {
                "account_id": account_id,
                "booking_date": booking_date,
                "time_slot": f"{time_slot}:00",  # Ensure HH:MM:SS format
                "location": location,
                "sub_location": sub_location,
                "status": "pending",
                "booking_reference": None,
                "error_message": None,
            }

            booking = self.db.create_booking(booking_data)
            created_bookings.append(booking)

            # Log the booking creation
            self.db.log_booking_event(
                booking_id=booking["id"],
                event_type="created",
                message=f"Booking created for {location} on {booking_date} at {time_slot}",
            )

        return created_bookings

    def get_bookings(
        self,
        account_id: Optional[int] = None,
        date: Optional[str] = None,
        status: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all bookings with optional filters.
        """
        filters = {}

        if account_id is not None:
            filters["account_id"] = account_id
        if date:
            filters["booking_date"] = date
        if status:
            filters["status"] = status
        if location:
            filters["location"] = location

        bookings = self.db.get_bookings(**filters)
        return bookings

    def get_booking(self, booking_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific booking by ID.
        """
        booking = self.db.get_booking(booking_id)
        return booking

    def update_booking(
        self,
        booking_id: int,
        status: Optional[str] = None,
        booking_reference: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Update a booking's status and related fields.
        """
        updates = {}

        if status:
            updates["status"] = status
        if booking_reference is not None:
            updates["booking_reference"] = booking_reference
        if error_message is not None:
            updates["error_message"] = error_message

        if not updates:
            return None

        booking = self.db.update_booking(booking_id, updates)

        if booking:
            # Log the status change
            event_type = "status_change" if status else "update"
            message = f"Booking updated: {', '.join(f'{k}={v}' for k, v in updates.items())}"
            self.db.log_booking_event(
                booking_id=booking_id, event_type=event_type, message=message
            )

        return booking

    def cancel_booking(self, booking_id: int) -> bool:
        """
        Cancel a booking (set status to 'cancelled').
        Returns True if successful, False otherwise.
        """
        booking = self.db.get_booking(booking_id)

        if not booking:
            return False

        # Only allow cancelling confirmed or pending bookings
        if booking["status"] not in ["pending", "confirmed"]:
            return False

        updated = self.db.update_booking(booking_id, {"status": "cancelled"})

        if updated:
            # Log the cancellation
            self.db.log_booking_event(
                booking_id=booking_id,
                event_type="cancelled",
                message="Booking cancelled by user",
            )
            return True

        return False

    def mark_booking_confirmed(
        self, booking_id: int, booking_reference: str
    ) -> Optional[Dict[str, Any]]:
        """
        Mark a booking as confirmed with a reference number.
        """
        return self.update_booking(
            booking_id=booking_id,
            status="confirmed",
            booking_reference=booking_reference,
            error_message=None,  # Clear any previous error
        )

    def mark_booking_failed(
        self, booking_id: int, error_message: str
    ) -> Optional[Dict[str, Any]]:
        """
        Mark a booking as failed with an error message.
        """
        return self.update_booking(
            booking_id=booking_id, status="failed", error_message=error_message
        )

    def get_account_bookings(
        self, account_id: int, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all bookings for a specific account.
        """
        filters = {"account_id": account_id}
        if status:
            filters["status"] = status

        return self.db.get_bookings(**filters)

    def get_booking_logs(self, booking_id: int) -> List[Dict[str, Any]]:
        """
        Get all log entries for a specific booking.
        """
        return self.db.get_booking_logs(booking_id)

    def get_upcoming_bookings(
        self, account_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all upcoming bookings (today or later, not cancelled/failed).
        """
        today = date_type.today().isoformat()
        all_bookings = self.get_bookings(account_id=account_id)

        # Filter for upcoming bookings that are pending or confirmed
        upcoming = [
            b
            for b in all_bookings
            if b["booking_date"] >= today and b["status"] in ["pending", "confirmed"]
        ]

        # Sort by date and time
        upcoming.sort(key=lambda x: (x["booking_date"], x["time_slot"]))

        return upcoming

    def get_booking_statistics(self, account_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get booking statistics for an account or all accounts.
        """
        filters = {}
        if account_id is not None:
            filters["account_id"] = account_id

        all_bookings = self.db.get_bookings(**filters)

        stats = {
            "total": len(all_bookings),
            "pending": sum(1 for b in all_bookings if b["status"] == "pending"),
            "confirmed": sum(1 for b in all_bookings if b["status"] == "confirmed"),
            "failed": sum(1 for b in all_bookings if b["status"] == "failed"),
            "cancelled": sum(1 for b in all_bookings if b["status"] == "cancelled"),
        }

        # Calculate success rate (confirmed / (confirmed + failed))
        total_attempts = stats["confirmed"] + stats["failed"]
        stats["success_rate"] = (
            round((stats["confirmed"] / total_attempts) * 100, 1)
            if total_attempts > 0
            else 0.0
        )

        return stats
