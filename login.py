import os
import sys
import argparse
import logging
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)
import undetected_chromedriver as uc

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("attendance_script.log"),
        logging.StreamHandler()
    ]
)

def initialize_webdriver():
    """Initialize the undetected Chrome WebDriver."""
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")  # Uncomment to run in headless mode

    driver = uc.Chrome(options=options)
    return driver

def login(driver, wait, username, password):
    """Perform the login action on the website."""
    url = 'your_company_url'   # Change this to your_url
    logging.info("Navigating to URL")
    driver.get(url)

    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    logging.info("Page loaded successfully")

    try:
        logging.info("Waiting for username field to be visible")
        username_field = wait.until(EC.visibility_of_element_located((By.ID, 'username')))

        logging.info("Waiting for password field to be visible")
        password_field = wait.until(EC.visibility_of_element_located((By.ID, 'password')))
    except TimeoutException:
        logging.error("Username or password field not found")
        return False

    logging.info(f"Entering username: {username}")
    username_field.clear()
    username_field.send_keys(username)

    logging.info("Entering password")
    password_field.clear()
    password_field.send_keys(password)

    try:
        logging.info("Attempting to locate the login button")
        login_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        logging.info("Clicking the login button")
        login_button.click()
    except (TimeoutException, ElementClickInterceptedException, ElementNotInteractableException) as e:
        logging.error(f"Failed to click the login button: {e}")
        return False

    try:
        logging.info("Waiting for dashboard element to confirm successful login")
        # Update the selector to match an element that is present after login
        dashboard_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'dashboard')]"))
        )
        logging.info("Login successful, dashboard found")
        return True
    except TimeoutException:
        logging.error("Login failed - Dashboard element not found")
        # Capture screenshot and page source for debugging
        driver.save_screenshot("login_failed_screenshot.png")
        with open("page_source_after_login.html", "w", encoding="utf-8") as file:
            file.write(driver.page_source)
        # Attempt to find and log any error messages on the page
        log_login_errors(driver)
        return False

def log_login_errors(driver):
    """Log any error messages displayed on the login page."""
    error_selectors = [
        (By.CLASS_NAME, 'error-message'),
        (By.CLASS_NAME, 'alert'),
        (By.ID, 'loginError'),
        (By.XPATH, "//div[contains(@class, 'error')]"),
    ]

    for by, selector in error_selectors:
        try:
            error_element = driver.find_element(by, selector)
            logging.error(f"Login error message: {error_element.text}")
        except NoSuchElementException:
            continue

def extract_cookies(driver):
    """Extract cookies from the WebDriver session."""
    cookies = driver.get_cookies()
    logging.info(f"Cookies after login: {cookies}")
    session_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
    return session_cookies

def extract_csrf_token(driver):
    """Extract CSRF token from the page if required."""
    try:
        csrf_token = driver.execute_script(
            "return document.querySelector('meta[name=\"csrf-token\"]').getAttribute('content');"
        )
        logging.info(f"CSRF token extracted: {csrf_token}")
        return csrf_token
    except Exception:
        logging.warning("CSRF token not found")
        return None

def mark_attendance(session_cookies, action='Signin', csrf_token=None):
    """Send a POST request to mark attendance using the extracted cookies."""
    api_url = f"https://your_company.greythr.com/v3/api/attendance/mark-attendance?action={action}"   # Change this to your URL.

    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/91.0.4472.124 Safari/537.36'
        ),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    if csrf_token:
        headers['X-CSRF-Token'] = csrf_token

    session = requests.Session()
    # Set the cookies for the session
    session.cookies.update(session_cookies)

    logging.info(f"Sending POST request to mark attendance with action '{action}'")
    response = session.post(api_url, headers=headers, json={})

    if response.status_code == 200:
        logging.info(f"Attendance '{action}' marked successfully.")
    else:
        logging.error(
            f"Failed to mark attendance '{action}'. Status code: {response.status_code}, Response: {response.text}"
        )

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Automate SignIn/SignOut on greythr.')
    parser.add_argument('action', choices=['Signin', 'Signout'], help='Action to perform')
    args = parser.parse_args()

    action = args.action

    username = os.getenv('GREYTHR_USERNAME')
    password = os.getenv('GREYTHR_PASSWORD')

    if not username or not password:
        logging.error("Username or password not set. Please set the environment variables.")
        return

    # Initialize WebDriver
    driver = initialize_webdriver()
    wait = WebDriverWait(driver, 60)

    try:
        login_successful = login(driver, wait, username, password)
        if not login_successful:
            return

        session_cookies = extract_cookies(driver)

        csrf_token = extract_csrf_token(driver)

        mark_attendance(session_cookies, action=action, csrf_token=csrf_token)

    except Exception as e:
        logging.error("An unexpected error occurred", exc_info=True)
    finally:
        driver.quit()
        logging.info("WebDriver session ended")

if __name__ == "__main__":
    main()




=============================================================================================================================================================

# For Scheduling Cron Jobs

# SignIn at 9:00 AM IST (3:30 AM UTC)
30 3 * * * GREYTHR_USERNAME='your_username' GREYTHR_PASSWORD='your_password' /usr/bin/python3 /path/to/login.py Signin >> /path/to/cron.log 2>&1

# SignOut at 8:30 PM IST (3:00 PM UTC)
0 15 * * * GREYTHR_USERNAME='your_username' GREYTHR_PASSWORD='your_password' /usr/bin/python3 /path/to/login.py Signout >> /path/to/cron.log 2>&1
