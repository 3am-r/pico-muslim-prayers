"""
Minimal Settings Test - Bypass UI completely
Test basic input without any complex drawing
"""

import time
from time import sleep_ms
from hardware_config import get_hardware

def minimal_settings_test():
    """Minimal settings test without complex UI"""
    print("=== MINIMAL SETTINGS TEST ===")
    
    # Get hardware directly
    hw = get_hardware()
    
    print("Hardware initialized:")
    print(f"- Joystick: {type(hw.joystick)}")
    print(f"- Touch: {type(hw.touch)}")
    print(f"- Buttons: {type(hw.buttons)}")
    
    # Fill screen with simple color
    hw.display.fill(0x001F)  # Blue
    
    settings = ["WiFi", "Time", "Buzzer", "Exit"]
    selected = 0
    
    print("\n=== CONTROLS ===")
    print("Joystick UP/DOWN: Navigate")
    print("Joystick CENTER: Select")
    print("Button 1: Select")
    print("Button 2: Exit")
    print("Touch screen: Show coordinates")
    
    print(f"\nCurrent selection: {settings[selected]}")
    
    last_input_time = 0
    
    while True:
        current_time = time.ticks_ms()
        
        # Only process input every 100ms to avoid spam
        if time.ticks_diff(current_time, last_input_time) > 100:
            input_detected = False
            
            # === TEST JOYSTICK ===
            try:
                direction = hw.joystick.get_direction()
                if direction and direction != 'center':
                    print(f"JOYSTICK: {direction}")
                    if direction == 'up':
                        selected = (selected - 1) % len(settings)
                        input_detected = True
                    elif direction == 'down':
                        selected = (selected + 1) % len(settings)
                        input_detected = True
                    
                # Check center button
                if hw.joystick.get_button_press():
                    print(f"JOYSTICK BUTTON: Selected {settings[selected]}")
                    if settings[selected] == "Exit":
                        break
                    input_detected = True
                    
            except Exception as e:
                print(f"Joystick error: {e}")
            
            # === TEST PHYSICAL BUTTONS ===
            try:
                hw.buttons.update()
                if hw.buttons.get_select_press():
                    print(f"BUTTON 1: Selected {settings[selected]}")
                    if settings[selected] == "Exit":
                        break
                    input_detected = True
                    
                if hw.buttons.get_back_press():
                    print("BUTTON 2: Exit")
                    break
                    
            except Exception as e:
                print(f"Buttons error: {e}")
            
            # === TEST TOUCH ===
            try:
                touch_data = hw.touch.get_touch()
                if touch_data:
                    x, y = touch_data[0], touch_data[1]
                    print(f"TOUCH: X={x}, Y={y}")
                    # Simple touch zones for selection
                    if y < 120:  # Top quarter
                        selected = 0
                        input_detected = True
                    elif y < 240:  # Second quarter
                        selected = 1
                        input_detected = True
                    elif y < 360:  # Third quarter
                        selected = 2
                        input_detected = True
                    else:  # Bottom quarter
                        selected = 3
                        input_detected = True
                    
            except Exception as e:
                print(f"Touch error: {e}")
            
            # Update display if input was detected
            if input_detected:
                print(f">>> SELECTION: {settings[selected]} <<<")
                last_input_time = current_time
                
                # Change screen color based on selection
                colors = [0xF800, 0x07E0, 0x001F, 0xFFE0]  # Red, Green, Blue, Yellow
                hw.display.fill(colors[selected])
        
        # Small sleep to prevent overwhelming CPU
        time.sleep(0.05)

if __name__ == "__main__":
    try:
        minimal_settings_test()
    except KeyboardInterrupt:
        print("\nTest interrupted")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()