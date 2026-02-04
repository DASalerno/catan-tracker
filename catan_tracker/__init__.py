"""
Catan Tracker - Settlement Analysis Package

This package provides tools for analyzing Settlers of Catan settlement
placements based on expected resource production.

Main classes:
    - HexTile: Represents a hex tile (resource + number)
    - Settlement: Represents a settlement/city with analysis methods

Constants:
    - ROLL_PROBABILITIES: 2d6 dice probability distribution
"""

__version__ = '0.1.0'
__author__ = 'Domingo Salerno'

# Import main classes and constants for easy access
from catan_tracker.probabilities import ROLL_PROBABILITIES
from catan_tracker.hex_tile import HexTile
from catan_tracker.settlement import Settlement

# Define what's exported when someone does: from catan_tracker import *
__all__ = [
    'ROLL_PROBABILITIES',
    'HexTile',
    'Settlement',
]