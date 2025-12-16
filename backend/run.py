import traceback
from contextlib import suppress

from selenium.common import NoSuchWindowException, InvalidSessionIdException
from selenium.webdriver.remote.webdriver import WebDriver
from urllib3.exceptions import ProtocolError, MaxRetryError

from .socket import socket_loop


def run(driver: WebDriver):
    with open("build/inject.js") as f:
        inject_script = f.read()

    driver.get("https://web.whatsapp.com/")
    driver.execute_script(inject_script)
    with suppress(NoSuchWindowException, ProtocolError):
        socket_loop(driver)
    with suppress(InvalidSessionIdException, MaxRetryError):
        driver.close()
