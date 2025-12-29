#! python3
# -*- coding: utf-8 -*-
"""Naukri Daily update - Using Chrome"""

import io
import logging
import os
import sys
import time
from datetime import datetime
from random import choice, randint
from string import ascii_uppercase, digits

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC
import constants
import chromedriver_autoinstaller
chromedriver_autoinstaller.install()
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
# Add folder Path of your resume
originalResumePath = constants.ORIGINAL_RESUME_PATH
# Add Path where modified resume should be saved
modifiedResumePath = constants.MODIFIED_RESUME_PATH

# Update your naukri username and password here before running
username = constants.USERNAME
password = constants.PASSWORD
mob = constants.MOBILE

# False if you dont want to add Random HIDDEN chars to your resume
updatePDF = False

# If Headless = True, script runs Chrome in headless mode without visible GUI
headless = False

# ----- No other changes required -----

# Set login URL
NaukriURL = constants.NAUKRI_LOGIN_URL

logging.basicConfig(
    level=logging.INFO, filename="naukri.log", format="%(asctime)s    : %(message)s"
)
# logging.disable(logging.CRITICAL)
os.environ["WDM_LOCAL"] = "1"
os.environ["WDM_LOG_LEVEL"] = "0"


def log_msg(message):
    """Print to console and store to Log"""
    print(message)
    logging.info(message)


def catch(error):
    """Method to catch errors and log error details"""
    _, _, exc_tb = sys.exc_info()
    lineNo = str(exc_tb.tb_lineno)
    msg = "%s : %s at Line %s." % (type(error), error, lineNo)
    print(msg)
    logging.error(msg)


def getObj(locatorType):
    """This map defines how elements are identified"""
    map = {
        "ID": By.ID,
        "NAME": By.NAME,
        "XPATH": By.XPATH,
        "TAG": By.TAG_NAME,
        "CLASS": By.CLASS_NAME,
        "CSS": By.CSS_SELECTOR,
        "LINKTEXT": By.LINK_TEXT,
    }
    return map[locatorType.upper()]


def GetElement(driver, elementTag, locator="ID"):
    """Wait max 15 secs for element and then select when it is available"""
    try:

        def _get_element(_tag, _locator):
            _by = getObj(_locator)
            if is_element_present(driver, _by, _tag):
                return WebDriverWait(driver, 15).until(
                    lambda d: driver.find_element(_by, _tag)
                )

        element = _get_element(elementTag, locator.upper())
        if element:
            return element
        else:
            log_msg("Element not found with %s : %s" % (locator, elementTag))
            return None
    except Exception as e:
        catch(e)
    return None


def is_element_present(driver, how, what):
    """Returns True if element is present"""
    try:
        driver.find_element(by=how, value=what)
    except NoSuchElementException:
        return False
    return True


def WaitTillElementPresent(driver, elementTag, locator="ID", timeout=30):
    """Wait till element present. Default 30 seconds"""
    result = False
    driver.implicitly_wait(0)
    locator = locator.upper()

    for _ in range(timeout):
        time.sleep(0.99)
        try:
            if is_element_present(driver, getObj(locator), elementTag):
                result = True
                break
        except Exception as e:
            log_msg("Exception when WaitTillElementPresent : %s" % e)
            pass

    if not result:
        log_msg("Element not found with %s : %s" % (locator, elementTag))
    driver.implicitly_wait(3)
    return result


def tearDown(driver):
    try:
        driver.close()
        log_msg("Driver Closed Successfully")
    except Exception as e:
        catch(e)
        pass

    try:
        driver.quit()
        log_msg("Driver Quit Successfully")
    except Exception as e:
        catch(e)
        pass


def randomText():
    return "".join(choice(ascii_uppercase + digits) for _ in range(randint(1, 5)))

def LoadNaukri(headless=True):
    """Initialize Chrome WebDriver for Naukri.com, optimized for GitHub Actions."""
    options = webdriver.ChromeOptions()
    
    # Common options
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-popups")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Headless mode for CI
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    
    # Pretend to be a real browser
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/116.0.0.0 Safari/537.36"
    )
    
    # Initialize Chrome driver
    driver = webdriver.Chrome(options=options, service=ChromeService())
    
    # Wait implicitly for elements
    driver.implicitly_wait(5)
    
    # Open Naukri login page
    driver.get(NaukriURL)
    
    # Ensure page loaded completely
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    
    log_msg("Naukri page loaded successfully")
    return driver


def naukriLogin(headless=True):
    """Open Chrome browser and Login to Naukri.com (for GitHub Actions)"""
    status = False
    driver = None
    username_locator = "usernameField"
    password_locator = "passwordField"
    login_btn_locator = "//*[@type='submit' and normalize-space()='Login']"

    try:
        driver = LoadNaukri(headless)

        log_msg(driver.title)
        if "naukri.com" in driver.title.lower():
            log_msg("Website Loaded Successfully.")

        # Wait for the username field to appear
        try:
            emailFieldElement = WebDriverWait(driver, 20).until(
                lambda d: d.find_element(By.ID, username_locator)
            )
        except Exception:
            log_msg("Username field not found!")
            emailFieldElement = None

        if emailFieldElement:
            print("p-1")
            emailFieldElement.clear()
            print(f"USERNAME is set with length {len(username)}")
            print(f"passwor is set with length {len(password)}")

            emailFieldElement.send_keys(username)
            passFieldElement = driver.find_element(By.ID, password_locator)
            passFieldElement.clear()
            passFieldElement.send_keys(password)

            loginButton = driver.find_element(By.XPATH, login_btn_locator)
            loginButton.send_keys(Keys.ENTER)

            # Wait until the login page stabilizes
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            time.sleep(10)

            # Save screenshot after page fully loaded
            screenshot_path = os.path.join(os.getcwd(), "login_debug.png")  # current folder in GitHub Actions
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved at {screenshot_path}")


            # Check if login successful
            if WaitTillElementPresent(driver, "nI-gNb-icon-img", locator="CLASS", timeout=50):
                CheckPoint = GetElement(driver, "nI-gNb-icon-img", locator="CLASS")
                if CheckPoint:
                    log_msg("Naukri Login Successful")
                    status = True
                else:
                    log_msg("Unknown Login Error")
            else:
                log_msg("Unknown Login Error")

    except Exception as e:
        catch(e)
    return (status, driver)



def UpdateProfile(driver):
    try:
        # 1️⃣ Navigate to profile page
        profile_url = "https://www.naukri.com/mnjuser/profile?id=&altresid"
        driver.get(profile_url)
        driver.implicitly_wait(3)
        log_msg("Profile page loaded.")

        # 2️⃣ Click on profile heading to open modal
        # 
        # profile_heading_xpath = '//*[@id="root"]/div[1]/div[4]/div/div/div/div[1]/div/div[2]/div[1]/h1/span'
        profile_heading_xpath = '//*[@id="root"]/div/div/span/div/div/div/div/div/div[1]/div[1]/div/div/div/div[2]/div[1]/div/div[1]/em'

        WaitTillElementPresent(driver, profile_heading_xpath, locator="XPATH", timeout=15)
        prof_heading_elem = GetElement(driver, profile_heading_xpath, locator="XPATH")
        prof_heading_elem.click()
        time.sleep(2)
        log_msg("Profile modal opened.")

        # 3️⃣ Update Mobile input
        # mobile_input_xpath = '//*[@id="mobile"]'
        # WaitTillElementPresent(driver, mobile_input_xpath, locator="XPATH", timeout=10)
        # mobile_input = GetElement(driver, mobile_input_xpath, locator="XPATH")
        # if mobile_input:
        #     mobile_input.clear()
        #     log_msg("Cleared mobile input. Waiting 5 seconds...")
        #     time.sleep(5)
        #     mobile_input.send_keys(mob)
        #     log_msg(f"Entered mobile number: {mob}. Waiting 5 seconds...")
        #     time.sleep(5)
        #     driver.implicitly_wait(1)

        # 4️⃣ Check & toggle HomeTown
        hometown_xpath = '//*[@id="locationSugg"]'
        WaitTillElementPresent(driver, hometown_xpath, locator="XPATH", timeout=10)
        hometown_input = GetElement(driver, hometown_xpath, locator="XPATH")
        if hometown_input:
            current_value = hometown_input.get_attribute("value").strip()
            if current_value.lower() in ["bangalore", "bengaluru"]:
                new_value = "Kozhikode"
            else:
                new_value = "Bengaluru"
            hometown_input.clear()
            log_msg(f"Cleared HomeTown input. Waiting 5 seconds...")
            time.sleep(2)
            hometown_input.send_keys(new_value)
            log_msg(f"Entered HomeTown: {new_value}. Waiting 2 seconds...")
            time.sleep(2)
            driver.implicitly_wait(1)
            
            # 4️⃣a Click on safe neutral element to register HomeTown change
            click_outside_xpath = '//*[@id="sugDrp_locationSugg"]/ul/li/div'
            WaitTillElementPresent(driver, click_outside_xpath, locator="XPATH", timeout=10)
            outside_elem = GetElement(driver, click_outside_xpath, locator="XPATH")
            outside_elem.click()
            log_msg("Clicked outside HomeTown input to register change.")
            time.sleep(2)

        # 5️⃣ Click Save button (wait until clickable)
        save_button_xpath = '//*[@id="submit-btn"]'
        try:
            save_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, save_button_xpath))
            )
            save_button.click()
            log_msg("Save clicked. Waiting 20 seconds for changes to apply...")
            time.sleep(5)
        except Exception as e:
            log_msg(f"Error clicking Save button: {e}")

        log_msg("Profile updated successfully: mobile number set and hometown toggled.")

    except Exception as e:
        log_msg(f"Error in UpdateProfile: {e}")
def UpdateResume():
    try:
        # Random text with random location and size
        txt = randomText()
        xloc = randint(700, 1000)  # This ensures that text is 'out of page'
        fsize = randint(1, 10)

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica", fsize)
        can.drawString(xloc, 100, txt)
        can.save()

        packet.seek(0)
        new_pdf = PdfReader(packet)
        with open(originalResumePath, "rb") as f:
            existing_pdf = PdfReader(f)
            pagecount = len(existing_pdf.pages)
            log_msg("Found %s pages in PDF" % pagecount)

            output = PdfWriter()
            # Merging new pdf with last page of existing pdf
            for pageNum in range(pagecount - 1):
                output.add_page(existing_pdf.pages[pageNum])
            page = existing_pdf.pages[pagecount - 1]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)

            # Save the new resume file
            with open(modifiedResumePath, "wb") as outputStream:
                output.write(outputStream)
            log_msg("Saved modified PDF: %s" % modifiedResumePath)
            return os.path.abspath(modifiedResumePath)
    except Exception as e:
        catch(e)
    return os.path.abspath(originalResumePath)


def UploadResume(driver, resumePath):
    try:
        # 1️⃣ Navigate to profile page
        driver.get(constants.NAUKRI_PROFILE_URL)
        time.sleep(3)
        log_msg("Profile page loaded.")

        # 2️⃣ Scroll to the bottom of the page to make the Update Resume button visible
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # time.sleep(2)
        # log_msg("Scrolled to bottom of the page.")

        # 3️⃣ Click the "Update Resume" button to open file input
        # update_resume_btn_xpath = '//*[@id="root"]/div[1]/div[4]/div/div/div/div[3]/div[2]/div[12]/div/div[3]/button'
        update_resume_btn_xpath = '//*[@id="lazyAttachCV"]/div/div[2]/div[2]/div/div[2]/div/div[1]/section/div/div[2]/input'
        
        WaitTillElementPresent(driver, update_resume_btn_xpath, locator="XPATH", timeout=10)
        update_btn = GetElement(driver, update_resume_btn_xpath, locator="XPATH")
        update_btn.click()
        log_msg("Clicked Update Resume button. Waiting for file input to appear...")
        time.sleep(2)

        # 4️⃣ Upload resume file via new input field
        file_input_xpath = '//*[@id="undefined-err-inp"]'
        WaitTillElementPresent(driver, file_input_xpath, locator="XPATH", timeout=10)
        file_input = GetElement(driver, "attachCV", locator="ID")
        if file_input:
            file_input.send_keys(os.path.abspath(resumePath))
            log_msg(f"Resume file '{resumePath}' uploaded. Waiting 20 seconds for auto-save...")
            time.sleep(20)  # wait for auto-save to complete

        # 5️⃣ Optional: check if resume updated (if there is any visible confirmation element)
        log_msg("Resume upload completed successfully.")

    except Exception as e:
        log_msg(f"Error in UploadResume: {e}")
        catch(e)

    time.sleep(2)

def main():
    log_msg("-----Naukri.py Script Run Begin-----")
    driver = None
    try:
        status, driver = naukriLogin(headless)
        if status:
            UpdateProfile(driver)
            print("d")
            if os.path.exists(originalResumePath):
                if updatePDF:
                    resumePath = UpdateResume()
                    UploadResume(driver, resumePath)
                else:
                    UploadResume(driver, originalResumePath)
            else:
                log_msg("Resume not found at %s " % originalResumePath)

    except Exception as e:
        catch(e)

    finally:
        tearDown(driver)

    log_msg("-----Naukri.py Script Run Ended-----\n")


if __name__ == "__main__":
    main()
