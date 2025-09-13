from typing import Literal

from selenium.webdriver import ChromeOptions, Chrome, Firefox, FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver


class Driver:
    driver_type: Literal["chrome", "firefox"] = "firefox"
    chrome_user_data_dir: str = None
    headless: bool = True
    implicit_wait: float = 10
    driver: WebDriver = None


global_driver = Driver()


def get_driver() -> WebDriver:
    if global_driver.driver is None:
        if global_driver.driver_type == "firefox":
            options = FirefoxOptions()
            if global_driver.headless:
                options.add_argument("-headless")
            driver = Firefox(options=options)
        elif global_driver.driver_type == "chrome":
            options = ChromeOptions()
            if global_driver.chrome_user_data_dir is not None:
                options.add_argument(f"--user-data-dir={global_driver.chrome_user_data_dir}")
            if global_driver.headless:
                options.add_argument("--headless=new")
            driver = Chrome(options=options)
        else:
            raise ValueError(f"Invalid driver type {global_driver.driver_type}")
        driver.implicitly_wait(global_driver.implicit_wait)
        global_driver.driver = driver
    return global_driver.driver


def close_driver():
    if global_driver.driver is not None:
        global_driver.driver.quit()
