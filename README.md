# Muslim Companion

**A comprehensive Islamic prayer times and calendar application for Raspberry Pi Pico**

## 📋 Project Overview

**Name:** Muslim Companion  
**Language:** MicroPython  
**Platform:** Raspberry Pi Pico 2 W/WH  
**Hardware:** GeeekPi GPIO Expansion Module with 3.5" Touch Screen  
**Author:** Amr Salem  

## 🚀 Features

### Prayer Times
- **Accurate prayer calculations** using astronomical algorithms
- **Multiple calculation methods** (ISNA, MWL, Mecca)
- **Automatic prayer alerts** with configurable buzzer
- **Next prayer countdown** display
- **Location-based calculations** for major US cities
- **12h/24h time format** support

### Hijri Calendar
- **Current Hijri date** display
- **Islamic events tracking** (Ramadan, Eid, Ashura, etc.)
- **Event countdown** with days remaining
- **Accurate date conversion** using Umm al-Qura calendar

### User Interface
- **Mobile-style navigation** with bottom tabs
- **Touch screen support** with intuitive interface
- **Joystick navigation** for all screens
- **Physical button controls** with audio feedback
- **Settings management** with easy configuration

### Hardware Integration
- **3.5" ST7796 Display** (320x480 pixels)
- **GT911 Capacitive Touch** controller
- **5-way Analog Joystick** navigation
- **Physical buttons** for quick access
- **Buzzer alerts** for prayer times and feedback
- **Modular hardware design** for easy expansion

## 🛠 Hardware Requirements

- **Raspberry Pi Pico 2 W/WH**
- **GeeekPi GPIO Expansion Module**
- **3.5" Touch Screen Display** (ST7796 driver)
- **Capacitive Touch Controller** (GT911)
- **5-way Joystick**
- **Physical Buttons** (2x)
- **Buzzer** for audio alerts

## 📱 Screenshots

### Main Prayer Times Screen
*[Screenshot placeholder - Prayer times display with current time and next prayer]*

### Hijri Events Calendar
*[Screenshot placeholder - Islamic calendar with current Hijri date and upcoming events]*

### Settings Menu
*[Screenshot placeholder - Configuration screen with navigation options]*

### Mobile-Style Navigation
*[Screenshot placeholder - Bottom navigation tabs in action]*

## 🗂 Project Structure

```
pico-muslim-prayer/
├── main.py                 # Main application entry point
├── boot.py                 # MicroPython boot configuration
├── hardware_config.py      # Hardware abstraction selector
├── prayer_config.py        # Configuration management
├── README.md              # This file
└── lib/
    ├── st7796.py          # Display driver
    ├── gt911.py           # Touch controller driver
    ├── font.py            # Text rendering
    ├── prayer_times.py    # Prayer calculations
    ├── hijri_calendar.py  # Islamic calendar
    ├── prayer_settings.py # Settings management
    ├── ui_manager.py      # User interface
    ├── joystick.py        # Joystick input handler
    ├── buttons.py         # Button input handler
    └── geekpi_gpio.py     # GeeekPi hardware abstraction
```

## ⚙️ Configuration

### Default Settings
- **Location:** Tampa, FL
- **Calculation Method:** ISNA
- **Time Format:** 12h
- **Buzzer:** Enabled
- **Alert Duration:** 5 seconds

### Supported Cities
Major US cities with accurate coordinates and timezones:
- New York, Los Angeles, Chicago, Houston
- Phoenix, Philadelphia, San Antonio, San Diego
- Dallas, Detroit, Miami, Boston, and more

### Prayer Calculation Methods
- **ISNA** - Islamic Society of North America
- **MWL** - Muslim World League  
- **Mecca** - Umm Al-Qura, Mecca

## 🎮 Navigation

### Touch Controls
- **Bottom tabs** - Switch between Prayer, Events, Settings
- **Touch settings items** - Modify configurations
- **Swipe gestures** - Navigate through options

### Joystick Controls
- **Left/Right** - Switch between tabs
- **Up/Down** - Navigate menu items
- **Center press** - Select/confirm
- **Directional navigation** - Full menu control

### Button Controls
- **Button 1** - Open settings menu
- **Button 2** - Refresh/back functions
- **Audio feedback** - Confirmation beeps

## 🔧 Installation

1. **Setup MicroPython** on Raspberry Pi Pico 2 W/WH
2. **Connect hardware** according to pin configuration
3. **Upload project files** to the Pico
4. **Configure settings** for your location
5. **Run the application** - `python main.py`

## 📋 Pin Configuration

### Display (ST7796)
- **SPI0:** CLK=GP2, MOSI=GP3, CS=GP5
- **Control:** DC=GP6, RST=GP7

### Touch (GT911)  
- **I2C0:** SDA=GP8, SCL=GP9
- **Control:** RST=GP10, INT=GP11

### Input Controls
- **Joystick:** X=GP27(ADC1), Y=GP26(ADC0), SW=GP15
- **Buttons:** BTN1=GP14, BTN2=GP15
- **Buzzer:** GP13

## 🎯 Key Features

### Modular Design
- **Hardware abstraction** for different GPIO modules
- **Vendor-specific configurations** (GeeekPi, Waveshare, custom)
- **Easy hardware switching** via configuration

### Accurate Calculations
- **Astronomical algorithms** for precise prayer times
- **Location-aware** calculations with timezone support
- **Multiple madhabs** and calculation methods

### User Experience
- **Mobile-like interface** with familiar navigation
- **Consistent input methods** - touch, joystick, buttons
- **Visual and audio feedback** for all interactions
- **Time format preferences** and customization

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is open source. Please check the license file for details.

## 🙏 Acknowledgments

- **Islamic prayer time calculations** based on established astronomical methods
- **Hijri calendar conversion** using Umm al-Qura calendar system
- **Hardware drivers** adapted for MicroPython compatibility
- **Community support** for Islamic applications and open source development

---

*Built with love for the Muslim community to help with daily prayers and Islamic calendar tracking.*