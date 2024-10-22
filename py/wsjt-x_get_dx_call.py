from pywinauto import Application
import time

def write_to_file(text):
    with open("dx_input_log.txt", "w") as file:
        file.write(text)

window_title_pattern = r"WSJT-X\s+.*by K1JT"
app = Application(backend="uia").connect(title_re=window_title_pattern)
window = app.window(title_re=window_title_pattern)
# window.print_control_identifiers()

input_field = window.child_window(auto_id="MainWindow.centralWidget.lower_panel_widget.DX_controls_widget.dxCallEntry", control_type="Edit")

while True:
    try:
        text = input_field.get_value()
        # print(f"{text}")

        if not text:
            text = ""

        write_to_file(text)

        time.sleep(1)

    except Exception as e:
        print(f"Error occurred: {e}")
        break