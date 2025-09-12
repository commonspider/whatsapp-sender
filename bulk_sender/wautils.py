import time

from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from .driver import get_driver

WA_URL = "https://web.whatsapp.com/"


def login_code(country: str, phone: str):
    driver = get_driver()
    driver.get(WA_URL)
    try:
        driver.find_element(By.TAG_NAME, "canvas")
        driver.find_element(By.XPATH, '//div[contains(text(),"Log in with phone number")]').click()
        driver.find_element(By.XPATH, '//span[@data-icon="chevron"]').click()
        driver.find_element(By.XPATH, '//div[@role="textbox"]').send_keys(country)
        driver.find_element(By.XPATH, f'//div[contains(text(),"{country}")]').click()
        driver.find_element(By.XPATH, '//input[@aria-label="Type your phone number."]').send_keys(phone)
        driver.find_element(By.XPATH, '//div[contains(text(),"Next")]').click()
        code = driver.find_element(By.XPATH, '//div[contains(@data-link-code, ",")]').text
        return code.replace("\n", "")
    except NoSuchElementException:
        return None


def login_qr():
    driver = get_driver()
    driver.get(WA_URL)
    try:
        canvas = driver.find_element(By.TAG_NAME, "canvas")
        return canvas.screenshot_as_png
    except NoSuchElementException:
        return None


def post_login(timeout: float = 600):
    driver = get_driver()
    WebDriverWait(driver, timeout).until(
        expected_conditions.presence_of_element_located((By.XPATH, '//div[@aria-placeholder="Search or start a new chat"]'))
    ).click()


def send_message(phone: str, text: str):
    driver = get_driver()
    driver.get(f"{WA_URL}send?phone={phone}&text={text}")
    try:
        driver.find_element(By.XPATH, '//button[@aria-label="Send"]').click()
        return True
    except NoSuchElementException:
        return False


def send_message_old(phone: str, text: str):
    driver = get_driver()
    search = driver.find_element(By.XPATH, '//div[@aria-placeholder="Search or start a new chat"]')
    search.click()
    search.send_keys(phone)
    time.sleep(1)
    items = driver.find_elements(By.XPATH, '//div[@role="listitem"]')
    if len(items) == 0:
        return False
    item = items[1]
    item.click()
    bar = driver.find_element(By.XPATH, '//div[@aria-placeholder="Type a message"]')
    bar.click()
    bar.send_keys(text)
    driver.find_element(By.XPATH, '//button[@aria-label="Send"]').click()
    time.sleep(1)
    return True
