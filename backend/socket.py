import time
from contextlib import suppress
from typing import TypedDict, Any

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

script_get_command = 'window["WhatsappSenderSocket"].getCommand(arguments[0]);'

script_send_result = 'window["WhatsappSenderSocket"].sendResult(arguments[0], arguments[1]);'


class Command(TypedDict):
    id: int
    type: str
    data: Any


def socket_loop(driver: WebDriver):
    while True:
        response = driver.execute_async_script(script_get_command)
        if response is None:
            time.sleep(0.1)
            continue
        command = Command(**response)
        result = execute_command(driver, command["type"], command["data"])
        driver.execute_script(script_send_result, command["id"], result)


def execute_command(driver: WebDriver, _type: str, data: Any) -> bool:
    with suppress(Exception):
        if _type == "click":
            element = driver.find_element(By.XPATH, data)
            element.click()
            return True
        else:
            return False
    return False
