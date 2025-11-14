"""
X Booking System Client
Handles direct interaction with the TU Delft X booking system.

NOTE: The X booking system uses OIDC/SSO authentication which is complex for direct HTTP requests.
This client is designed to work with Selenium WebDriver sessions that have already authenticated.
For a standalone test, use the Selenium-based main.py instead.
"""
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)


class BookingClient:
    """
    Client for interacting with TU Delft X booking system.
    
    Can work in two modes:
    1. With a Selenium WebDriver (recommended for authentication)
    2. With requests Session (if you have valid cookies)
    """
    
    BASE_URL = "https://x.tudelft.nl"
    
    def __init__(self, driver: Optional[webdriver.Chrome] = None):
        """
        Initialize the booking client.
        
        Args:
            driver: Optional Selenium WebDriver instance (already authenticated)
        """
        self.driver = driver
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.is_authenticated = False
        self.current_account = None
        
        # If driver provided, copy cookies to requests session
        if self.driver:
            self._sync_cookies_from_driver()

    def _sync_cookies_from_driver(self):
        """Copy cookies from Selenium driver to requests session"""
        if not self.driver:
            return
        
        try:
            for cookie in self.driver.get_cookies():
                self.session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))
            self.is_authenticated = True
            logger.info("Synced cookies from Selenium driver")
        except Exception as e:
            logger.error("Failed to sync cookies: %s", str(e))

    def login_with_selenium(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login using Selenium WebDriver (handles OIDC/SSO flow).
        This is the recommended way to authenticate with X booking system.
        
        Args:
            username: TU Delft NetID
            password: Account password
            
        Returns:
            Dict with success status and user info or error message
        """
        if not self.driver:
            return {
                "success": False,
                "error": "Selenium driver not initialized. Create client with: BookingClient(driver)"
            }
        
        try:
            logger.info("Attempting login for user: %s", username)
            
            # Navigate to X booking system
            self.driver.get(f"{self.BASE_URL}/dashboard")
            wait = WebDriverWait(self.driver, 10)
            
            # Check if already logged in
            current_url = self.driver.current_url
            if '/pages/login' not in current_url:
                try:
                    # Look for dashboard elements
                    self.driver.find_element(By.CSS_SELECTOR, "participations-table")
                    logger.info("Already authenticated")
                    self.is_authenticated = True
                    self._sync_cookies_from_driver()
                    return {
                        "success": True,
                        "user": {"username": username},
                        "message": "Already authenticated"
                    }
                except:
                    pass
            
            # Click TU Delft login button
            tu_button = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-test-id='oidc-login-button']")))
            tu_button.click()
            
            # Select TU Delft account
            tu_account = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div[data-title='Delft University of Technology']")))
            tu_account.click()
            
            # Enter credentials
            username_field = wait.until(EC.presence_of_element_located((By.ID, 'username')))
            password_field = self.driver.find_element(By.ID, 'password')
            
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            # Click login
            login_button = self.driver.find_element(By.ID, 'submit_button')
            login_button.click()
            
            # Wait for redirect
            wait.until(lambda d: 'x.tudelft.nl' in d.current_url and '/pages/login' not in d.current_url)
            
            # Sync cookies and mark as authenticated
            self._sync_cookies_from_driver()
            self.current_account = {"username": username}
            
            logger.info("Login successful for user: %s", username)
            return {
                "success": True,
                "user": self.current_account,
                "message": "Login successful"
            }
            
        except Exception as e:
            logger.error("Login error for user %s: %s", username, str(e))
            return {
                "success": False,
                "error": f"Login failed: {str(e)}"
            }

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login to X booking system.
        
        If Selenium driver is available, uses OIDC/SSO flow.
        Otherwise, returns error (direct HTTP auth not supported for OIDC).
        
        Args:
            username: Account username/NetID
            password: Account password
            
        Returns:
            Dict with success status and user info or error message
        """
        if self.driver:
            return self.login_with_selenium(username, password)
        else:
            return {
                "success": False,
                "error": "Direct HTTP login not supported. Use Selenium driver or provide authenticated session."
            }

    def logout(self) -> bool:
        """Logout from current session"""
        try:
            self.session.get(f"{self.BASE_URL}/api/auth/logout")
            self.is_authenticated = False
            self.current_account = None
            return True
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return False

    def get_available_slots(
        self, 
        location: str,
        date: str,  # YYYY-MM-DD
        sub_location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get available booking slots for a specific location and date.
        
        Args:
            location: 'Fitness', 'X1', or 'X3'
            date: Date in YYYY-MM-DD format
            sub_location: Optional 'A' or 'B' for X1/X3
            
        Returns:
            Dict with available slots and their details
        """
        if not self.is_authenticated:
            return {
                "success": False,
                "error": "Not authenticated. Please login first."
            }
        
        try:
            # Map location to product ID
            location_map = {
                "Fitness": "20061",
                "X1": "20045",
                "X3": "20047",
            }
            
            product_id = location_map.get(location)
            if not product_id:
                return {
                    "success": False,
                    "error": f"Invalid location: {location}"
                }
            
            # Get available slots
            params = {
                "productId": product_id,
                "date": date,
            }
            
            if sub_location and location in ["X1", "X3"]:
                # Add resource filter for sub-location
                resource_map = {
                    "X1": {"A": "4", "B": "5"},
                    "X3": {"A": "16534", "B": "16535"},
                }
                resource_id = resource_map[location].get(sub_location)
                if resource_id:
                    params["resourceId"] = resource_id
            
            response = self.session.get(
                f"{self.BASE_URL}/api/bookings/available",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse available slots
                available_slots = []
                for slot in data.get("slots", []):
                    available_slots.append({
                        "time": slot.get("startTime"),  # e.g., "06:00"
                        "end_time": slot.get("endTime"),  # e.g., "07:00"
                        "available": slot.get("availableSpots", 0),
                        "total": slot.get("totalSpots", 0),
                        "slot_id": slot.get("id"),
                        "resource_id": slot.get("resourceId"),
                    })
                
                logger.info(f"Found {len(available_slots)} available slots for {location} on {date}")
                return {
                    "success": True,
                    "location": location,
                    "sub_location": sub_location,
                    "date": date,
                    "slots": available_slots,
                    "count": len(available_slots)
                }
            else:
                logger.error(f"Failed to get available slots: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Failed to fetch available slots: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error getting available slots: {str(e)}")
            return {
                "success": False,
                "error": f"Error fetching slots: {str(e)}"
            }

    def get_current_bookings(self, include_past: bool = False) -> Dict[str, Any]:
        """
        Get all current bookings for the logged-in account.
        
        Args:
            include_past: If True, includes past bookings
            
        Returns:
            Dict with list of bookings
        """
        if not self.is_authenticated:
            return {
                "success": False,
                "error": "Not authenticated. Please login first."
            }
        
        try:
            params = {}
            if not include_past:
                # Only get upcoming bookings
                params["from"] = datetime.now().strftime("%Y-%m-%d")
            
            response = self.session.get(
                f"{self.BASE_URL}/api/bookings/my-bookings",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse bookings
                bookings = []
                for booking in data.get("bookings", []):
                    bookings.append({
                        "id": booking.get("id"),
                        "booking_id": booking.get("id"),  # External booking ID
                        "date": booking.get("startDate"),  # "2025-11-15"
                        "start_time": booking.get("startTime"),  # "13:00"
                        "end_time": booking.get("endTime"),  # "14:00"
                        "location": booking.get("productDescription"),  # "Fitness", "X1", "X3"
                        "sub_location": self._parse_sub_location(booking.get("productDescription")),  # "A" or "B"
                        "resource_id": booking.get("resourceId"),
                        "status": "confirmed",  # Bookings from API are confirmed
                        "can_cancel": booking.get("canCancel", False),
                        "participants": booking.get("participantAmount", 1),
                    })
                
                logger.info(f"Retrieved {len(bookings)} bookings")
                return {
                    "success": True,
                    "bookings": bookings,
                    "count": len(bookings)
                }
            else:
                logger.error(f"Failed to get bookings: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Failed to fetch bookings: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error getting bookings: {str(e)}")
            return {
                "success": False,
                "error": f"Error fetching bookings: {str(e)}"
            }

    def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        """
        Cancel a specific booking by its ID.
        
        Args:
            booking_id: The booking ID to cancel
            
        Returns:
            Dict with success status and message
        """
        if not self.is_authenticated:
            return {
                "success": False,
                "error": "Not authenticated. Please login first."
            }
        
        try:
            logger.info(f"Attempting to cancel booking: {booking_id}")
            
            response = self.session.delete(
                f"{self.BASE_URL}/api/bookings/{booking_id}"
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully cancelled booking: {booking_id}")
                return {
                    "success": True,
                    "message": "Booking cancelled successfully",
                    "booking_id": booking_id
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": "Booking not found"
                }
            elif response.status_code == 400:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                return {
                    "success": False,
                    "error": error_data.get("message", "Cannot cancel this booking")
                }
            else:
                logger.error(f"Failed to cancel booking: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Failed to cancel booking: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error cancelling booking: {str(e)}")
            return {
                "success": False,
                "error": f"Error cancelling booking: {str(e)}"
            }

    def create_booking(
        self,
        location: str,
        date: str,
        time_slot: str,  # e.g., "06:00"
        sub_location: Optional[str] = None,
        slot_id: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new booking for the specified slot.
        
        Args:
            location: 'Fitness', 'X1', or 'X3'
            date: Date in YYYY-MM-DD format
            time_slot: Time in HH:MM format
            sub_location: Optional 'A' or 'B' for X1/X3
            slot_id: The slot ID from available slots
            resource_id: The resource ID from available slots
            
        Returns:
            Dict with success status and booking details
        """
        if not self.is_authenticated:
            return {
                "success": False,
                "error": "Not authenticated. Please login first."
            }
        
        try:
            logger.info(f"Attempting to book {location} on {date} at {time_slot}")
            
            # Map location to product ID
            location_map = {
                "Fitness": "20061",
                "X1": "20045",
                "X3": "20047",
            }
            
            product_id = location_map.get(location)
            if not product_id:
                return {
                    "success": False,
                    "error": f"Invalid location: {location}"
                }
            
            # Prepare booking data
            booking_data = {
                "productId": product_id,
                "date": date,
                "startTime": time_slot,
                "participantAmount": 1,
            }
            
            if slot_id:
                booking_data["slotId"] = slot_id
            if resource_id:
                booking_data["resourceId"] = resource_id
            
            response = self.session.post(
                f"{self.BASE_URL}/api/bookings",
                json=booking_data
            )
            
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully created booking for {location} on {date} at {time_slot}")
                return {
                    "success": True,
                    "message": "Booking created successfully",
                    "booking": {
                        "id": data.get("id"),
                        "booking_id": data.get("id"),
                        "date": date,
                        "time": time_slot,
                        "location": location,
                        "sub_location": sub_location,
                    }
                }
            elif response.status_code == 409:
                return {
                    "success": False,
                    "error": "Slot already booked or no longer available"
                }
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                logger.error(f"Failed to create booking: {response.status_code}")
                return {
                    "success": False,
                    "error": error_data.get("message", f"Booking failed: {response.status_code}")
                }
                
        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}")
            return {
                "success": False,
                "error": f"Error creating booking: {str(e)}"
            }

    def _parse_sub_location(self, product_description: str) -> Optional[str]:
        """Parse sub-location (A or B) from product description"""
        if not product_description:
            return None
        
        # Check for "X1 A", "X1 B", "X3 A", "X3 B"
        if " A" in product_description:
            return "A"
        elif " B" in product_description:
            return "B"
        
        return None

    def is_logged_in(self) -> bool:
        """Check if currently authenticated"""
        return self.is_authenticated

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current logged-in user info"""
        return self.current_account
