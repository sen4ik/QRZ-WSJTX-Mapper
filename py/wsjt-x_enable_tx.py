from pywinauto import Application, findwindows
import time
import sys
from datetime import datetime

def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} - {message}")

def close_grid_tracker_alerts_window():
    try:
        alerts_windows = findwindows.find_elements(title_re=r".*Alerts.*", backend="uia")
        
        if not alerts_windows:
            log_message("No 'Alerts' window found.")
            return False
            
        log_message(f"Found {len(alerts_windows)} 'Alerts' window(s). Attempting to close...")
        alerts_app = Application(backend="uia").connect(handle=alerts_windows[0].handle)
        alerts_window = alerts_app.window(handle=alerts_windows[0].handle)
        alerts_window.close()
        log_message("Closed 'Alerts' window using window.close() method.")
        return True
                    
    except Exception as e:
        log_message(f"Error while trying to close 'Alerts' window: {e}")
        return False

def monitor_and_enable_tx():
    window_title_pattern = r"WSJT-X\s+.*by K1JT"
    app = None
    max_attempts = 10
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
    
    log_message("Starting continuous monitoring of 'Enable Tx' checkbox...")
    log_message("Press Ctrl+C to stop monitoring.")
    
    try:
        # Main monitoring loop
        while True:
            try:
                # Get a reference to the Enable Tx checkbox using the exact identifier
                enable_tx_checkbox = window.child_window(
                    title="Enable Tx", 
                    auto_id="MainWindow.centralWidget.lower_panel_widget.autoButton", 
                    control_type="CheckBox"
                )
                
                # Get a reference to the Tx 6 button
                tx6_button = window.child_window(
                    title="Tx 6", 
                    auto_id="MainWindow.centralWidget.lower_panel_widget.controls_stack_widget.page.QSO_controls_widget.tabWidget.qt_tabwidget_stackedwidget.tab.txb6", 
                    control_type="Button"
                )
                
                # Check if Enable Tx checkbox is already checked
                is_checked = enable_tx_checkbox.get_toggle_state()
                
                if is_checked:
                    log_message("'Enable Tx' is already checked.")
                else:
                    log_message("'Enable Tx' is not checked.")
                    
                    # Check if a Log QSO window is open
                    try:
                        # Look for any window with "- Log QSO" in the title
                        log_qso_windows = findwindows.find_elements(title_re=r".*- Log QSO.*", backend="uia")
                        
                        if log_qso_windows:
                            log_message("Found a 'Log QSO' window. Waiting 16 seconds before clicking OK...")
                            # Wait 16 seconds before closing the Log QSO window
                            time.sleep(15.2)
                            
                            # Connect to the Log QSO window
                            log_qso_app = Application(backend="uia").connect(handle=log_qso_windows[0].handle)
                            log_qso_window = log_qso_app.window(handle=log_qso_windows[0].handle)
                            
                            # Find and click the OK button
                            ok_button = log_qso_window.child_window(title="OK", control_type="Button")
                            ok_button.click()
                            log_message("Clicked OK on the 'Log QSO' window after 16-second wait.")
                            time.sleep(0.5)  # Give UI time to respond
                            
                            # Now try to close the "Alerts" window if it's present
                            close_grid_tracker_alerts_window()
                            
                    except Exception as e:
                        log_message(f"Error handling Log QSO window: {e}")
                    
                    # First click the Tx 6 button
                    log_message("Clicking 'Tx 6' button first...")
                    tx6_button.click()
                    time.sleep(0.5)  # Give UI time to respond
                    
                    # Then click the Enable Tx checkbox
                    log_message("Now clicking 'Enable Tx' checkbox...")
                    enable_tx_checkbox.click()
                    
                    # Verify if state changed
                    time.sleep(0.5)  # Short wait for state to update
                    new_state = enable_tx_checkbox.get_toggle_state()
                    if new_state:
                        log_message("Successfully enabled TX after clicking 'Tx 6'.")
                    else:
                        log_message("Warning: Checkbox was clicked but did not change state.")
                
                # Wait before checking again
                time.sleep(1)
                
                # Check if we are stuck responding to someone without luck
                try:
                    sending_report_radio_button = window.child_window(
                        auto_id="MainWindow.centralWidget.lower_panel_widget.controls_stack_widget.page.QSO_controls_widget.tabWidget.qt_tabwidget_stackedwidget.tab.txrb2", 
                        control_type="RadioButton"
                    )
                    
                    sending_report_radio_button_state = sending_report_radio_button.get_toggle_state()
                    if sending_report_radio_button_state:
                        log_message("RadioButton 'txrb2' is checked.")
                    else:
                        log_message("RadioButton 'txrb2' is not checked.")
                except Exception as e:
                    log_message(f"Error checking RadioButton 'txrb2': {e}")
                
            except Exception as e:
                # If there's an error during a single check, log it but don't exit
                # This makes the script more resilient to temporary UI issues
                log_message(f"Error during check: {e}")
                log_message("Will retry in 3 seconds...")
                time.sleep(3)
                
                # Try to reconnect to the window if needed
                try:
                    # Check if window still exists and is responsive
                    window.is_visible()
                except:
                    log_message("Window may have closed. Attempting to reconnect...")
                    # Try to reconnect
                    matches = findwindows.find_elements(title_re=window_title_pattern, backend="uia")
                    if matches:
                        app = Application(backend="uia").connect(handle=matches[0].handle)
                        window = app.window(handle=matches[0].handle)
                        log_message("Reconnected to WSJT-X window.")
                    else:
                        log_message("WSJT-X window not found. Exiting.")
                        sys.exit(1)
        
    except KeyboardInterrupt:
        log_message("Monitoring stopped by user (Ctrl+C).")
    except Exception as e:
        log_message(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    monitor_and_enable_tx()