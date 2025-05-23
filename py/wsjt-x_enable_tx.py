from pywinauto import Application, findwindows
import time
import sys
from datetime import datetime

TIME_IN_REPORT_MAX_SECONDS = 90 # Max number of seconds allowed to be in the sending signal report state
REST_TIME_IN_SECONDS = 30 # Number of seconds to rest after 
TX6_TIMEOUT_SECONDS = 150  # Time before pausing due to TX6 being active too long
TX6_PAUSE_SECONDS = 120    # Duration of pause after a timeout

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

def handle_stuck_in_report_mode(window, enable_tx_checkbox, tx_report_start_time):
    """
    Handles the situation when we're stuck in report mode (txrb2 checked) for too long.
    
    Args:
        window: The WSJT-X window
        enable_tx_checkbox: Reference to the Enable TX checkbox
        tx_report_start_time: When we first detected being in report mode
        
    Returns:
        None if not stuck or not in report mode, or timestamp when action was taken
    """
    current_time = time.time()
    time_in_report_mode = current_time - tx_report_start_time
    
    # Check if we've been in report mode for more than {TIME_IN_REPORT_MAX_SECONDS} seconds
    if time_in_report_mode > TIME_IN_REPORT_MAX_SECONDS:
        log_message(f"Been in report mode for {time_in_report_mode:.1f} seconds, which exceeds {TIME_IN_REPORT_MAX_SECONDS} seconds")
        log_message("Taking action to reset stuck state...")
        
        log_message("Clicking 'Enable Tx' checkbox to stop TX...")
        enable_tx_checkbox.click()
        time.sleep(0.5)
        new_state = enable_tx_checkbox.get_toggle_state()
        if not new_state:
            log_message("Successfully disabled TX to reset from stuck state.")
        else:
            log_message("Warning: Checkbox was clicked but did not change state.")
        
        log_message("Waiting {REST_TIME_IN_SECONDS} seconds before resuming normal operation...")
        time.sleep(REST_TIME_IN_SECONDS)
        log_message("Resuming normal operation after reset.")

        try:
            tx6_button = window.child_window(
                title="Tx 6", 
                auto_id="MainWindow.centralWidget.lower_panel_widget.controls_stack_widget.page.QSO_controls_widget.tabWidget.qt_tabwidget_stackedwidget.tab.txb6", 
                control_type="Button"
            )
            log_message("Clicking 'Tx 6' button after reset...")
            tx6_button.click()
            time.sleep(0.5)
        except Exception as e:
            log_message(f"Error clicking Tx 6 button after reset: {e}")
        
        # Return the current time to reset the timer
        return None  # Reset the timer
    
    return tx_report_start_time  # Not stuck, return the original start time

def monitor_and_enable_tx():    
    window_title_pattern = r"WSJT-X\s+.*by K1JT"
    app = None
    max_attempts = 10
    attempts = 0
    
    # Variables to track time in report mode
    tx_report_start_time = None  # Will be set when we first detect being in report mode
    
    # Variables to track tx6 button activation time
    tx6_button_start_time = None
    tx6_button_paused = False
    tx6_pause_start_time = None

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
            # Check if we're in the pause state after tx6 was active for too long
            if tx6_button_paused:
                current_time = time.time()
                time_paused = current_time - tx6_pause_start_time
                
                if time_paused > TX6_PAUSE_SECONDS:  # If we've completed the full pause duration
                    log_message(f"Completed {TX6_PAUSE_SECONDS}-second pause after TX6 timeout. Resuming normal operation.")
                    tx6_button_paused = False
                    tx6_button_start_time = None
                    
                    # Get a reference to the Enable Tx checkbox
                    enable_tx_checkbox = window.child_window(
                        title="Enable Tx", 
                        auto_id="MainWindow.centralWidget.lower_panel_widget.autoButton", 
                        control_type="CheckBox"
                    )
                    
                    # Re-enable TX
                    if not enable_tx_checkbox.get_toggle_state():
                        log_message("Re-enabling TX...")
                        enable_tx_checkbox.click()
                        time.sleep(0.5)
                        
                        # Verify if state changed
                        new_state = enable_tx_checkbox.get_toggle_state()
                        if new_state:
                            log_message("Successfully re-enabled TX after pause period.")
                        else:
                            log_message("Warning: Checkbox was clicked but did not change state.")
                else:
                    log_message(f"Still in pause mode. {TX6_PAUSE_SECONDS - time_paused:.1f} seconds remaining.")
                    time.sleep(15)  # Check less frequently during pause
                    continue
            
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
                
                # Check for tx6 timeout
                if is_checked and tx6_button_start_time is not None:
                    current_time = time.time()
                    time_since_tx6 = current_time - tx6_button_start_time
                    
                    if time_since_tx6 > TX6_TIMEOUT_SECONDS:  # If TX6 has been active for too long
                        # Check if we're in signal report state
                        in_report_mode = False
                        report_time_under_limit = False
                        
                        try:
                            sending_report_radio_button = window.child_window(
                                auto_id="MainWindow.centralWidget.lower_panel_widget.controls_stack_widget.page.QSO_controls_widget.tabWidget.qt_tabwidget_stackedwidget.tab.txrb2", 
                                control_type="RadioButton"
                            )
                            
                            in_report_mode = sending_report_radio_button.get_toggle_state()
                            
                            # If in report mode, check if we're still under the {TIME_IN_REPORT_MAX_SECONDS}-second limit
                            if in_report_mode and tx_report_start_time is not None:
                                time_in_report_mode = current_time - tx_report_start_time
                                report_time_under_limit = time_in_report_mode < TIME_IN_REPORT_MAX_SECONDS  # Under {TIME_IN_REPORT_MAX_SECONDS} seconds limit
                                # log_message(f"In report mode for {time_in_report_mode:.1f} seconds ({TIME_IN_REPORT_MAX_SECONDS}-second limit)")
                            
                        except Exception as e:
                            log_message(f"Error checking report mode state: {e}")
                        
                        # Only initiate pause if NOT in report mode OR in report mode but OVER the time limit
                        if not (in_report_mode and report_time_under_limit):
                            if in_report_mode:
                                log_message(f"In report mode but exceeded time limit, proceeding with TX timeout pause")
                            else:
                                log_message(f"Not in report mode, proceeding with TX timeout pause")
                                
                            log_message(f"TX6 has been active for {time_since_tx6:.1f} seconds, which exceeds {TX6_TIMEOUT_SECONDS} seconds")
                            log_message(f"Initiating {TX6_PAUSE_SECONDS}-second pause and disabling TX...")
                            
                            # Disable TX
                            log_message("Clicking 'Enable Tx' checkbox to stop TX...")
                            enable_tx_checkbox.click()
                            time.sleep(0.5)
                            
                            # Verify if state changed
                            new_state = enable_tx_checkbox.get_toggle_state()
                            if not new_state:
                                log_message("Successfully disabled TX for pause period.")
                            else:
                                log_message("Warning: Checkbox was clicked but did not change state.")
                            
                            # Set pause state
                            tx6_button_paused = True
                            tx6_pause_start_time = time.time()
                            log_message(f"Beginning {TX6_PAUSE_SECONDS}-second pause at {datetime.fromtimestamp(tx6_pause_start_time).strftime('%H:%M:%S')}")
                        else:
                            log_message(f"TX6 timeout detected but we're in report mode for less than {TIME_IN_REPORT_MAX_SECONDS} seconds ({time_in_report_mode:.1f}s), continuing without pause")
                
                if is_checked:
                    # log_message(".")
                    # If TX6 timer not started yet, start it now
                    if tx6_button_start_time is None:
                        tx6_button_start_time = time.time()
                        log_message(f"Started tracking TX6 button activity at {datetime.fromtimestamp(tx6_button_start_time).strftime('%H:%M:%S')}")
                else:
                    log_message("'Enable Tx' is not checked.")
                    # Reset TX6 timer if TX is disabled
                    if tx6_button_start_time is not None:
                        log_message("TX disabled, resetting TX6 timer.")
                        tx6_button_start_time = None
                    
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
                    
                    # NEW: Start the tx6 button timer
                    tx6_button_start_time = time.time()
                    log_message(f"Started tracking TX6 button activity at {datetime.fromtimestamp(tx6_button_start_time).strftime('%H:%M:%S')}")
                    
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
                        log_message("Responding with signal report")
                        
                        # Start timing if this is the first time we see it checked
                        if tx_report_start_time is None:
                            tx_report_start_time = time.time()
                            log_message(f"Started tracking time in report mode at {datetime.fromtimestamp(tx_report_start_time).strftime('%H:%M:%S')}")
                        
                        # Check if we've been stuck in report mode too long
                        tx_report_start_time = handle_stuck_in_report_mode(window, enable_tx_checkbox, tx_report_start_time)
                        
                    else:
                        # log_message("...")
                        # Reset the timer if the radio button is not checked
                        if tx_report_start_time is not None:
                            log_message("No longer in report mode, resetting timer.")
                            tx_report_start_time = None
                            
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