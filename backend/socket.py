import time
import uuid
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from logging import Logger
from threading import Lock
from typing import TypedDict, Any, Literal

from selenium.webdriver.remote.webdriver import WebDriver


class Packet(TypedDict):
    type: Literal["request", "response", "exception"]
    uid: str
    data: Any


class Socket:
    def __init__(self, driver: WebDriver, callback: Callable[[Any], Any]):
        self._driver = driver
        self._logger = Logger("socket")
        self._socket_lock = Lock()
        self._buffer_out: list[Packet] = []
        self._request_futures: dict[str, Future] = {}
        self._callback_lock = Lock()
        self._callback = callback

    def send(self, data: Any):
        uid = str(uuid.uuid4())
        packet: Packet = {
            "type": "request",
            "uid": uid,
            "data": data
        }
        future = Future()
        with self._socket_lock:
            self._request_futures[uid] = future
            self._buffer_out.append(packet)
        return future

    def loop(self):
        with ThreadPoolExecutor() as executor:
            while True:
                with self._socket_lock:
                    buffer_out = self._buffer_out
                    self._buffer_out = []
                buffer_in = self._driver.execute_async_script(
                    'const callback = arguments[1];\n'
                    'const result = window["WhatsappSender"].socket.communicate(arguments[0]);\n'
                    'callback({data: result});\n',
                    buffer_out
                )
                if buffer_in is None:
                    break
                executor.map(self._receive_packet, buffer_in["data"])
                time.sleep(0.5)

    def _receive_packet(self, packet: Packet):
        typ = packet["type"]
        uid = packet["uid"]
        data = packet["data"]

        if typ == "response":
            with self._socket_lock:
                future = self._request_futures.pop(uid)
            future.set_result(data)

        elif typ == "exception":
            with self._socket_lock:
                future = self._request_futures.pop(uid)
            future.set_exception(Exception(data))

        elif typ == "request":
            try:
                with self._callback_lock:
                    result = self._callback(data)
                with self._socket_lock:
                    self._buffer_out.append({
                        "type": "response",
                        "uid": uid,
                        "data": result
                    })
            except BaseException as exc:
                with self._socket_lock:
                    self._buffer_out.append({
                        "type": "exception",
                        "uid": uid,
                        "data": str(exc)
                    })
