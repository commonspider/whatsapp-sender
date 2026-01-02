import traceback

from backend import make_driver, App

driver = make_driver(
    driver_type="chrome",
    chrome_user_data_dir="profile",
    implicit_wait=10,
)
app = App(driver, "build/inject.js")

try:
    app.run()
except Exception as exc:
    traceback.print_exception(exc)
    input()
