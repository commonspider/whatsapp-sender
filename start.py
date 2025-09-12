from bulk_sender import create_app, global_driver, close_driver

### CONFIGURATION
global_driver.user_data_dir = "profile"
global_driver.headless = False
global_driver.implicit_wait = 5
port = 8050
homepage_delay = 1
debug = False
###

app = create_app()
try:
    print(f"=== APRI IL BROWSER E VAI SU http://127.0.0.1:{port} ===")
    app.run(port=port, debug=debug)
finally:
    close_driver()
