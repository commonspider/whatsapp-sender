from typing import Literal

from selenium.webdriver import ChromeOptions, Chrome, Firefox, FirefoxOptions


def make_driver(
    driver_type: Literal["chrome", "firefox"] = "firefox",
    chrome_user_data_dir: str | None = None,
    headless: bool = False,
    implicit_wait: float = 10,
):
    if driver_type == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        driver = Firefox(options=options)
    elif driver_type == "chrome":
        options = ChromeOptions()
        if chrome_user_data_dir is not None:
            options.add_argument(f"--user-data-dir={chrome_user_data_dir}")
        if headless:
            options.add_argument("--headless=new")
        driver = Chrome(options=options)
    else:
        raise ValueError(f"Invalid driver type {global_driver.driver_type}")
    driver.implicitly_wait(implicit_wait)
    return driver
