"""
GT911 Capacitive Touch Controller Driver for MicroPython
I2C interface at address 0x5D
"""

import time
from micropython import const

# GT911 I2C Address
GT911_ADDR = const(0x5D)

# GT911 Registers
GT911_PRODUCT_ID = const(0x8140)
GT911_CONFIG_VERSION = const(0x8047)
GT911_X_OUTPUT_MAX = const(0x8048)
GT911_Y_OUTPUT_MAX = const(0x804A)
GT911_TOUCH_NUMBER = const(0x804C)
GT911_MODULE_SWITCH1 = const(0x804D)
GT911_MODULE_SWITCH2 = const(0x804E)
GT911_SHAKE_COUNT = const(0x804F)
GT911_FILTER = const(0x8050)
GT911_LARGE_TOUCH = const(0x8051)
GT911_NOISE_REDUCTION = const(0x8052)
GT911_SCREEN_TOUCH_LEVEL = const(0x8053)
GT911_SCREEN_RELEASE_LEVEL = const(0x8054)
GT911_LOW_POWER_CONTROL = const(0x8055)
GT911_REFRESH_RATE = const(0x8056)
GT911_X_THRESHOLD = const(0x8057)
GT911_Y_THRESHOLD = const(0x8058)
GT911_X_SPEED_LIMIT = const(0x8059)
GT911_Y_SPEED_LIMIT = const(0x805A)
GT911_SPACE = const(0x805B)
GT911_MINI_FILTER = const(0x805C)
GT911_STRETCH_R0 = const(0x805D)
GT911_STRETCH_R1 = const(0x805E)
GT911_STRETCH_R2 = const(0x805F)
GT911_STRETCH_RM = const(0x8060)
GT911_DRV_GROUPA_NUM = const(0x8061)
GT911_DRV_GROUPB_NUM = const(0x8062)
GT911_SENSOR_NUM = const(0x8063)
GT911_FREQ_A_FACTOR = const(0x8064)
GT911_FREQ_B_FACTOR = const(0x8065)
GT911_PANEL_BIT_FREQ = const(0x8066)
GT911_PANEL_SENSOR_TIME = const(0x8068)
GT911_PANEL_TX_GAIN = const(0x806A)
GT911_PANEL_RX_GAIN = const(0x806B)
GT911_PANEL_DUMP_SHIFT = const(0x806C)
GT911_DRV_FRAME_CONTROL = const(0x806D)
GT911_CHARGING_LEVEL_UP = const(0x806E)
GT911_MODULE_SWITCH3 = const(0x806F)
GT911_GESTURE_DIS = const(0x8070)
GT911_GESTURE_LONG_PRESS_TIME = const(0x8071)
GT911_X_Y_SLOPE_ADJUST = const(0x8072)
GT911_GESTURE_CONTROL = const(0x8073)
GT911_GESTURE_SWITCH1 = const(0x8074)
GT911_GESTURE_SWITCH2 = const(0x8075)
GT911_GESTURE_REFRESH_RATE = const(0x8076)
GT911_GESTURE_TOUCH_LEVEL = const(0x8077)
GT911_NEWGREENWAKEUPLEVEL = const(0x8078)
GT911_FREQ_HOPPING_START = const(0x8079)
GT911_FREQ_HOPPING_END = const(0x807A)
GT911_NOISE_DETECT_TIMES = const(0x807B)
GT911_HOPPING_FLAG = const(0x807C)
GT911_HOPPING_THRESHOLD = const(0x807D)
GT911_NOISE_THRESHOLD = const(0x807E)
GT911_NOISE_MIN_THRESHOLD = const(0x807F)
GT911_HOPPING_SENSOR_GROUP = const(0x8082)
GT911_HOPPING_SEG1_NORMALIZE = const(0x8083)
GT911_HOPPING_SEG1_FACTOR = const(0x8084)
GT911_MAIN_CLOCK_ADJUST = const(0x8085)
GT911_HOPPING_SEG2_NORMALIZE = const(0x8086)
GT911_HOPPING_SEG2_FACTOR = const(0x8087)
GT911_HOPPING_SEG3_NORMALIZE = const(0x8089)
GT911_HOPPING_SEG3_FACTOR = const(0x808A)
GT911_HOPPING_SEG4_NORMALIZE = const(0x808C)
GT911_HOPPING_SEG4_FACTOR = const(0x808D)
GT911_HOPPING_SEG5_NORMALIZE = const(0x808F)
GT911_HOPPING_SEG5_FACTOR = const(0x8090)
GT911_HOPPING_SEG6_NORMALIZE = const(0x8092)
GT911_KEY_1 = const(0x8093)
GT911_KEY_2 = const(0x8094)
GT911_KEY_3 = const(0x8095)
GT911_KEY_4 = const(0x8096)
GT911_KEY_AREA = const(0x8097)
GT911_KEY_TOUCH_LEVEL = const(0x8098)
GT911_KEY_LEAVE_LEVEL = const(0x8099)
GT911_KEY_SENSITIVITY = const(0x809A)
GT911_KEY_SENSITIVITY2 = const(0x809B)
GT911_KEY_RESTRAIN = const(0x809C)
GT911_KEY_RESTRAIN_TIME = const(0x809D)
GT911_GESTURE_LARGE_TOUCH = const(0x809E)
GT911_HOTKNOT_NOISE_MAP = const(0x80A1)
GT911_LINK_THRESHOLD = const(0x80A2)
GT911_PXY_THRESHOLD = const(0x80A3)
GT911_GHOT_DUMP_SHIFT = const(0x80A4)
GT911_GHOT_RX_GAIN = const(0x80A5)
GT911_FREQ_GAIN0 = const(0x80A6)
GT911_FREQ_GAIN1 = const(0x80A7)
GT911_FREQ_GAIN2 = const(0x80A8)
GT911_FREQ_GAIN3 = const(0x80A9)
GT911_COMBINE_DIS = const(0x80B3)
GT911_SPLIT_SET = const(0x80B4)
GT911_SENSOR_CH0 = const(0x80B7)
GT911_DRIVER_CH0 = const(0x80D5)
GT911_CONFIG_CHKSUM = const(0x80FF)
GT911_CONFIG_FRESH = const(0x8100)
GT911_CONFIG_SIZE = const(0xFF - 0x47 + 1)
GT911_STATUS = const(0x814E)
GT911_POINT_1 = const(0x814F)
GT911_POINT_2 = const(0x8157)
GT911_POINT_3 = const(0x815F)
GT911_POINT_4 = const(0x8167)
GT911_POINT_5 = const(0x816F)

# Touch point structure size
GT911_POINT_SIZE = const(8)

class GT911:
    def __init__(self, i2c, rst=None, int_pin=None, width=320, height=480):
        self.i2c = i2c
        self.rst = rst
        self.int_pin = int_pin
        self.width = width
        self.height = height
        self.touched = False
        self.touch_points = []
        
        # Initialize pins
        if self.rst:
            self.rst.init(self.rst.OUT, value=1)
        if self.int_pin:
            self.int_pin.init(self.int_pin.IN)
            
        # Initialize touch controller
        self.init_touch()
        
    def write_reg(self, reg, data):
        """Write data to register"""
        if isinstance(data, int):
            data = bytes([data])
        buf = bytes([(reg >> 8) & 0xFF, reg & 0xFF]) + data
        self.i2c.writeto(GT911_ADDR, buf)
        
    def read_reg(self, reg, length):
        """Read data from register"""
        buf = bytes([(reg >> 8) & 0xFF, reg & 0xFF])
        self.i2c.writeto(GT911_ADDR, buf)
        return self.i2c.readfrom(GT911_ADDR, length)
        
    def init_touch(self):
        """Initialize GT911 touch controller"""
        # Reset sequence
        if self.rst and self.int_pin:
            # Set INT pin as output temporarily
            self.int_pin.init(self.int_pin.OUT)
            
            # Address 0x5D sequence
            self.int_pin(0)
            self.rst(0)
            time.sleep_ms(10)
            
            self.rst(1)
            time.sleep_ms(10)
            
            self.int_pin(0)
            time.sleep_ms(50)
            
            # Set INT pin back to input
            self.int_pin.init(self.int_pin.IN)
            
        time.sleep_ms(100)
        
        # Read product ID to verify communication
        try:
            product_id = self.read_reg(GT911_PRODUCT_ID, 4)
            print(f"GT911 Product ID: {product_id}")
        except:
            print("GT911 communication failed")
            return
            
        # Configure touch controller
        self.configure()
        
    def configure(self):
        """Configure GT911 settings"""
        # Read current configuration
        config = bytearray(self.read_reg(GT911_CONFIG_VERSION, GT911_CONFIG_SIZE))
        
        # Modify configuration
        config[1] = (self.width & 0xFF)  # X resolution low byte
        config[2] = (self.width >> 8) & 0xFF  # X resolution high byte
        config[3] = (self.height & 0xFF)  # Y resolution low byte
        config[4] = (self.height >> 8) & 0xFF  # Y resolution high byte
        config[5] = 5  # Number of touch points supported
        config[6] = 0x35  # Module switch 1
        config[7] = 0x00  # Module switch 2
        
        # Calculate checksum
        checksum = 0
        for i in range(len(config)):
            checksum += config[i]
        checksum = (~checksum + 1) & 0xFF
        
        # Write configuration
        self.write_reg(GT911_CONFIG_VERSION, config)
        self.write_reg(GT911_CONFIG_CHKSUM, bytes([checksum]))
        self.write_reg(GT911_CONFIG_FRESH, bytes([1]))
        
        time.sleep_ms(100)
        
    def get_status(self):
        """Get touch status"""
        status = self.read_reg(GT911_STATUS, 1)[0]
        return status
        
    def get_touch(self):
        """Get touch coordinates"""
        status = self.get_status()
        
        # Check if screen is touched
        if status & 0x80:
            touch_count = status & 0x0F
            
            if touch_count > 0 and touch_count <= 5:
                # Read touch points
                points = []
                for i in range(touch_count):
                    point_reg = GT911_POINT_1 + (i * GT911_POINT_SIZE)
                    data = self.read_reg(point_reg, GT911_POINT_SIZE)
                    
                    # Extract coordinates
                    track_id = data[0]
                    x = data[1] | (data[2] << 8)
                    y = data[3] | (data[4] << 8)
                    size = data[5] | (data[6] << 8)
                    
                    points.append({
                        'id': track_id,
                        'x': x,
                        'y': y,
                        'size': size
                    })
                
                # Clear status register
                self.write_reg(GT911_STATUS, bytes([0]))
                
                self.touch_points = points
                self.touched = True
                
                # Return first touch point for simple interface
                if points:
                    return (points[0]['x'], points[0]['y'])
            else:
                # Clear status register
                self.write_reg(GT911_STATUS, bytes([0]))
        
        self.touched = False
        self.touch_points = []
        return None
        
    def get_all_touches(self):
        """Get all touch points"""
        self.get_touch()
        return self.touch_points
        
    def is_touched(self):
        """Check if screen is currently touched"""
        return self.touched