"""
Comprehensive Hardware Test for Muslim Companion
Test all input components individually
"""

import time
from hardware_config import get_hardware

def test_all_hardware():
    """Test all hardware components"""
    print("=== MUSLIM COMPANION HARDWARE TEST ===")
    
    try:
        # Initialize hardware
        print("Initializing hardware...")
        hw = get_hardware()
        print("✓ Hardware initialization successful")
        
        # Test display
        print("\n--- DISPLAY TEST ---")
        try:
            hw.display.fill(0xF800)  # Red
            time.sleep(0.5)
            hw.display.fill(0x07E0)  # Green  
            time.sleep(0.5)
            hw.display.fill(0x001F)  # Blue
            time.sleep(0.5)
            hw.display.fill(0x0000)  # Black
            print("✓ Display test successful")
        except Exception as e:
            print(f"✗ Display test failed: {e}")
        
        # Test joystick
        print("\n--- JOYSTICK TEST ---")
        print("Move joystick and press center button (10 seconds)...")
        start_time = time.time()
        joystick_working = False
        
        while time.time() - start_time < 10:
            try:
                # Raw values
                raw = hw.joystick.read_raw()
                norm = hw.joystick.read_normalized()
                direction = hw.joystick.get_direction()
                button = hw.joystick.get_button_press()
                
                if abs(norm['x']) > 0.3 or abs(norm['y']) > 0.3:
                    print(f"Joystick movement: {direction} (x:{norm['x']:.2f}, y:{norm['y']:.2f})")
                    joystick_working = True
                    
                if button:
                    print("Joystick button pressed!")
                    joystick_working = True
                    
            except Exception as e:
                print(f"Joystick error: {e}")
                break
                
            time.sleep(0.1)
        
        if joystick_working:
            print("✓ Joystick test successful")
        else:
            print("✗ Joystick test failed - no movement detected")
        
        # Test physical buttons
        print("\n--- PHYSICAL BUTTONS TEST ---")
        print("Press Button 1 and Button 2 (10 seconds)...")
        start_time = time.time()
        buttons_working = False
        
        while time.time() - start_time < 10:
            try:
                hw.buttons.update()
                
                if hw.buttons.get_select_press():
                    print("Button 1 (Select) pressed!")
                    buttons_working = True
                    
                if hw.buttons.get_back_press():
                    print("Button 2 (Back) pressed!")
                    buttons_working = True
                    
            except Exception as e:
                print(f"Buttons error: {e}")
                break
                
            time.sleep(0.1)
        
        if buttons_working:
            print("✓ Physical buttons test successful")
        else:
            print("✗ Physical buttons test failed - no presses detected")
        
        # Test touch screen
        print("\n--- TOUCH SCREEN TEST ---")
        print("Touch the screen anywhere (10 seconds)...")
        start_time = time.time()
        touch_working = False
        
        while time.time() - start_time < 10:
            try:
                touch_data = hw.touch.get_touch()
                if touch_data:
                    x, y = touch_data[0], touch_data[1]
                    print(f"Touch detected: X={x}, Y={y}")
                    # Draw dot at touch location
                    hw.display.fill_rect(x-5, y-5, 10, 10, 0xFFE0)  # Yellow dot
                    touch_working = True
                    
            except Exception as e:
                print(f"Touch error: {e}")
                break
                
            time.sleep(0.1)
        
        if touch_working:
            print("✓ Touch screen test successful")
        else:
            print("✗ Touch screen test failed - no touches detected")
        
        # Test buzzer
        print("\n--- BUZZER TEST ---")
        try:
            print("Playing test tones...")
            hw.play_tone(1000, 200)  # 1kHz for 200ms
            time.sleep(0.3)
            hw.play_tone(2000, 200)  # 2kHz for 200ms
            time.sleep(0.3)
            hw.play_tone(500, 200)   # 500Hz for 200ms
            print("✓ Buzzer test successful")
        except Exception as e:
            print(f"✗ Buzzer test failed: {e}")
        
        # Summary
        print("\n=== HARDWARE TEST SUMMARY ===")
        print("If any component failed, check:")
        print("1. Wiring connections")
        print("2. Pin assignments in geekpi_gpio.py")
        print("3. Hardware initialization")
        print("4. Power supply")
        
        # Clear screen
        hw.display.fill(0x0000)
        
    except Exception as e:
        print(f"Hardware initialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_all_hardware()