"""
Core Catan analysis functionality.

This module provides classes and functions for analyzing Settlers of Catan
settlement placements based on expected resource production.
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

    # Valid resource types
    VALID_RESOURCES = {'wood', 'brick', 'sheep', 'wheat', 'ore', 'desert'}

    def __init__(self, resource, number):
        """
        Create a new hex tile.

        Args:
            resource (str): Type of resource ('wood', 'brick', 'sheep',
                           'wheat', 'ore', 'desert')
            number (int): Dice number on the tile (2-12, or 0 for desert)

        Raises:
            ValueError: If resource or number is invalid

        Examples:
            >>> wood_hex = HexTile('wood', 6)
            >>> desert = HexTile('desert', 0)
        """
        # Convert to lowercase for case-insensitive comparison
        resource = resource.lower()

        # Validate resource type
        if resource not in self.VALID_RESOURCES:
            raise ValueError(
                f"Invalid resource '{resource}'. "
                f"Must be one of: {', '.join(sorted(self.VALID_RESOURCES))}"
            )

        # Validate number is an integer
        if not isinstance(number, int):
            raise ValueError(
                f"Number must be an integer, got {type(number).__name__}"
            )

        # Validate number range
        if number < 0 or number > 12:
            raise ValueError(f"Number must be 0-12, got {number}")

        # Validate number is not 7 (no hex has a 7 in Catan)
        if number == 7:
            raise ValueError("Number cannot be 7 (robber!)")

        # All valid, store the data
        self.resource = resource
        self.number = number

    def __repr__(self):
        """Return a string representation of this hex tile."""
        return f"HexTile('{self.resource}', {self.number})"


class Settlement:
    """Represents a settlement or city placement in Catan."""

    def __init__(self, hexes, is_city=False):
        """
        Create a new settlement.

        Args:
            hexes (list): List of HexTile objects adjacent to this settlement
                         (maximum 3)
            is_city (bool): Whether this is a city (default: False)

        Raises:
            ValueError: If hexes is invalid

        Examples:
            >>> hexes = [HexTile('wood', 6), HexTile('brick', 8)]
            >>> settlement = Settlement(hexes)
            >>> city = Settlement(hexes, is_city=True)
        """
        # Validate hexes is a list
        if not isinstance(hexes, list):
            raise ValueError(
                f"hexes must be a list, got {type(hexes).__name__}"
            )

        # Validate settlement can have at most 3 hexes
        if len(hexes) > 3:
            raise ValueError(
                f"A settlement can touch at most 3 hexes, got {len(hexes)}"
            )

        # Validate all items are HexTile objects
        for i, hex_tile in enumerate(hexes):
            if not isinstance(hex_tile, HexTile):
                raise ValueError(
                    f"All hexes must be HexTile objects. "
                    f"Item {i} is {type(hex_tile).__name__}"
                )

        # All valid, store the data
        self.hexes = hexes
        self.is_city = is_city
        self.multiplier = 2 if is_city else 1

    def __repr__(self):
        """Return a string representation of this settlement."""
        settlement_type = "City" if self.is_city else "Settlement"
        return f"{settlement_type}({len(self.hexes)} hexes)"

    def expected_resources_per_roll(self):
        """
        Calculate expected resources per roll.

        Returns:
            float: Expected number of resources per dice roll

        Example:
            >>> hexes = [HexTile('wood', 6), HexTile('brick', 8)]
            >>> settlement = Settlement(hexes)
            >>> settlement.expected_resources_per_roll()
            0.2778
        """
        total = 0.0

        for hex_tile in self.hexes:
            # Skip desert hexes (number 0)
            if hex_tile.number > 0:
                # Get probability for this number
                prob = ROLL_PROBABILITIES.get(hex_tile.number, 0)
                # Add to total, accounting for city multiplier
                total += prob * self.multiplier

        return total


# ============================================================================
# TEST CODE - Run this file directly to test the classes
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("CATAN TRACKER - Core Module Tests")
    print("=" * 70)

    # ========================================================================
    # Test 1: Dice Probabilities
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 1: Dice Probabilities")
    print("=" * 70)

    # Verify probabilities sum to 1.0
    total_prob = sum(ROLL_PROBABILITIES.values())
    print(f"\nTotal probability: {total_prob:.10f}")
    print(f"Should be 1.0: {abs(total_prob - 1.0) < 0.0001}")

    # Show the distribution
    print("\nDice Roll Probabilities:")
    for number, prob in sorted(ROLL_PROBABILITIES.items()):
        print(f"  {number:2d}: {prob:.4f} ({prob*100:5.2f}%)")

    # ========================================================================
    # Test 2: HexTile Creation
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 2: HexTile Creation")
    print("=" * 70)

    # Valid hex tiles
    wood_hex = HexTile('wood', 6)
    brick_hex = HexTile('brick', 8)
    desert = HexTile('desert', 0)

    print(f"\nWood hex: {wood_hex}")
    print(f"Brick hex: {brick_hex}")
    print(f"Desert: {desert}")
    print(f"Different objects: {wood_hex is not brick_hex}")

    # Case insensitive
    wood_upper = HexTile('WOOD', 6)
    print(f"\nCase insensitive works: {wood_upper}")

    # ========================================================================
    # Test 3: HexTile Validation
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 3: HexTile Validation")
    print("=" * 70)

    # Invalid resource
    try:
        invalid_hex = HexTile('gold', 6)
        print("\n✗ Should have raised ValueError for invalid resource")
    except ValueError as e:
        print(f"\n✓ Caught invalid resource: {e}")

    # Invalid number (too high)
    try:
        invalid_hex = HexTile('wood', 13)
        print("\n✗ Should have raised ValueError for number too high")
    except ValueError as e:
        print(f"\n✓ Caught invalid number: {e}")

    # Number is 7
    try:
        invalid_hex = HexTile('wood', 7)
        print("\n✗ Should have raised ValueError for number 7")
    except ValueError as e:
        print(f"\n✓ Caught number 7: {e}")

    # ========================================================================
    # Test 4: Settlement Creation
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 4: Settlement Creation")
    print("=" * 70)

    # Create hex tiles
    hexes = [
        HexTile('wood', 6),
        HexTile('brick', 8),
        HexTile('wheat', 9)
    ]

    # Create settlement
    settlement = Settlement(hexes)
    print(f"\nSettlement: {settlement}")
    print(f"  Is city: {settlement.is_city}")
    print(f"  Multiplier: {settlement.multiplier}")
    print(f"  Number of hexes: {len(settlement.hexes)}")

    # Create city
    city = Settlement(hexes, is_city=True)
    print(f"\nCity: {city}")
    print(f"  Is city: {city.is_city}")
    print(f"  Multiplier: {city.multiplier}")

    # ========================================================================
    # Test 5: Settlement Validation
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 5: Settlement Validation")
    print("=" * 70)

    # Too many hexes
    try:
        too_many_hexes = [
            HexTile('wood', 6),
            HexTile('brick', 8),
            HexTile('wheat', 9),
            HexTile('ore', 10)
        ]
        invalid_settlement = Settlement(too_many_hexes)
        print("\n✗ Should have raised ValueError for too many hexes")
    except ValueError as e:
        print(f"\n✓ Caught too many hexes: {e}")

    # Wrong type in list
    try:
        invalid_settlement = Settlement(['wood', 'brick'])
        print("\n✗ Should have raised ValueError for wrong type")
    except ValueError as e:
        print(f"\n✓ Caught wrong type: {e}")

    # ========================================================================
    # Test 6: Expected Resources Calculation
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 6: Expected Resources Calculation")
    print("=" * 70)

    # Test case 1: Single hex
    hexes = [HexTile('wood', 6)]
    settlement = Settlement(hexes)
    expected = settlement.expected_resources_per_roll()
    print(f"\nSingle hex (wood-6):")
    print(f"  Expected: {expected:.4f}")
    print(f"  Should be: {5/36:.4f} (5/36)")
    print(f"  Match: {abs(expected - 5/36) < 0.0001}")

    # Test case 2: Multiple hexes
    hexes = [
        HexTile('wood', 6),
        HexTile('brick', 8),
        HexTile('wheat', 9)
    ]
    settlement = Settlement(hexes)
    expected = settlement.expected_resources_per_roll()
    manual_calc = 5/36 + 5/36 + 4/36
    print(f"\nMultiple hexes (6, 8, 9):")
    print(f"  Expected: {expected:.4f}")
    print(f"  Should be: {manual_calc:.4f} (5/36 + 5/36 + 4/36)")
    print(f"  Match: {abs(expected - manual_calc) < 0.0001}")

    # Test case 3: City vs settlement
    city = Settlement(hexes, is_city=True)
    city_expected = city.expected_resources_per_roll()
    print(f"\nCity (same hexes):")
    print(f"  Expected: {city_expected:.4f}")
    print(f"  Should be double: {expected * 2:.4f}")
    print(f"  Match: {abs(city_expected - expected * 2) < 0.0001}")

    # Test case 4: With desert
    hexes_with_desert = [
        HexTile('wood', 6),
        HexTile('desert', 0)
    ]
    settlement = Settlement(hexes_with_desert)
    expected = settlement.expected_resources_per_roll()
    print(f"\nWith desert (wood-6, desert-0):")
    print(f"  Expected: {expected:.4f}")
    print(f"  Should ignore desert: {5/36:.4f}")
    print(f"  Match: {abs(expected - 5/36) < 0.0001}")

    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "=" * 70)
    print("All tests complete!")
    print("=" * 70)