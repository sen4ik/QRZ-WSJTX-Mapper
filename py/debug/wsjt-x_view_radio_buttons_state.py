from pywinauto import Application, findwindows
import time
import sys
from datetime import datetime

def log_message(message):
    """Helper function to print timestamped log messages"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} - {message}")

def check_radio_buttons():
    """
    Connects to WSJT-X application and checks the status of all radio buttons
    txrb1 through txrb6.
    """
    window_title_pattern = r"WSJT-X\s+.*by K1JT"
    app = None
    max_attempts = 5
    attempts = 0

    log_message("Searching for WSJT-X application window...")
    
    while app is None and attempts < max_attempts:
        try:
            matches = findwindows.find_elements(title_re=window_title_pattern, backend="uia")
            if len(matches) > 1:
                log_message(f"Multiple windows found ({len(matches)}) matching WSJT-X. Retrying in 3 seconds...")
                time.sleep(3)
                attempts += 1
                continue
            elif len(matches) == 0:
                log_message("WSJT-X not running. Retrying in 3 seconds...")
                time.sleep(3)
                attempts += 1
                continue
            else:
                app = Application(backend="uia").connect(handle=matches[0].handle)
                window = app.window(handle=matches[0].handle)
                log_message("Successfully connected to WSJT-X window.")
        except Exception as e:
            log_message(f"Error occurred while connecting: {e}. Retrying in 3 seconds...")
            time.sleep(3)
            attempts += 1

    if app is None:
        log_message(f"Failed to connect to WSJT-X after {max_attempts} attempts. Exiting.")
        sys.exit(1)
    
    log_message("Checking status of radio buttons txrb1 through txrb6...")
    
    try:
        # Base auto_id pattern, we'll replace the number for each radio button
        base_id = "MainWindow.centralWidget.lower_panel_widget.controls_stack_widget.page.QSO_controls_widget.tabWidget.qt_tabwidget_stackedwidget.tab.txrb"
        
        # Check each radio button from txrb1 to txrb6
        for i in range(1, 7):
            radio_id = f"{base_id}{i}"
            try:
                radio_button = window.child_window(
                    auto_id=radio_id, 
                    control_type="RadioButton"
                )
                
                # Get the state of the RadioButton
                radio_button_state = radio_button.get_toggle_state()
                
                # Get the button text if possible
                try:
                    button_text = radio_button.window_text()
                    text_info = f" (Text: '{button_text}')"
                except:
                    text_info = ""
                
                if radio_button_state:
                    log_message(f"RadioButton 'txrb{i}' is CHECKED{text_info}")
                else:
                    log_message(f"RadioButton 'txrb{i}' is NOT checked{text_info}")
                    
                # Also print the button's coordinates if possible
                try:
                    rect = radio_button.rectangle()
                    log_message(f"  Position: Left={rect.left}, Top={rect.top}, Right={rect.right}, Bottom={rect.bottom}")
                except Exception as e:
                    log_message(f"  Could not get position: {e}")
                    
            except Exception as e:
                log_message(f"Error checking RadioButton 'txrb{i}': {e}")
            
            # Add a small delay between checks
            time.sleep(0.2)
            
        log_message("Radio button check complete.")
        
    except Exception as e:
        log_message(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_radio_buttons()