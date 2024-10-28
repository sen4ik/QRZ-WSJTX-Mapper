from pywinauto import Application
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
app = Application(backend="uia").connect(title_re=window_title_pattern)
window = app.window(title_re=window_title_pattern)
# window.print_control_identifiers()

input_field = window.child_window(auto_id="MainWindow.centralWidget.lower_panel_widget.DX_controls_widget.dxCallEntry", control_type="Edit")

previous_text = read_previous_text()

while True:
    try:
        text = input_field.get_value()
        # print(f"{text}")

        if text and text != previous_text:
            write_to_file(text)
            previous_text = text
            print(f"{text}")

        time.sleep(1)

    except Exception as e:
        print(f"Error occurred: {e}")
        break