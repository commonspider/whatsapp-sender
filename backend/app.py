from contextlib import suppress
from typing import TypedDict, Any

from selenium.common import NoSuchWindowException, InvalidSessionIdException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from urllib3.exceptions import ProtocolError, MaxRetryError

from .socket import Socket

exit_exception = [NoSuchWindowException, ProtocolError, InvalidSessionIdException, MaxRetryError]


class Command(TypedDict):
    type: str
    data: Any


class App:
    def __init__(self, driver: WebDriver, inject_script: str):
        self._driver = driver
        self._socket = Socket(driver, self._parse_command)
        with open(inject_script) as f:
            self._inject = f.read()

    def run(self):
        self._driver.get("https://web.whatsapp.com/")
        self._driver.execute_script(self._inject)

        with suppress(*exit_exception):
            self._socket.loop()
        with suppress(*exit_exception):
            self._driver.close()

    def _parse_command(self, command: Command):
        typ = command["type"]
        data = command["data"]

        if typ == "click":
            element = self._get_element(data)
            element.click()
        elif typ == "click_and_type":
            element = self._get_element(data["element"])
            value = data["value"]
            element.click()
            element.send_keys(value)

    def _get_element(self, element: str | WebElement):
        if isinstance(element, WebElement):
            return element
        elif isinstance(element, str):
            return self._driver.find_element(By.XPATH, element)
