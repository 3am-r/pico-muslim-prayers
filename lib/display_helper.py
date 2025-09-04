"""
Display helper functions for text rendering
"""

from lib.font import Font

def draw_text(display, text, x, y, color, size=1):
    """Draw text on display using Font class"""
    font = Font()
    font.draw_text(display, text, x, y, size, color)

def draw_text_centered(display, text, y, width, color, size=1):
    """Draw centered text"""
    font = Font()
    text_width = font.get_text_width(text, size)
    x = (width - text_width) // 2
    font.draw_text(display, text, x, y, size, color)