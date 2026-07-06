#!/usr/bin/env python3
"""
Weather Dashboard Main Entry Point
Run this script to start the weather dashboard application
"""

import sys
import os

# Add the weather_dashboard directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from weather_dashboard.ui import main

if __name__ == "__main__":
    main()
