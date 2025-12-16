import traceback
from contextlib import suppress

from selenium.common import NoSuchWindowException, InvalidSessionIdException
from selenium.webdriver.remote.webdriver import WebDriver
from urllib3.exceptions import ProtocolError, MaxRetryError

from .socket import socket_loop

exit_exception = [NoSuchWindowException, ProtocolError, InvalidSessionIdException, MaxRetryError]


def run(driver: WebDriver):
    with open("build/inject.js") as f:
        inject_script = f.read()

    driver.get("https://web.whatsapp.com/")
    driver.execute_script(inject_script)
    with suppress(*exit_exception):
        socket_loop(driver)
    with suppress(*exit_exception):
        driver.close()
