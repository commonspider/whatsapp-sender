import time
import traceback
from contextlib import suppress
from typing import TypedDict, Any

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

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
    try:
        if _type == "click":
            if isinstance(data, WebElement):
                data.click()
                return True
            elif isinstance(data, str):
                element = driver.find_element(By.XPATH, data)
                element.click()
                return True
        elif _type == "click_and_type":
            if isinstance(data, dict):
                element = data["element"]
                value = data["value"]
                if isinstance(element, str):
                    element = driver.find_element(By.XPATH, element)
                    element.click()
                    element.send_keys(value)
                    return True
    except Exception as exc:
        traceback.print_exception(exc)
    return False
