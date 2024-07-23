import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import logging

logging.basicConfig(level=logging.INFO)

def locate_element(driver, by, value, wait_time=10):
    try:
        return WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((by, value)))
    except Exception as e:
        logging.error(f"Element not found: {by}={value}. Exception: {e}")
        return None

try:
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    chrome_options.add_argument("--no-sandbox")  # Disable sandboxing
    chrome_options.add_argument("--disable-dev-shm-usage")  # Disable /dev/shm usage

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    url = 'Your_URL' #Please provide your URL here
    logging.info("Navigating to URL")
    driver.get(url)
    
    logging.info("Locating username and password fields")
    username_field = locate_element(driver, By.ID, 'username')
    password_field = locate_element(driver, By.ID, 'password')
    
    if not username_field or not password_field:
        raise Exception("Username or Password field not found")

    # Use environment variables for login credentials
    username = os.getenv('GREYTHR_USERNAME')
    password = os.getenv('GREYTHR_PASSWORD')
    
    if not username or not password:
        raise Exception("Username or Password environment variables not set")
    
    logging.info("Logging in")
    username_field.send_keys(username)
    password_field.send_keys(password)
    
    # Locate and click the login button
    login_button = locate_element(driver, By.XPATH, '//button[@type="submit"]')
    if login_button:
        login_button.click()
    else:
        raise Exception("Login button not found")
    
    time.sleep(10)  # Wait for 10 seconds to ensure the page is fully loaded
    
    logging.info("Locating Sign Out button")
    signout_button = locate_element(driver, By.XPATH, '//div[contains(@class, "btn-container")]//gt-button[@shade="primary"]')
    
    if not signout_button:
        raise Exception("Sign Out button not found")
    
    signout_button.click()
    
    time.sleep(5)
    logging.info("Logged out successfully")

except Exception as e:
    logging.error(f"An error occurred: {e}")

finally:
    if 'driver' in locals():
        driver.quit()
