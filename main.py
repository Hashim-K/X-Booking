import os
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import subprocess
import shutil
import platform
import traceback

import numpy as np

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import argparse
import sys


def find_chrome_binary():
    """
    Detect the best available Chrome/Chromium browser across platforms.
    Priority: Default browser → Brave → Chrome → Chromium → Flatpak browsers
    
    Returns:
        str: Path to the browser binary, or None if not found
    """
    system = platform.system()
    
    # Linux
    if system == "Linux":
        # Try to get default browser using xdg-settings
        try:
            result = subprocess.run(
                ["xdg-settings", "get", "default-web-browser"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                default_browser = result.stdout.strip().lower()
                
                # Map .desktop files to binaries
                browser_map = {
                    "brave-browser.desktop": ("brave-browser", "Brave"),
                    "brave.desktop": ("brave-browser", "Brave"),
                    "chromium-browser.desktop": ("chromium-browser", "Chromium"),
                    "chromium.desktop": ("chromium-browser", "Chromium"),
                    "google-chrome.desktop": ("google-chrome", "Google Chrome"),
                }
                
                if default_browser in browser_map:
                    binary, name = browser_map[default_browser]
                    path = shutil.which(binary)
                    if path:
                        print(f"Using default browser: {name} ({path})")
                        return path
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Fallback chain for Linux
        browsers = [
            ("brave-browser", "Brave"),
            ("brave", "Brave"),
            ("chromium-browser", "Chromium"),
            ("chromium", "Chromium"),
            ("google-chrome", "Google Chrome"),
        ]
        
        for binary, name in browsers:
            # Check if it's an absolute path
            if os.path.isabs(binary):
                if os.path.exists(binary):
                    print(f"Using {name} ({binary})")
                    return binary
            else:
                path = shutil.which(binary)
                if path:
                    print(f"Using {name} ({path})")
                    return path
        
        # Check Flatpak browsers
        try:
            result = subprocess.run(
                ["flatpak", "list", "--app", "--columns=application"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                flatpak_browsers = {
                    "com.brave.Browser": "Brave (Flatpak)",
                    "com.google.Chrome": "Google Chrome (Flatpak)",
                    "org.chromium.Chromium": "Chromium (Flatpak)",
                }
                for app_id, name in flatpak_browsers.items():
                    if app_id in result.stdout:
                        print(f"Using {name}")
                        return f"flatpak run {app_id}"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    
    # macOS
    elif system == "Darwin":
        # Try to get default browser
        try:
            result = subprocess.run(
                ["defaults", "read", "com.apple.LaunchServices/com.apple.launchservices.secure", "LSHandlers"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and "brave" in result.stdout.lower():
                brave_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
                if os.path.exists(brave_path):
                    print(f"Using default browser: Brave ({brave_path})")
                    return brave_path
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Fallback chain for macOS
        browsers = [
            ("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser", "Brave"),
            ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "Google Chrome"),
            ("/Applications/Chromium.app/Contents/MacOS/Chromium", "Chromium"),
        ]
        
        for path, name in browsers:
            if os.path.exists(path):
                print(f"Using {name} ({path})")
                return path
    
    # Windows
    elif system == "Windows":
        # Try to get default browser from registry
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice"
            )
            prog_id = winreg.QueryValueEx(key, "ProgId")[0]
            winreg.CloseKey(key)
            
            if "Brave" in prog_id:
                brave_paths = [
                    os.path.expandvars(r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"),
                    os.path.expandvars(r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe"),
                ]
                for path in brave_paths:
                    if os.path.exists(path):
                        print(f"Using default browser: Brave ({path})")
                        return path
            elif "Chrome" in prog_id:
                chrome_paths = [
                    os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                    os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
                ]
                for path in chrome_paths:
                    if os.path.exists(path):
                        print(f"Using default browser: Chrome ({path})")
                        return path
        except (ImportError, OSError):
            pass
        
        # Fallback chain for Windows
        browsers = [
            (r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe", "Brave"),
            (r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe", "Brave"),
            (r"%ProgramFiles%\Google\Chrome\Application\chrome.exe", "Google Chrome"),
            (r"%LocalAppData%\Google\Chrome\Application\chrome.exe", "Google Chrome"),
        ]
        
        for path_template, name in browsers:
            path = os.path.expandvars(path_template)
            if os.path.exists(path):
                print(f"Using {name} ({path})")
                return path
    
    print("Warning: No Chrome/Chromium browser found. Selenium will try default ChromeDriver path.")
    return None


def login_x(target_date, desired_times, retry_interval, location="Fitness"):
    """
    Try to book fitness slots at the specified times on the target date.

    Args:
        target_date (datetime): Date to book for (time component is ignored)
        desired_times (list): List of times to try booking in order of preference
                            Format: ["09:00", "10:30", "12:00"]
        retry_interval: Interval to wait before retrying
        location (str): Location to book - "Fitness", "X1", "X2", or "X3"
    """
    # Format date for the date picker
    date_str = target_date.strftime("%Y-%m-%d")

    # Load environment variables
    load_dotenv()
    username = os.getenv('TU_USERNAME')
    password = os.getenv('TU_PASSWORD')

    # Initialize Chrome options
    chrome_options = Options()
    
    # Detect and set browser binary
    browser_binary = find_chrome_binary()
    if browser_binary:
        chrome_options.binary_location = browser_binary
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    # Add headless mode options
    # new headless mode for Chrome v109+
    chrome_options.add_argument("--headless=new")
    # Set a standard resolution
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")  # Recommended for headless

    # Initialize the webdriver with Selenium 4.6+ automatic driver management
    driver = webdriver.Chrome(options=chrome_options)

    try:
        while True:
            try:
                # If driver is not responding, restart it
                try:
                    driver.current_url
                except Exception:
                    print("Browser seems unresponsive, restarting...")
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    driver = webdriver.Chrome(options=chrome_options)

                # Navigate to the website
                print("Navigating to x.tudelft.nl...")
                driver.get('https://x.tudelft.nl')

                # Check if already authenticated by looking for the login page
                print("Checking authentication status...")
                wait = WebDriverWait(driver, 10)
                try:
                    # Wait a moment for page to load
                    time.sleep(2)
                    
                    # Check if we're on the login page
                    current_url = driver.current_url
                    login_heading = driver.find_elements(By.CSS_SELECTOR, "h1[data-test-id='login-page-header']")
                    
                    if not login_heading and '/pages/login' not in current_url:
                        print("Already authenticated (no login page), skipping login...")
                    else:
                        # Need to log in
                        print("Not authenticated, proceeding with login...")
                        # Wait for and click the TU Delft button
                        print("Waiting for TU Delft button...")
                        tu_delft_button = wait.until(EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, "button[data-test-id='oidc-login-button']")))
                        print("Found TU Delft button")
                        tu_delft_button.click()
                        print("Clicked TU Delft button")

                        # Select "Delft University of Technology" account
                        tu_delft_account = wait.until(EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, "div[data-title='Delft University of Technology']")))
                        tu_delft_account.click()
                        print("Clicked TU Delft account")
                        # Wait for login elements and login
                        username_field = wait.until(
                            EC.presence_of_element_located((By.ID, 'username')))
                        password_field = driver.find_element(By.ID, 'password')

                        username_field.send_keys(username)
                        password_field.send_keys(password)
                        print("Sent username and password")
                        # Find and click login button
                        login_button = driver.find_element(By.ID, 'submit_button')
                        login_button.click()
                        print("Clicked login button")

                        # Wait for redirect to x.tudelft.nl after login
                        print("Waiting for redirect to x.tudelft.nl...")
                        wait.until(lambda d: 'x.tudelft.nl' in d.current_url)
                        print(f"Redirected to: {driver.current_url}")
                except Exception as e:
                    print(f"Error during authentication check/login: {str(e)}")
                    raise

                # Wait for date picker to be present and interactable
                # Updated selector to match the actual form control
                date_picker = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "input[type='date'].form-control"))
                )
                # Wait until it's not disabled/readonly
                wait.until(lambda d: date_picker.get_attribute("readonly") is None)

                # Set the date value using JavaScript to ensure correct format
                driver.execute_script(
                    "arguments[0].value = arguments[1]",
                    date_picker,
                    date_str
                )
                print(f"Set date to {date_str}")

                # Trigger change event to ensure the page updates
                driver.execute_script(
                    "arguments[0].dispatchEvent(new Event('change', { 'bubbles': true }))",
                    date_picker
                )
                print(f"Date change event dispatched")

                # Wait for the page to update with the new date
                time.sleep(1)

                # Map location to checkbox ID and filter text
                location_map = {
                    "Fitness": ("tagCheckbox28", "Fitness"),
                    "X1": ("tagCheckbox147", "X1"),
                    "X2": ("tagCheckbox148", "X2"),
                    "X3": ("tagCheckbox149", "X3"),
                }
                
                if location not in location_map:
                    raise ValueError(f"Invalid location: {location}. Must be one of: Fitness, X1, X3")
                
                checkbox_id, filter_text = location_map[location]

                # Type the location into the filter input
                filter_input = wait.until(
                    EC.presence_of_element_located((By.ID, 'tag-filterinput')))
                filter_input.clear()
                filter_input.send_keys(filter_text)
                print(f"Sent {filter_text} to filter")
                time.sleep(0.5)  # Wait for filter to process

                # For X1, X2 and X3, we need to expand the "All spaces" dropdown first
                if location in ["X1", "X2", "X3"]:
                    # Find and click the "All spaces" dropdown to expand it
                    spaces_dropdown = wait.until(
                        EC.element_to_be_clickable((By.XPATH, 
                            "//li[@tabindex='0']//span[contains(text(), 'All spaces')]")))
                    spaces_dropdown.click()
                    print("Expanded 'All spaces' dropdown")
                    time.sleep(0.5)

                # Select the location checkbox
                location_checkbox = wait.until(
                    EC.element_to_be_clickable((By.ID, checkbox_id)))
                location_checkbox.click()
                print(f"Clicked {location} checkbox")

                # Press Escape to close the filter popup
                filter_input.send_keys(Keys.ESCAPE)
                print("Pressed Escape to close filter")

                # Wait for slots to load and be interactive
                wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//div[@data-test-id='bookable-slot-list']")))
                print(f"{location} slots loaded")

                # Try to ensure the page is in a stable state
                driver.execute_script("window.scrollTo(0, 0)")  # Scroll to top
                time.sleep(1)  # Let the page settle

                # Look for slots matching desired times in order
                for desired_time in desired_times:
                    print(f"Trying to book slot for {desired_time}")
                    # Find all slots for this time
                    time_slots = driver.find_elements(
                        By.XPATH,
                        f"//p[@data-test-id='bookable-slot-start-time'][.//strong[contains(text(), '{desired_time}')]]"
                    )
                    print(f"Found {len(time_slots)} slots for {desired_time}")

                    # For each time slot, find its parent container and check if it's available
                    available_slots = [
                        slot.find_element(
                            By.XPATH, "ancestor::div[@data-test-id='bookable-slot-list']")
                        for slot in time_slots
                        if not (
                            'opacity-50' in slot.find_element(
                                By.XPATH, "ancestor::div[@data-test-id='bookable-slot-list']").get_attribute('class')
                            or slot.find_element(By.XPATH, "ancestor::div[@data-test-id='bookable-slot-list']").find_elements(By.XPATH, ".//div[@data-test-id='bookable-slot-spots-full']")
                        )
                    ]
                    print(
                        f"Found {len(available_slots)} available slots for {desired_time}")

                    if available_slots:
                        try:
                            # Find and click the book button within the slot container
                            book_button = wait.until(EC.element_to_be_clickable(available_slots[0].find_element(
                                By.XPATH,
                                ".//button[@data-test-id='bookable-slot-book-button']"
                            )))
                            print("Found book button")

                            # Try to ensure no overlays are present
                            driver.execute_script(
                                "arguments[0].scrollIntoView({block: 'center'});", book_button)
                            time.sleep(1)  # Wait for any overlays to clear

                            # Try clicking via JavaScript if regular click fails
                            try:
                                book_button.click()
                            except:
                                driver.execute_script(
                                    "arguments[0].click();", book_button)
                            print("Clicked book button")

                            # Wait for and click the confirm booking button
                            confirm_button = wait.until(EC.element_to_be_clickable(
                                (By.XPATH,
                                 "//button[@data-test-id='details-book-button']")
                            ))

                            # Scroll the confirm button to the middle of the viewport
                            driver.execute_script("""
                                var element = arguments[0];
                                var elementRect = element.getBoundingClientRect();
                                var absoluteElementTop = elementRect.top + window.pageYOffset;
                                var middle = absoluteElementTop - (window.innerHeight / 2);
                                window.scrollTo(0, middle);
                            """, confirm_button)

                            confirm_button.click()
                            print("Clicked confirm button")

                            # Wait for and verify the booking success message
                            try:
                                # Wait for the success icon to appear
                                wait.until(
                                    EC.visibility_of_element_located((By.XPATH, "//i[@data-test-id='booking-success']"))
                                )
                                # Check for the heading text "Booking was made"
                                success_heading = driver.find_element(By.XPATH, "//h4[contains(text(), 'Booking was made')]")
                                if success_heading.is_displayed():
                                    print(f"Successfully booked a slot for {desired_time}!")
                                    return True
                                else:
                                    print(f"Booking failed: Success heading not visible")
                                    continue
                            except TimeoutException:
                                print("Booking failed: Success message not found within timeout period")
                                continue
                            except Exception as e:
                                print(f"Booking verification failed: {str(e)}")
                                continue

                        except Exception as e:
                            print(f"Error booking {desired_time}: {str(e)}")
                            continue
                    else:
                        print(f"No available slots for {desired_time}")

                print(
                    f"No slots available at any of the desired times. Trying again in {retry_interval} seconds...")
                raise NoAvailableSlotsError(
                    "No slots available at any of the desired times")

            except Exception as e:
                if isinstance(e, NoAvailableSlotsError):
                    print(f"No available slots: {str(e)}")
                    return False
                else:
                    # Enhanced error logging
                    print("=" * 80)
                    print(f"ERROR OCCURRED: {str(e)}")
                    print("=" * 80)
                    print("\nFull traceback:")
                    traceback.print_exc()
                    print("\n" + "=" * 80)
                    
                    # Get current URL for debugging
                    try:
                        current_url = driver.current_url
                        print(f"Current URL: {current_url}")
                    except Exception:
                        print("Could not retrieve current URL")
                    
                    # Save screenshot to project directory
                    try:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        screenshot_path = f"booking_error_{timestamp}.png"
                        driver.save_screenshot(screenshot_path)
                        print(f"Screenshot saved to: {os.path.abspath(screenshot_path)}")
                    except Exception as screenshot_error:
                        print(f"Could not save screenshot: {screenshot_error}")
                    
                    # Save HTML dump to project directory
                    try:
                        html_path = f"booking_error_{timestamp}.html"
                        with open(html_path, 'w', encoding='utf-8') as f:
                            f.write(driver.page_source)
                        print(f"HTML dump saved to: {os.path.abspath(html_path)}")
                    except Exception as html_error:
                        print(f"Could not save HTML dump: {html_error}")
                    
                    print("=" * 80)
                    return False
    finally:
        # Always cleanup the browser, even if an exception occurs
        print("Cleaning up browser session...")
        try:
            driver.quit()
        except Exception as e:
            print(f"Error during browser cleanup: {e}")


class NoAvailableSlotsError(Exception):
    pass


class BookingGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Fitness Slot Booking")
        self.root.geometry("500x750")

        # Date Selection
        self.cal = Calendar(self.root,
                            mindate=datetime.now(),
                            maxdate=datetime.now().replace(month=datetime.now().month + 3),
                            date_pattern='y-mm-dd')
        self.cal.pack(pady=20)

        # Location Selection
        location_frame = ttk.LabelFrame(self.root, text="Location")
        location_frame.pack(pady=10, padx=10, fill="x")

        self.location = tk.StringVar(value="Fitness")
        locations = [("Fitness", "Fitness"), ("X1", "X1"), ("X2", "X2"), ("X3", "X3")]
        
        for loc_value, loc_text in locations:
            ttk.Radiobutton(location_frame, text=loc_text, 
                           variable=self.location, value=loc_value).pack(side=tk.LEFT, padx=10)

        # Add retry interval control
        retry_frame = ttk.LabelFrame(self.root, text="Retry Settings")
        retry_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(retry_frame, text="Retry Interval (seconds):").pack(
            side=tk.LEFT, padx=5)

        # Default retry interval is 300 seconds (5 minutes)
        self.retry_interval = tk.StringVar(value="300")

        # Entry widget for retry interval with validation
        vcmd = (self.root.register(self.validate_interval), '%P')
        retry_entry = ttk.Entry(retry_frame, textvariable=self.retry_interval,
                                width=5, validate='key', validatecommand=vcmd)
        retry_entry.pack(side=tk.LEFT, padx=5)

        # Time Selection
        time_frame = ttk.LabelFrame(self.root, text="Select Times")
        time_frame.pack(pady=20, padx=10, fill="x")

        # Available times with priority
        self.times = [
            "07:00", "08:00", "09:00", "10:00", "11:00", "12:00",
            "13:00", "14:00", "15:00", "16:00", "17:00", "18:00",
            "19:00", "20:00", "21:00", "22:00", "23:00"
        ]

        # Create a frame for the list of selected times
        self.selected_frame = ttk.LabelFrame(
            self.root, text="Selected Times (Priority Order)")
        self.selected_frame.pack(pady=20, padx=10, fill="x")

        # Create checkboxes for times
        self.time_vars = {}
        for i, time in enumerate(self.times):
            var = tk.BooleanVar()
            self.time_vars[time] = var

            # Create frame for each time slot
            slot_frame = ttk.Frame(time_frame)
            slot_frame.grid(row=i//3, column=i % 3, padx=5, pady=2, sticky="w")

            # Add checkbox
            cb = ttk.Checkbutton(slot_frame, text=time, variable=var,
                                 command=lambda t=time: self.update_selected_times())
            cb.pack(side=tk.LEFT)

        # Selected times will be stored in order
        self.selected_times = []

        # Button frame for Book and Stop buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)

        # Book Button
        self.book_button = ttk.Button(button_frame, text="Book Selected Slots",
                                      command=self.start_booking)
        self.book_button.pack(side=tk.LEFT, padx=5)

        # Stop Button
        self.stop_button = ttk.Button(button_frame, text="Stop Retrying",
                                      command=self.stop_booking)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Status Label
        self.status_label = ttk.Label(self.root, text="")
        self.status_label.pack(pady=10)

        # Add retry timer attribute
        self.retry_timer = None

    def update_selected_times(self):
        # Clear the selected frame
        for widget in self.selected_frame.winfo_children():
            widget.destroy()

        # Get currently selected times
        current_selected = [time for time,
                            var in self.time_vars.items() if var.get()]

        # Add new selections
        for time in current_selected:
            if time not in self.selected_times:
                self.selected_times.append(time)

        # Remove unselected times
        self.selected_times = [
            t for t in self.selected_times if t in current_selected]

        # Display selected times with up/down buttons
        for i, time in enumerate(self.selected_times):
            frame = ttk.Frame(self.selected_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)

            ttk.Label(frame, text=f"{i+1}. {time}").pack(side=tk.LEFT)

            if i > 0:  # Can move up
                ttk.Button(frame, text="↑", width=3,
                           command=lambda t=time: self.move_time_up(t)).pack(side=tk.RIGHT)
            if i < len(self.selected_times) - 1:  # Can move down
                ttk.Button(frame, text="↓", width=3,
                           command=lambda t=time: self.move_time_down(t)).pack(side=tk.RIGHT)

    def move_time_up(self, time):
        idx = self.selected_times.index(time)
        if idx > 0:
            self.selected_times[idx -
                                1], self.selected_times[idx] = self.selected_times[idx], self.selected_times[idx-1]
            self.update_selected_times()

    def move_time_down(self, time):
        idx = self.selected_times.index(time)
        if idx < len(self.selected_times) - 1:
            self.selected_times[idx], self.selected_times[idx +
                                                          1] = self.selected_times[idx+1], self.selected_times[idx]
            self.update_selected_times()

    def validate_interval(self, P):
        """Validate the retry interval input"""
        if P == "":
            return True
        try:
            value = int(P)
            return value > 0
        except ValueError:
            return False

    def start_booking(self):
        selected_date = self.cal.get_date()

        if not self.selected_times:
            self.status_label.config(
                text="Please select at least one time slot")
            return

        self.status_label.config(text="Starting booking process...")

        self.book_button.state(['disabled'])

        # Create date object (time will be ignored)
        target_date = datetime.strptime(selected_date, '%Y-%m-%d')

        # Start the booking process with prioritized times
        try:
            if login_x(target_date, self.selected_times, self.retry_interval.get(), self.location.get()):
                self.status_label.config(text="Booking completed!")
                self.book_button.state(['!disabled'])
            else:
                # Get retry interval in seconds
                try:
                    interval = int(self.retry_interval.get())
                except ValueError:
                    # Default to 300 seconds (5 minutes) if invalid input
                    interval = 300

                self.status_label.config(
                    text=f"No available slots, retrying in {interval} seconds...")

                interval = interval * 1000  # Convert seconds to milliseconds

                # Schedule retry using after() with the custom interval
                if self.retry_timer:
                    self.root.after_cancel(self.retry_timer)
                self.retry_timer = self.root.after(interval,
                                                   lambda: self.start_booking())
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            self.book_button.state(['!disabled'])

    def stop_booking(self):
        if self.retry_timer:
            self.root.after_cancel(self.retry_timer)
            self.retry_timer = None
            self.status_label.config(text="Booking stopped")
            self.book_button.state(['!disabled'])

    def run(self):
        self.root.mainloop()


def main():
    parser = argparse.ArgumentParser(description='Book fitness slots')
    parser.add_argument('--date', type=str, required=True,
                        help='Date in YYYY-MM-DD format')
    parser.add_argument('--times', type=str, required=True,
                        help='Comma-separated list of times')
    parser.add_argument('--interval', type=int, required=True,
                        help='Retry interval in seconds')
    parser.add_argument('--location', type=str, default='Fitness',
                        choices=['Fitness', 'X1', 'X2', 'X3'],
                        help='Location to book (default: Fitness)')

    args = parser.parse_args()

    # Parse date
    target_date = datetime.strptime(args.date, '%Y-%m-%d')

    # Parse times
    desired_times = args.times.split(',')

    # Run in headless mode
    return login_x(target_date, desired_times, args.interval, args.location)


if __name__ == '__main__':
    # Check if running with arguments
    if len(sys.argv) > 1:
        try:
            success = main()
        except Exception as e:
            print(f"Failed to book: {str(e)}")
            sys.exit(1)
        if success:
            print("Successfully booked")
            sys.exit(0)
        else:
            print("No available slots")
            sys.exit(1)
    else:
        app = BookingGUI()
        app.run()
