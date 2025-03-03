from pywinauto import Application, findwindows
from datetime import datetime
import time
import os

def write_to_file(text):
    with open("dx_input_log.txt", "w") as file:
        file.write(text)

def read_previous_text():
    if os.path.exists("dx_input_log.txt"):
        with open("dx_input_log.txt", "r") as file:
            return file.read().strip()
    return None

window_title_pattern = r"WSJT-X\s+.*by K1JT"
previous_text = read_previous_text()
app = None

while app is None:
    try:
        matches = findwindows.find_elements(title_re=window_title_pattern, backend="uia")
        if len(matches) > 1:
            print(f"Multiple windows found ({len(matches)}) matching WSJT-X. Retrying in 5 seconds...")
            time.sleep(5)
            continue
        elif len(matches) == 0:
            print("WSJT-X not running. Retrying in 5 seconds...")
            time.sleep(5)
            continue
        else:
            app = Application(backend="uia").connect(handle=matches[0].handle)
            window = app.window(handle=matches[0].handle)
    except Exception as e:
        print(f"Error occurred: {e}. Retrying in 5 seconds...")
        time.sleep(5)

# window.print_control_identifiers()
input_field = window.child_window(auto_id="MainWindow.centralWidget.lower_panel_widget.DX_controls_widget.dxCallEntry", control_type="Edit")

while True:
    try:
        text = input_field.get_value()
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {text}")

        if text and text != previous_text:
            write_to_file(text)
            previous_text = text
            # print(f"{text}")

        time.sleep(1)

    except Exception as e:
        print(f"Error occurred: {e}")
        break
