"""
Hardware Configuration Selector
Allows switching between different hardware vendors
"""

# Select your hardware vendor here
# Available options: 'geekpi', 'waveshare', 'custom'
HARDWARE_VENDOR = 'geekpi'

def get_hardware():
    """
    Returns the appropriate hardware abstraction based on configuration
    """
    if HARDWARE_VENDOR == 'geekpi':
        from lib.geekpi_gpio import GeeekPiHardware
        return GeeekPiHardware()
    elif HARDWARE_VENDOR == 'waveshare':
        # Future implementation
        # from lib.waveshare_gpio import WaveshareHardware
        # return WaveshareHardware()
        raise NotImplementedError("Waveshare hardware not implemented yet")
    elif HARDWARE_VENDOR == 'custom':
        # Future implementation
        # from lib.custom_gpio import CustomHardware
        # return CustomHardware()
        raise NotImplementedError("Custom hardware not implemented yet")
    else:
        raise ValueError(f"Unknown hardware vendor: {HARDWARE_VENDOR}")