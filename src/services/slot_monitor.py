"""Slot monitoring service for tracking availability in real-time."""

from datetime import datetime, date, time as time_type, timedelta
from typing import Optional, List, Dict, Any, Callable
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import threading
import time
import json
from .database import db_service, SlotAvailability

class SlotMonitorService:
    """Service for monitoring slot availability."""
    
    def __init__(self, poll_interval: int = 60):
        """Initialize slot monitor.
        
        Args:
            poll_interval: Seconds between polls (default: 60)
        """
        self.poll_interval = poll_interval
        self.is_monitoring = False
        self.monitor_thread = None
        self.callbacks: List[Callable] = []
        self.cache_ttl = 30  # Cache valid for 30 seconds
        
    def register_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Register callback for slot availability changes.
        
        Args:
            callback: Function to call when slots change
        """
        self.callbacks.append(callback)
        
    def _notify_callbacks(self, event_data: Dict[str, Any]):
        """Notify all registered callbacks."""
        for callback in self.callbacks:
            try:
                callback(event_data)
            except Exception as e:
                print(f"Error in callback: {e}")
    
    def scrape_slots(self, location: str, target_date: date, 
                    netid: str, password: str) -> List[Dict[str, Any]]:
        """Scrape available slots for a location and date.
        
        Args:
            location: 'Fitness', 'X1', or 'X3'
            target_date: Date to check
            netid: Account netid for authentication
            password: Account password
            
        Returns:
            List of slot dictionaries with availability info
        """
        from main import login_x, find_chrome_binary
        
        # Setup headless browser
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Set binary location
        chrome_binary = find_chrome_binary()
        if chrome_binary:
            chrome_options.binary_location = chrome_binary
            
        driver = None
        slots = []
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate and get slots
            success = login_x(
                driver=driver,
                netid=netid,
                password=password,
                target_date=target_date,
                selected_times=[],  # Don't book, just check
                retry_interval=0,
                location=location,
                headless=True
            )
            
            if not success:
                print(f"Failed to access booking page for {location}")
                return slots
            
            # Wait for time slots to load
            wait = WebDriverWait(driver, 10)
            time_container = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".time-slot-container, .booking-times"))
            )
            
            # Find all time slot elements
            slot_elements = driver.find_elements(By.CSS_SELECTOR, ".time-slot, .booking-time")
            
            for slot_elem in slot_elements:
                try:
                    # Extract time (format: "13:00" or "13:00 - 14:00")
                    time_text = slot_elem.find_element(By.CSS_SELECTOR, ".time-label, .time").text.strip()
                    if '-' in time_text:
                        time_text = time_text.split('-')[0].strip()
                    
                    # Check if slot is available (not disabled/booked)
                    is_available = True
                    classes = slot_elem.get_attribute('class') or ''
                    
                    if 'disabled' in classes or 'booked' in classes or 'unavailable' in classes:
                        is_available = False
                    
                    # Check for capacity info if available
                    capacity_text = None
                    try:
                        capacity_elem = slot_elem.find_element(By.CSS_SELECTOR, ".capacity, .spots-left")
                        capacity_text = capacity_elem.text.strip()
                    except NoSuchElementException:
                        pass
                    
                    # Parse capacity (e.g., "5 spots left" or "Full")
                    remaining = None
                    total = None
                    if capacity_text:
                        if 'full' in capacity_text.lower():
                            is_available = False
                            remaining = 0
                        elif 'spot' in capacity_text.lower():
                            # Extract number
                            import re
                            match = re.search(r'(\d+)', capacity_text)
                            if match:
                                remaining = int(match.group(1))
                                if remaining == 0:
                                    is_available = False
                    
                    # Parse time string to time object
                    try:
                        hour, minute = map(int, time_text.split(':'))
                        slot_time = time_type(hour, minute)
                    except ValueError:
                        continue
                    
                    slots.append({
                        'time': slot_time,
                        'time_str': time_text,
                        'is_available': is_available,
                        'total_capacity': total,
                        'remaining_capacity': remaining,
                        'location': location,
                        'date': target_date
                    })
                    
                except Exception as e:
                    print(f"Error parsing slot element: {e}")
                    continue
            
        except TimeoutException:
            print(f"Timeout waiting for time slots on {location}")
        except Exception as e:
            print(f"Error scraping slots: {e}")
        finally:
            if driver:
                driver.quit()
        
        return slots
    
    def update_slot_cache(self, location: str, target_date: date,
                         netid: str, password: str) -> List[SlotAvailability]:
        """Update cached slot availability.
        
        Args:
            location: Location to check
            target_date: Date to check
            netid: Account for authentication
            password: Account password
            
        Returns:
            List of updated SlotAvailability objects
        """
        # Scrape current availability
        slots = self.scrape_slots(location, target_date, netid, password)
        
        # Update database cache
        updated_slots = []
        for slot_data in slots:
            slot = db_service.update_slot_availability(
                location=slot_data['location'],
                booking_date=slot_data['date'],
                time_slot=slot_data['time'],
                is_available=slot_data['is_available'],
                total_capacity=slot_data['total_capacity'],
                remaining_capacity=slot_data['remaining_capacity']
            )
            if slot:
                updated_slots.append(slot)
        
        # Notify callbacks of update
        self._notify_callbacks({
            'type': 'slots_updated',
            'location': location,
            'date': target_date.isoformat(),
            'slots_count': len(updated_slots),
            'available_count': sum(1 for s in slots if s['is_available'])
        })
        
        return updated_slots
    
    def get_cached_availability(self, location: str, target_date: date,
                               time_range: Optional[tuple] = None,
                               force_refresh: bool = False) -> List[SlotAvailability]:
        """Get slot availability from cache or refresh if stale.
        
        Args:
            location: Location to check
            target_date: Date to check
            time_range: Optional (start_time, end_time) filter
            force_refresh: Force refresh even if cache is fresh
            
        Returns:
            List of SlotAvailability objects
        """
        # Check cache freshness
        slots = db_service.get_slot_availability(location, target_date)
        
        if not slots or force_refresh:
            # Cache miss or forced refresh - need credentials
            # For now, return empty list if no cache
            # In production, would use a dedicated monitoring account
            return []
        
        # Check if cache is stale
        now = datetime.utcnow()
        if slots and (now - slots[0].last_checked).total_seconds() > self.cache_ttl:
            # Cache is stale but we can't refresh without credentials
            # Return stale data with warning
            print(f"Warning: Slot cache is stale (>{self.cache_ttl}s old)")
        
        # Apply time range filter
        if time_range:
            start_time, end_time = time_range
            slots = [s for s in slots if start_time <= s.time_slot <= end_time]
        
        return slots
    
    def _monitor_loop(self, locations: List[str], date_range: int,
                     netid: str, password: str):
        """Background monitoring loop.
        
        Args:
            locations: List of locations to monitor
            date_range: Number of days ahead to monitor
            netid: Account for scraping
            password: Account password
        """
        print(f"🔍 Starting slot monitor (interval: {self.poll_interval}s)")
        
        while self.is_monitoring:
            try:
                today = date.today()
                
                for location in locations:
                    for day_offset in range(date_range):
                        check_date = today + timedelta(days=day_offset)
                        
                        print(f"Polling {location} for {check_date}...")
                        self.update_slot_cache(location, check_date, netid, password)
                        
                        # Small delay between locations
                        time.sleep(2)
                
                # Wait for next poll interval
                time.sleep(self.poll_interval)
                
            except Exception as e:
                print(f"Error in monitor loop: {e}")
                time.sleep(10)  # Wait before retry
        
        print("🛑 Slot monitor stopped")
    
    def start_monitoring(self, locations: List[str], date_range: int = 7,
                        netid: str = None, password: str = None):
        """Start background monitoring.
        
        Args:
            locations: List of locations to monitor ['Fitness', 'X1', 'X3']
            date_range: Number of days ahead to monitor (default: 7)
            netid: Account for scraping
            password: Account password
        """
        if self.is_monitoring:
            print("Monitor already running")
            return
        
        if not netid or not password:
            raise ValueError("netid and password required for monitoring")
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(locations, date_range, netid, password),
            daemon=True
        )
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop background monitoring."""
        if self.is_monitoring:
            self.is_monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            print("Monitor stopped")
    
    def get_available_slots(self, location: str, target_date: date,
                           time_window: Optional[tuple] = None,
                           consecutive_hours: int = 1) -> List[List[SlotAvailability]]:
        """Find available consecutive slots.
        
        Args:
            location: Location to check
            target_date: Date to check
            time_window: Optional (start_time, end_time) to search within
            consecutive_hours: Number of consecutive hours needed
            
        Returns:
            List of lists, each inner list is a consecutive slot sequence
        """
        # Get all available slots
        slots = self.get_cached_availability(location, target_date, time_window)
        available_slots = [s for s in slots if s.is_available]
        
        if consecutive_hours == 1:
            return [[slot] for slot in available_slots]
        
        # Find consecutive sequences
        consecutive_sequences = []
        
        for i in range(len(available_slots) - consecutive_hours + 1):
            sequence = [available_slots[i]]
            
            for j in range(1, consecutive_hours):
                next_slot = available_slots[i + j]
                prev_slot = sequence[-1]
                
                # Check if slots are consecutive (1 hour apart)
                time_diff = (
                    datetime.combine(date.min, next_slot.time_slot) -
                    datetime.combine(date.min, prev_slot.time_slot)
                ).total_seconds() / 3600
                
                if time_diff == 1.0:
                    sequence.append(next_slot)
                else:
                    break
            
            if len(sequence) == consecutive_hours:
                consecutive_sequences.append(sequence)
        
        return consecutive_sequences


# Global monitor instance
slot_monitor = SlotMonitorService()


if __name__ == "__main__":
    """Test slot monitoring."""
    from .database import db_service
    
    # Initialize database
    db_service.initialize_db()
    
    # Test scraping (requires valid credentials)
    print("Testing slot scraper...")
    print("Note: Requires valid TU Delft credentials")
    
    # Example: Test getting cached slots
    print("\nTesting cached availability...")
    from datetime import date
    slots = slot_monitor.get_cached_availability('X1', date(2025, 11, 17))
    print(f"Found {len(slots)} cached slots")
    
    # Example: Register callback
    def on_slots_updated(event):
        print(f"📢 Slots updated: {event}")
    
    slot_monitor.register_callback(on_slots_updated)
    
    print("\n✓ Slot monitor service ready")
    print("To start monitoring: slot_monitor.start_monitoring(['X1', 'X3'], netid='...', password='...')")
