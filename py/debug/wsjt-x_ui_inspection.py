# Helps finding all the UI elements. 

from pywinauto import Application, findwindows
import time
import sys
import os

def inspect_wsjt_x_ui():
    """
    Creates a detailed inspection of the WSJT-X UI including:
    1. Full control hierarchy
    2. Detailed button properties
    3. Screenshots of the window (if PIL is available)
    4. Saves results to a log file for later reference
    """
    window_title_pattern = r"WSJT-X\s+.*by K1JT"
    app = None
    max_attempts = 10
    attempts = 0
    
    # Create a log file
    log_filename = "wsjt_x_ui_inspection.log"
    with open(log_filename, "w") as log_file:
        log_file.write(f"WSJT-X UI Inspection Report\n")
        log_file.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write("="*50 + "\n\n")

    print(f"Searching for WSJT-X application window...")
    log_message(f"Searching for WSJT-X application window...", log_filename)
    
    while app is None and attempts < max_attempts:
        try:
            matches = findwindows.find_elements(title_re=window_title_pattern, backend="uia")
            if len(matches) > 1:
                msg = f"Multiple windows found ({len(matches)}) matching WSJT-X. Retrying in 3 seconds..."
                print(msg)
                log_message(msg, log_filename)
                time.sleep(3)
                attempts += 1
                continue
            elif len(matches) == 0:
                msg = "WSJT-X not running. Retrying in 3 seconds..."
                print(msg)
                log_message(msg, log_filename)
                time.sleep(3)
                attempts += 1
                continue
            else:
                app = Application(backend="uia").connect(handle=matches[0].handle)
                window = app.window(handle=matches[0].handle)
                msg = "Successfully connected to WSJT-X window."
                print(msg)
                log_message(msg, log_filename)
        except Exception as e:
            msg = f"Error occurred while connecting: {e}. Retrying in 3 seconds..."
            print(msg)
            log_message(msg, log_filename)
            time.sleep(3)
            attempts += 1

    if app is None:
        msg = f"Failed to connect to WSJT-X after {max_attempts} attempts. Exiting."
        print(msg)
        log_message(msg, log_filename)
        sys.exit(1)
    
    try:
        # 1. Get basic window information
        msg = "\n=== BASIC WINDOW INFORMATION ===\n"
        print(msg)
        log_message(msg, log_filename)
        
        window_info = {
            "Title": window.window_text(),
            "Class": window.class_name(),
            "Handle": window.handle,
            "Rectangle": window.rectangle(),
            "Is Visible": window.is_visible(),
            "Process ID": window.process_id(),
        }
        
        for key, value in window_info.items():
            msg = f"{key}: {value}"
            print(msg)
            log_message(msg, log_filename)
        
        # 2. Print all control identifiers
        msg = "\n=== FULL CONTROL HIERARCHY ===\n"
        print(msg)
        log_message(msg, log_filename)
        
        # Capture print_control_identifiers output
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            window.print_control_identifiers(depth=10)  # Maximum depth to see everything
        
        control_output = f.getvalue()
        print(control_output)
        log_message(control_output, log_filename)
        
        # 3. Find and detail all buttons
        msg = "\n=== DETAILED BUTTON ANALYSIS ===\n"
        print(msg)
        log_message(msg, log_filename)
        
        all_buttons = window.descendants(control_type="Button")
        msg = f"Found {len(all_buttons)} buttons in the UI."
        print(msg)
        log_message(msg, log_filename)
        
        for i, button in enumerate(all_buttons, 1):
            try:
                # Collect all possible properties
                props = {
                    "Index": i,
                    "Text": button.window_text(),
                    "Control Type": button.control_type(),
                    "Class Name": button.class_name(),
                    "Automation ID": button.automation_id() if hasattr(button, 'automation_id') else 'N/A',
                    "Rectangle": button.rectangle(),
                    "Is Visible": button.is_visible(),
                    "Is Enabled": button.is_enabled(),
                    "Parent": button.parent().window_text() if button.parent() else 'N/A',
                    "Parent Class": button.parent().class_name() if button.parent() else 'N/A',
                    "Parent Automation ID": button.parent().automation_id() if button.parent() and hasattr(button.parent(), 'automation_id') else 'N/A',
                }
                
                # Print button properties
                msg = f"\nButton #{i}:"
                print(msg)
                log_message(msg, log_filename)
                
                for key, value in props.items():
                    msg = f"  {key}: {value}"
                    print(msg)
                    log_message(msg, log_filename)
                
                # Additional check for TX-related buttons
                if any(tx_term in props["Text"].lower() for tx_term in ['tx', 'enable', 'transmit']):
                    msg = f"  NOTE: This button may be the TX button based on its text!"
                    print(msg)
                    log_message(msg, log_filename)
                
                # Get all available properties for the button
                msg = "  All Properties:"
                print(msg)
                log_message(msg, log_filename)
                
                # Try to get all properties using different methods
                try:
                    # Method 1: Legacy .get_properties() if available
                    if hasattr(button, 'get_properties'):
                        for prop, value in button.get_properties().items():
                            msg = f"    {prop}: {value}"
                            print(msg)
                            log_message(msg, log_filename)
                    else:
                        # Method 2: Look at element_info properties
                        if hasattr(button, 'element_info'):
                            msg = f"    Using element_info properties:"
                            print(msg)
                            log_message(msg, log_filename)
                            
                            for prop in dir(button.element_info):
                                if not prop.startswith('_') and prop not in ['parent', 'children']:
                                    try:
                                        value = getattr(button.element_info, prop)
                                        if callable(value):
                                            try:
                                                value = value()
                                            except:
                                                value = "Method (cannot call)"
                                        msg = f"      {prop}: {value}"
                                        print(msg)
                                        log_message(msg, log_filename)
                                    except Exception as e:
                                        pass
                except Exception as e:
                    msg = f"    Error getting properties: {e}"
                    print(msg)
                    log_message(msg, log_filename)
                
            except Exception as e:
                msg = f"Error analyzing button #{i}: {e}"
                print(msg)
                log_message(msg, log_filename)
        
        # 4. Look specifically for controls in the lower panel
        msg = "\n=== LOOKING FOR CONTROLS IN LOWER PANEL ===\n"
        print(msg)
        log_message(msg, log_filename)
        
        # Try to find lower panel or similar container
        lower_panel_candidates = []
        for control in window.descendants():
            try:
                control_id = control.automation_id() if hasattr(control, 'automation_id') else ''
                control_text = control.window_text() if hasattr(control, 'window_text') else ''
                control_class = control.class_name() if hasattr(control, 'class_name') else ''
                
                if any(term in control_id.lower() for term in ['lower', 'bottom', 'panel']) or \
                   any(term in control_text.lower() for term in ['lower', 'bottom', 'panel']):
                    lower_panel_candidates.append(control)
            except:
                continue
        
        if lower_panel_candidates:
            msg = f"Found {len(lower_panel_candidates)} potential lower panel containers."
            print(msg)
            log_message(msg, log_filename)
            
            for i, panel in enumerate(lower_panel_candidates, 1):
                try:
                    msg = f"\nLower Panel Candidate #{i}:"
                    print(msg)
                    log_message(msg, log_filename)
                    
                    panel_info = {
                        "Text": panel.window_text(),
                        "Control Type": panel.control_type(),
                        "Class Name": panel.class_name(),
                        "Automation ID": panel.automation_id() if hasattr(panel, 'automation_id') else 'N/A',
                    }
                    
                    for key, value in panel_info.items():
                        msg = f"  {key}: {value}"
                        print(msg)
                        log_message(msg, log_filename)
                    
                    # List all children of this panel
                    panel_children = panel.children()
                    msg = f"  Children: {len(panel_children)}"
                    print(msg)
                    log_message(msg, log_filename)
                    
                    for j, child in enumerate(panel_children, 1):
                        try:
                            child_info = {
                                "Text": child.window_text(),
                                "Control Type": child.control_type(),
                                "Class Name": child.class_name(),
                                "Automation ID": child.automation_id() if hasattr(child, 'automation_id') else 'N/A',
                            }
                            
                            msg = f"    Child #{j}:"
                            print(msg)
                            log_message(msg, log_filename)
                            
                            for key, value in child_info.items():
                                msg = f"      {key}: {value}"
                                print(msg)
                                log_message(msg, log_filename)
                        except:
                            continue
                except:
                    continue
        else:
            msg = "No clear lower panel containers found."
            print(msg)
            log_message(msg, log_filename)
        
        # 5. Provide specific guidance based on findings
        msg = "\n=== ANALYSIS AND RECOMMENDATIONS ===\n"
        print(msg)
        log_message(msg, log_filename)
        
        # Try to identify the most likely TX button candidates
        tx_button_candidates = []
        for button in all_buttons:
            score = 0
            try:
                button_text = button.window_text().lower()
                button_id = button.automation_id().lower() if hasattr(button, 'automation_id') else ''
                
                # Score based on button text
                if 'enable tx' in button_text:
                    score += 10
                elif 'tx' == button_text:
                    score += 8
                elif 'tx' in button_text:
                    score += 5
                elif any(term in button_text for term in ['transmit', 'xmit']):
                    score += 4
                
                # Score based on automation ID
                if 'txbutton' in button_id:
                    score += 8
                elif 'tx' in button_id:
                    score += 5
                elif any(term in button_id for term in ['transmit', 'xmit']):
                    score += 4
                
                # Only include if has some relevance
                if score > 0:
                    tx_button_candidates.append((button, score))
            except:
                continue
        
        # Sort by score
        tx_button_candidates.sort(key=lambda x: x[1], reverse=True)
        
        if tx_button_candidates:
            msg = "Most likely TX button candidates (in order of probability):"
            print(msg)
            log_message(msg, log_filename)
            
            for i, (button, score) in enumerate(tx_button_candidates, 1):
                try:
                    button_text = button.window_text()
                    button_id = button.automation_id() if hasattr(button, 'automation_id') else 'N/A'
                    button_class = button.class_name()
                    
                    msg = (f"{i}. Score: {score}/10 - Text: '{button_text}', "
                           f"ID: '{button_id}', Class: '{button_class}'")
                    print(msg)
                    log_message(msg, log_filename)
                except:
                    continue
            
            # Provide code example for the top candidate
            if tx_button_candidates:
                top_button, _ = tx_button_candidates[0]
                try:
                    top_text = top_button.window_text()
                    top_id = top_button.automation_id() if hasattr(top_button, 'automation_id') else None
                    top_class = top_button.class_name()
                    
                    msg = "\nRecommended code to click the top candidate button:"
                    print(msg)
                    log_message(msg, log_filename)
                    
                    if top_id:
                        code = f"button = window.child_window(auto_id='{top_id}', control_type='Button')"
                    elif top_text:
                        code = f"button = window.child_window(title='{top_text}', control_type='Button')"
                    else:
                        code = f"# Need to use a more complex search strategy - see full report"
                    
                    code_sample = f"""
# Code to click the most likely TX button
try:
    {code}
    button.click()
    print("Successfully clicked the TX button")
except Exception as e:
    print(f"Failed to click TX button: {{e}}")
"""
                    print(code_sample)
                    log_message(code_sample, log_filename)
                except:
                    pass
        else:
            msg = "No clear TX button candidates identified. Please review the full control hierarchy."
            print(msg)
            log_message(msg, log_filename)
        
        msg = f"\nComplete inspection saved to: {os.path.abspath(log_filename)}"
        print(msg)
    
    except Exception as e:
        msg = f"Error during UI inspection: {e}"
        print(msg)
        log_message(msg, log_filename)
        sys.exit(1)

def log_message(message, log_filename):
    """Write a message to the log file"""
    with open(log_filename, "a") as log_file:
        log_file.write(message + "\n")

if __name__ == "__main__":
    inspect_wsjt_x_ui()