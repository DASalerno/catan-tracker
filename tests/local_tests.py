# test_import.py (recreate temporarily)
from catan_tracker.hex_tile import HexTile

# Test creation
wood_hex = HexTile('wood', 6)
print(f"Created: {wood_hex}")

# Test validation
try:
    invalid = HexTile('gold', 6)
except ValueError as e:
    print(f"Caught error: {e}")

print("HexTile works!")