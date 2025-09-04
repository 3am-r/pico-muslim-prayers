"""
ST7796 Display Driver for MicroPython
320x480 pixels, 16-bit color
"""

import time
from micropython import const

# ST7796 Commands
ST7796_NOP = const(0x00)
ST7796_SWRESET = const(0x01)
ST7796_RDDID = const(0x04)
ST7796_RDDST = const(0x09)
ST7796_SLPIN = const(0x10)
ST7796_SLPOUT = const(0x11)
ST7796_PTLON = const(0x12)
ST7796_NORON = const(0x13)
ST7796_INVOFF = const(0x20)
ST7796_INVON = const(0x21)
ST7796_DISPOFF = const(0x28)
ST7796_DISPON = const(0x29)
ST7796_CASET = const(0x2A)
ST7796_RASET = const(0x2B)
ST7796_RAMWR = const(0x2C)
ST7796_RAMRD = const(0x2E)
ST7796_PTLAR = const(0x30)
ST7796_MADCTL = const(0x36)
ST7796_COLMOD = const(0x3A)
ST7796_FRMCTR1 = const(0xB1)
ST7796_FRMCTR2 = const(0xB2)
ST7796_FRMCTR3 = const(0xB3)
ST7796_INVCTR = const(0xB4)
ST7796_DISSET5 = const(0xB6)
ST7796_PWCTR1 = const(0xC0)
ST7796_PWCTR2 = const(0xC1)
ST7796_PWCTR3 = const(0xC2)
ST7796_VMCTR1 = const(0xC5)
ST7796_VMCTR2 = const(0xC7)
ST7796_GMCTRP1 = const(0xE0)
ST7796_GMCTRN1 = const(0xE1)
ST7796_CSCON = const(0xF0)

# Color definitions
BLACK = const(0x0000)
WHITE = const(0xFFFF)
RED = const(0xF800)
GREEN = const(0x07E0)
BLUE = const(0x001F)
CYAN = const(0x07FF)
MAGENTA = const(0xF81F)
YELLOW = const(0xFFE0)
ORANGE = const(0xFD20)
PURPLE = const(0x8010)
GREY = const(0x8410)
DARK_GREEN = const(0x0400)

class ST7796:
    def __init__(self, spi, cs, dc, rst, width=320, height=480, rotation=0):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.width = width
        self.height = height
        self.rotation = rotation
        
        # Initialize pins
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        if self.rst:
            self.rst.init(self.rst.OUT, value=1)
        
        # Initialize display
        self.init_display()
        
    def write_cmd(self, cmd):
        """Write command to display"""
        self.cs(0)
        self.dc(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)
        
    def write_data(self, data):
        """Write data to display"""
        self.cs(0)
        self.dc(1)
        if isinstance(data, int):
            self.spi.write(bytearray([data]))
        else:
            self.spi.write(data)
        self.cs(1)
        
    def init_display(self):
        """Initialize ST7796 display"""
        # Hardware reset
        if self.rst:
            self.rst(1)
            time.sleep_ms(5)
            self.rst(0)
            time.sleep_ms(20)
            self.rst(1)
            time.sleep_ms(150)
        
        # Software reset
        self.write_cmd(ST7796_SWRESET)
        time.sleep_ms(150)
        
        # Exit sleep mode
        self.write_cmd(ST7796_SLPOUT)
        time.sleep_ms(120)
        
        # Memory access control
        self.write_cmd(ST7796_MADCTL)
        self.write_data(0x48)  # MX, BGR
        
        # Pixel format
        self.write_cmd(ST7796_COLMOD)
        self.write_data(0x55)  # 16 bits per pixel
        
        # Frame rate control
        self.write_cmd(ST7796_FRMCTR1)
        self.write_data(0x00)
        self.write_data(0x10)
        
        # Display function control
        self.write_cmd(ST7796_DISSET5)
        self.write_data(0x00)
        self.write_data(0x22)
        self.write_data(0x3B)
        
        # Power control
        self.write_cmd(ST7796_PWCTR1)
        self.write_data(0x17)
        self.write_data(0x15)
        
        self.write_cmd(ST7796_PWCTR2)
        self.write_data(0x41)
        
        # VCOM control
        self.write_cmd(ST7796_VMCTR1)
        self.write_data(0x00)
        self.write_data(0x12)
        self.write_data(0x80)
        
        # Positive gamma correction
        self.write_cmd(ST7796_GMCTRP1)
        gamma_data = bytearray([
            0xF0, 0x09, 0x13, 0x12, 0x12, 0x2B, 0x3C, 0x44,
            0x4B, 0x1B, 0x18, 0x17, 0x1D, 0x21
        ])
        for byte in gamma_data:
            self.write_data(byte)
        
        # Negative gamma correction
        self.write_cmd(ST7796_GMCTRN1)
        gamma_data = bytearray([
            0xF0, 0x09, 0x13, 0x0C, 0x0D, 0x27, 0x3B, 0x44,
            0x4D, 0x0B, 0x17, 0x17, 0x1D, 0x21
        ])
        for byte in gamma_data:
            self.write_data(byte)
        
        # Command set control
        self.write_cmd(ST7796_CSCON)
        self.write_data(0xC3)
        
        self.write_cmd(ST7796_CSCON)
        self.write_data(0x96)
        
        # Display inversion
        self.write_cmd(ST7796_INVON)
        
        # Normal display on
        self.write_cmd(ST7796_NORON)
        time.sleep_ms(10)
        
        # Display on
        self.write_cmd(ST7796_DISPON)
        time.sleep_ms(100)
        
        # Clear screen
        self.clear(BLACK)
        
    def set_window(self, x0, y0, x1, y1):
        """Set drawing window"""
        # Column address set
        self.write_cmd(ST7796_CASET)
        self.write_data(x0 >> 8)
        self.write_data(x0 & 0xFF)
        self.write_data(x1 >> 8)
        self.write_data(x1 & 0xFF)
        
        # Row address set
        self.write_cmd(ST7796_RASET)
        self.write_data(y0 >> 8)
        self.write_data(y0 & 0xFF)
        self.write_data(y1 >> 8)
        self.write_data(y1 & 0xFF)
        
        # Write to RAM
        self.write_cmd(ST7796_RAMWR)
        
    def clear(self, color=BLACK):
        """Clear screen with color"""
        self.fill_rect(0, 0, self.width, self.height, color)
        
    def pixel(self, x, y, color):
        """Draw a single pixel"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.set_window(x, y, x, y)
            self.write_data(bytearray([(color >> 8) & 0xFF, color & 0xFF]))
            
    def fill_rect(self, x, y, w, h, color):
        """Fill rectangle with color"""
        if x < 0 or y < 0 or x + w > self.width or y + h > self.height:
            return
            
        self.set_window(x, y, x + w - 1, y + h - 1)
        
        # Prepare color data
        color_high = (color >> 8) & 0xFF
        color_low = color & 0xFF
        
        # Send color data
        self.cs(0)
        self.dc(1)
        
        # Send in chunks for better performance
        chunk_size = 512
        chunk = bytearray(chunk_size)
        for i in range(0, chunk_size, 2):
            chunk[i] = color_high
            chunk[i + 1] = color_low
            
        pixels = w * h
        full_chunks = pixels * 2 // chunk_size
        
        for _ in range(full_chunks):
            self.spi.write(chunk)
            
        # Send remaining pixels
        remaining = (pixels * 2) % chunk_size
        if remaining:
            self.spi.write(chunk[:remaining])
            
        self.cs(1)
        
    def draw_rect(self, x, y, w, h, color):
        """Draw rectangle outline"""
        self.draw_hline(x, y, w, color)
        self.draw_hline(x, y + h - 1, w, color)
        self.draw_vline(x, y, h, color)
        self.draw_vline(x + w - 1, y, h, color)
        
    def draw_hline(self, x, y, w, color):
        """Draw horizontal line"""
        self.fill_rect(x, y, w, 1, color)
        
    def draw_vline(self, x, y, h, color):
        """Draw vertical line"""
        self.fill_rect(x, y, 1, h, color)
        
    def draw_line(self, x0, y0, x1, y1, color):
        """Draw line using Bresenham's algorithm"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            self.pixel(x0, y0, color)
            
            if x0 == x1 and y0 == y1:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
                
    def text(self, text, x, y, color, size=1):
        """Draw text on the display using built-in font"""
        from lib.font import Font
        font = Font()
        font.draw_text(self, text, x, y, size, color)
    
    def draw_circle(self, x, y, r, color):
        """Draw circle outline"""
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        px = 0
        py = r
        
        self.pixel(x, y + r, color)
        self.pixel(x, y - r, color)
        self.pixel(x + r, y, color)
        self.pixel(x - r, y, color)
        
        while px < py:
            if f >= 0:
                py -= 1
                ddF_y += 2
                f += ddF_y
            px += 1
            ddF_x += 2
            f += ddF_x
            
            self.pixel(x + px, y + py, color)
            self.pixel(x - px, y + py, color)
            self.pixel(x + px, y - py, color)
            self.pixel(x - px, y - py, color)
            self.pixel(x + py, y + px, color)
            self.pixel(x - py, y + px, color)
            self.pixel(x + py, y - px, color)
            self.pixel(x - py, y - px, color)
            
    def fill_circle(self, x, y, r, color):
        """Fill circle with color"""
        self.draw_vline(x, y - r, 2 * r + 1, color)
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        px = 0
        py = r
        
        while px < py:
            if f >= 0:
                py -= 1
                ddF_y += 2
                f += ddF_y
            px += 1
            ddF_x += 2
            f += ddF_x
            
            self.draw_vline(x + px, y - py, 2 * py + 1, color)
            self.draw_vline(x - px, y - py, 2 * py + 1, color)
            self.draw_vline(x + py, y - px, 2 * px + 1, color)
            self.draw_vline(x - py, y - px, 2 * px + 1, color)