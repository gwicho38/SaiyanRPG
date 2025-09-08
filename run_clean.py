#!/usr/bin/env python3
"""Clean launcher for SaiyanQuest GTA that suppresses warnings"""

import os
import sys
import warnings
import subprocess

# Suppress all warnings
warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'

# Clear problematic environment variable
if 'VIRTUAL_ENV' in os.environ and 'SaiyanRPG' in os.environ['VIRTUAL_ENV']:
    del os.environ['VIRTUAL_ENV']

# Import and run the game
try:
    from saiyanquest.gta_game import main
    if __name__ == '__main__':
        main()
except ImportError as e:
    print(f"Error importing game: {e}")
    sys.exit(1)