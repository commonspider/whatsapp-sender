import traceback

from backend import make_driver, run

driver = make_driver(
    driver_type="chrome",
    chrome_user_data_dir="profile",
    implicit_wait=10,
)

try:
    run(driver)
except Exception as exc:
    traceback.print_exception(exc)
    input()
