from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.remote.webdriver import WebDriver


class Driver:
    user_data_dir: str = None
    headless: bool = True
    implicit_wait: float = 10
    driver: WebDriver = None


global_driver = Driver()


def get_driver() -> WebDriver:
    if global_driver.driver is None:
        options = ChromeOptions()
        if global_driver.user_data_dir is not None:
            options.add_argument(f"--user-data-dir={global_driver.user_data_dir}")
        if global_driver.headless:
            options.add_argument("--headless=new")
        driver = Chrome(options=options)
        driver.implicitly_wait(global_driver.implicit_wait)
        global_driver.driver = driver
    return global_driver.driver


def close_driver():
    if global_driver.driver is not None:
        global_driver.driver.quit()
