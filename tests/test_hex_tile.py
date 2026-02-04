"""Tests for HexTile class."""

import unittest
from catan_tracker import HexTile


class TestHexTileCreation(unittest.TestCase):
    """Test HexTile object creation."""

    def test_create_valid_hex(self):
        """Test creating a valid hex tile."""
        hex_tile = HexTile('wood', 6)
        self.assertEqual(hex_tile.resource, 'wood')
        self.assertEqual(hex_tile.number, 6)

    def test_case_insensitive_resource(self):
        """Test resource names are case-insensitive."""
        hex_tile = HexTile('WOOD', 6)
        self.assertEqual(hex_tile.resource, 'wood')

    def test_create_desert(self):
        """Test creating a desert hex."""
        desert = HexTile('desert', 0)
        self.assertEqual(desert.resource, 'desert')
        self.assertEqual(desert.number, 0)

    def test_repr(self):
        """Test string representation."""
        hex_tile = HexTile('wood', 6)
        self.assertEqual(repr(hex_tile), "HexTile('wood', 6)")


class TestHexTileValidation(unittest.TestCase):
    """Test HexTile input validation."""

    def test_invalid_resource(self):
        """Test invalid resource type raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            HexTile('gold', 6)
        self.assertIn('Invalid resource', str(cm.exception))

    def test_number_too_high(self):
        """Test number > 12 raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            HexTile('wood', 13)
        self.assertIn('must be 0-12', str(cm.exception))

    def test_number_negative(self):
        """Test negative number raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            HexTile('wood', -1)
        self.assertIn('must be 0-12', str(cm.exception))

    def test_number_is_seven(self):
        """Test number 7 raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            HexTile('wood', 7)
        self.assertIn('cannot be 7', str(cm.exception))

    def test_number_not_integer(self):
        """Test non-integer number raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            HexTile('wood', 6.5)
        self.assertIn('must be an integer', str(cm.exception))


if __name__ == '__main__':
    unittest.main()