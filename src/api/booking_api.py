"""
Python Booking API Bridge
This module will be integrated into main.py to handle booking operations
from the Next.js frontend via HTTP requests.

NOTE: This is a placeholder for Phase 5.5. The actual implementation
will be integrated with the existing Python backend structure.

For now, the booking operations are exposed through the BookingService
class which can be called directly or via an HTTP bridge.
"""
from typing import Dict, Any

from src.services.database import DatabaseService
from src.services.booking_service import BookingService


def handle_booking_request(data: Dict[str, Any]) -> tuple[Dict[str, Any], int]:
    """
    Main handler for booking operations.
    Returns (response_dict, status_code)
    
    Expected data structure:
    {
        "action": "create_booking" | "get_bookings" | "get_booking" | "update_booking" | "cancel_booking",
        ... other fields depending on action
    }
    """
    try:
        # Initialize services
        db_service = DatabaseService()
        booking_service = BookingService(db_service)
        
        action = data.get("action")

        if action == "create_booking":
            return create_booking(data, db_service, booking_service)
        elif action == "get_bookings":
            return get_bookings(data, booking_service)
        elif action == "get_booking":
            return get_booking(data, booking_service)
        elif action == "update_booking":
            return update_booking(data, booking_service)
        elif action == "cancel_booking":
            return cancel_booking(data, booking_service)
        else:
            return {"error": f"Unknown action: {action}"}, 400

    except Exception as e:
        return {"error": str(e)}, 500


def create_booking(data: Dict[str, Any], db_service: DatabaseService, booking_service: BookingService) -> tuple[Dict[str, Any], int]:
    """Handle booking creation"""
    account_id = data.get("account_id")
    booking_date = data.get("booking_date")
    time_slots = data.get("time_slots", [])
    location = data.get("location")
    sub_location = data.get("sub_location")
    retry_interval = data.get("retry_interval", 60)
    auto_retry = data.get("auto_retry", False)

    # Validation
    if not all([account_id, booking_date, time_slots, location]):
        return {
            "error": "Missing required fields: account_id, booking_date, time_slots, location"
        }, 400

    # Check if account exists
    account = db_service.get_account_by_id(account_id)
    if not account:
        return {"error": f"Account with ID {account_id} not found"}, 404

    # Create bookings
    bookings = booking_service.create_booking(
        account_id=account_id,
        booking_date=booking_date,
        time_slots=time_slots,
        location=location,
        sub_location=sub_location,
        retry_interval=retry_interval,
        auto_retry=auto_retry,
    )

    return {"success": True, "bookings": bookings}, 201


def get_bookings(data: Dict[str, Any], booking_service: BookingService) -> tuple[Dict[str, Any], int]:
    """Handle getting bookings with filters"""
    account_id = data.get("account_id")
    date = data.get("date")
    status = data.get("status")
    location = data.get("location")

    bookings = booking_service.get_bookings(
        account_id=account_id, date=date, status=status, location=location
    )

    return {"success": True, "bookings": bookings}, 200


def get_booking(data: Dict[str, Any], booking_service: BookingService) -> tuple[Dict[str, Any], int]:
    """Handle getting a single booking"""
    booking_id = data.get("booking_id")

    if not booking_id:
        return {"error": "booking_id is required"}, 400

    booking = booking_service.get_booking(booking_id)

    if not booking:
        return {"error": f"Booking with ID {booking_id} not found"}, 404

    return {"success": True, "booking": booking}, 200


def update_booking(data: Dict[str, Any], booking_service: BookingService) -> tuple[Dict[str, Any], int]:
    """Handle updating a booking"""
    booking_id = data.get("booking_id")
    status = data.get("status")
    booking_reference = data.get("booking_reference")
    error_message = data.get("error_message")

    if not booking_id:
        return {"error": "booking_id is required"}, 400

    booking = booking_service.update_booking(
        booking_id=booking_id,
        status=status,
        booking_reference=booking_reference,
        error_message=error_message,
    )

    if not booking:
        return {"error": "Booking not found or no updates provided"}, 404

    return {"success": True, "booking": booking}, 200


def cancel_booking(data: Dict[str, Any], booking_service: BookingService) -> tuple[Dict[str, Any], int]:
    """Handle cancelling a booking"""
    booking_id = data.get("booking_id")

    if not booking_id:
        return {"error": "booking_id is required"}, 400

    success = booking_service.cancel_booking(booking_id)

    if not success:
        return {
            "error": "Booking not found or cannot be cancelled (already completed/failed)"
        }, 400

    return {"success": True, "message": "Booking cancelled"}, 200

