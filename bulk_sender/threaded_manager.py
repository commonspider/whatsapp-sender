import traceback
from collections import defaultdict
from collections.abc import Callable
from contextvars import copy_context
from threading import Thread
from typing import Any

from dash._callback_context import context_value
from dash._utils import AttributeDict
from dash.background_callback._proxy_set_props import ProxySetProps
from dash.background_callback.managers import BaseBackgroundCallbackManager
from dash.exceptions import PreventUpdate


class ThreadedManager(BaseBackgroundCallbackManager):
    def __init__(self):
        super().__init__(None)
        self._threads: dict[str, Thread] = {}
        self._results = {}
        self._props = defaultdict(list)
        self._progress = {}

    def make_job_fn(self, fn: Callable, progress: bool, key=None):
        def job_fn(result_key: str, user_callback_args: list | dict | Any, context: dict):
            def _set_progress(progress_value):
                if not isinstance(progress_value, (list, tuple)):
                    progress_value = [progress_value]
                self._results[result_key] = progress_value

            maybe_progress = [_set_progress] if progress else []

            def _set_props(_id, props):
                self._props[result_key].append({_id: props})

            def run():
                c = AttributeDict(**context)
                c.ignore_register_page = False
                c.updated_props = ProxySetProps(_set_props)
                context_value.set(c)
                try:
                    if isinstance(user_callback_args, dict):
                        user_callback_output = fn(*maybe_progress, **user_callback_args)
                    elif isinstance(user_callback_args, (list, tuple)):
                        user_callback_output = fn(*maybe_progress, *user_callback_args)
                    else:
                        user_callback_output = fn(*maybe_progress, user_callback_args)
                except PreventUpdate:
                    self._results[result_key] = {"_dash_no_update": "_dash_no_update"}
                except Exception as err:
                    self._results[result_key] = {
                        "background_callback_error": {
                            "msg": str(err),
                            "tb": traceback.format_exc(),
                        }
                    }
                else:
                    self._results[result_key] = user_callback_output

            ctx = copy_context()
            ctx.run(run)

        return job_fn

    def call_job_fn(self, key: str, job_fn: Callable, args: tuple, context: dict):
        thread = Thread(
            target=job_fn,
            args=(key, args, context)
        )
        thread.start()
        self._threads[str(thread.ident)] = thread
        return thread.ident

    def get_result(self, key: str, job: str | None):
        if len(self._props[key]) > 0:
            return self.UNDEFINED

        result = self._results.pop(key, self.UNDEFINED)
        if result is self.UNDEFINED:
            return self.UNDEFINED

        self._progress.pop(key, None)
        self._props.pop(key, None)
        self.terminate_job(job)
        return result

    def terminate_job(self, job: str | None):
        if job is None:
            return

        self._threads[job].join()
        del self._threads[job]

    def job_running(self, job: str):
        thread = self._threads.get(job)
        if thread:
            return thread.is_alive()
        else:
            return False

    def get_updated_props(self, key):
        try:
            return self._props[key].pop(0)
        except IndexError:
            return {}
