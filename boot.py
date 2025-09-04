"""
Boot script for MicroPython
Adds lib folder to the module search path
"""

import sys

# Add lib folder to the path
if 'lib' not in sys.path:
    sys.path.append('lib')
    print("Boot: Added lib to sys.path")