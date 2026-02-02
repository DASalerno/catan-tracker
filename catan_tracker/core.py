"""
Core Catan analysis functionality.
"""

# Dice roll probabilities for 2d6
ROLL_PROBABILITIES = {
    2: 1/36,   # 2.78%
    3: 2/36,   # 5.56%
    4: 3/36,   # 8.33%
    5: 4/36,   # 11.11%
    6: 5/36,   # 13.89%
    7: 6/36,   # 16.67%
    8: 5/36,   # 13.89%
    9: 4/36,   # 11.11%
    10: 3/36,  # 8.33%
    11: 2/36,  # 5.56%
    12: 1/36,  # 2.78%
}

class HexTile:
    """Represents a single hex tile on the Catan board."""

    def __init__(self, resource, number):
        """
        Create a new hex tile.

        Args:
            resource (str): Type of resource ('wood', 'brick', 'sheep', 'wheat', 'ore', 'desert')
            number (int): Dice number on the tile (2-12, or 0 for desert)

        Examples:
            >>> wood_hex = HexTile('wood', 6)
            >>> desert = HexTile('desert', 0)
        """
        self.resource = resource
        self.number = number


if __name__ == '__main__':
    print("=" * 50)
    print("Testing HexTile Class")
    print("=" * 50)

    # Create some hex tiles
    wood_hex = HexTile('wood', 6)
    brick_hex = HexTile('brick', 8)
    desert = HexTile('desert', 0)

    # Test they were created correctly
    print(f"\nWood hex: {wood_hex.resource}, {wood_hex.number}")
    print(f"Brick hex: {brick_hex.resource}, {brick_hex.number}")
    print(f"Desert: {desert.resource}, {desert.number}")

    # Verify they're different objects
    print(f"\nWood and brick are different objects: {wood_hex is not brick_hex}")