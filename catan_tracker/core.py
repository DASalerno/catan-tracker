"""
Core Catan analysis functionality.

This module provides classes and functions for analyzing Settlers of Catan
settlement placements based on expected resource production.
"""

import math

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

    def expected_resources_weighted_by_diversity(self):
        """
        Calculate expected resources weighted by resource diversity.

        This metric scales expected resources by the square root of unique
        resource types, rewarding diversity while avoiding over-penalization
        of specialized settlements. Square root scaling provides diminishing
        returns - the third unique resource adds less value than the second.

        Desert hexes are excluded from the diversity count since they
        don't produce resources.

        Returns:
            float: Expected resources scaled by sqrt(diversity count)

        Example:
            >>> # Settlement with 3 different resources
            >>> hexes = [
            ...     HexTile('wood', 6),
            ...     HexTile('brick', 8),
            ...     HexTile('wheat', 9)
            ... ]
            >>> settlement = Settlement(hexes)
            >>> settlement.expected_resources_weighted_by_diversity()
            0.6728

            >>> # Settlement with 1 resource type
            >>> hexes = [
            ...     HexTile('wood', 6),
            ...     HexTile('wood', 8)
            ... ]
            >>> settlement = Settlement(hexes)
            >>> settlement.expected_resources_weighted_by_diversity()
            0.2778
        """
        # Get base expected resources per roll
        base_expected = self.expected_resources_per_roll()

        # Count unique resource types (excluding desert) using set comprehension
        resource_types = {
            hex_tile.resource
            for hex_tile in self.hexes
            if hex_tile.resource != 'desert'
        }

        # Apply square root scaling for balanced weighting
        diversity_factor = math.sqrt(len(resource_types))

        return base_expected * diversity_factor

    def probability_of_resources_on_roll(self):
        """
        Calculate probability of getting at least one resource on any given roll.

        This metric sums the probabilities of rolling any number that produces
        resources for this settlement. It does NOT double-count - if multiple
        hexes have the same number, we still only count that number once.

        Returns:
            float: Probability of getting resources (0.0 to 1.0)

        Example:
            >>> # Settlement covering three different numbers
            >>> hexes = [HexTile('wood', 6), HexTile('brick', 8), HexTile('wheat', 9)]
            >>> settlement = Settlement(hexes)
            >>> settlement.probability_of_resources_on_roll()
            0.3889  # P(6) + P(8) + P(9) = 5/36 + 5/36 + 4/36

            >>> # Settlement with duplicate numbers
            >>> hexes = [HexTile('wood', 6), HexTile('sheep', 6)]
            >>> settlement = Settlement(hexes)
            >>> settlement.probability_of_resources_on_roll()
            0.1389  # P(6) = 5/36 (not double-counted!)
        """
        # Collect unique dice numbers (excluding desert)
        unique_numbers = {
            hex_tile.number
            for hex_tile in self.hexes
            if hex_tile.number > 0
        }

        # Sum probabilities for all unique numbers
        total_probability = sum(
            ROLL_PROBABILITIES.get(number, 0)
            for number in unique_numbers
        )

        return total_probability


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
    # Test 7: Diversity Weighting Calculation
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 7: Diversity Weighting Calculation (Square Root Scaling)")
    print("=" * 70)

    # Test case 7.1: Single resource type (all wood)
    hexes = [
        HexTile('wood', 6),
        HexTile('wood', 8),
        HexTile('wood', 9)
    ]
    settlement = Settlement(hexes)
    base_expected = settlement.expected_resources_per_roll()
    weighted = settlement.expected_resources_weighted_by_diversity()
    expected_factor = math.sqrt(1)
    print(f"\nSingle resource type (all wood):")
    print(f"  Base expected: {base_expected:.4f}")
    print(f"  Weighted: {weighted:.4f}")
    print(f"  Diversity factor: √1 = {expected_factor:.4f}")
    print(f"  Should be: {base_expected * expected_factor:.4f}")
    print(f"  Match: {abs(weighted - base_expected * expected_factor) < 0.0001}")

    # Test case 7.2: Two resource types
    hexes = [
        HexTile('wood', 6),
        HexTile('wood', 8),
        HexTile('brick', 9)
    ]
    settlement = Settlement(hexes)
    base_expected = settlement.expected_resources_per_roll()
    weighted = settlement.expected_resources_weighted_by_diversity()
    expected_factor = math.sqrt(2)
    print(f"\nTwo resource types (wood, brick):")
    print(f"  Base expected: {base_expected:.4f}")
    print(f"  Weighted: {weighted:.4f}")
    print(f"  Diversity factor: √2 = {expected_factor:.4f}")
    print(f"  Should be: {base_expected * expected_factor:.4f}")
    print(f"  Match: {abs(weighted - base_expected * expected_factor) < 0.0001}")

    # Test case 7.3: Three resource types
    hexes = [
        HexTile('wood', 6),
        HexTile('brick', 8),
        HexTile('wheat', 9)
    ]
    settlement = Settlement(hexes)
    base_expected = settlement.expected_resources_per_roll()
    weighted = settlement.expected_resources_weighted_by_diversity()
    expected_factor = math.sqrt(3)
    print(f"\nThree resource types (wood, brick, wheat):")
    print(f"  Base expected: {base_expected:.4f}")
    print(f"  Weighted: {weighted:.4f}")
    print(f"  Diversity factor: √3 = {expected_factor:.4f}")
    print(f"  Should be: {base_expected * expected_factor:.4f}")
    print(f"  Match: {abs(weighted - base_expected * expected_factor) < 0.0001}")

    # Test case 7.4: With desert (should be ignored)
    hexes = [
        HexTile('wood', 6),
        HexTile('brick', 8),
        HexTile('desert', 0)
    ]
    settlement = Settlement(hexes)
    base_expected = settlement.expected_resources_per_roll()
    weighted = settlement.expected_resources_weighted_by_diversity()
    expected_factor = math.sqrt(2)
    print(f"\nWith desert (wood, brick, desert):")
    print(f"  Base expected: {base_expected:.4f}")
    print(f"  Weighted: {weighted:.4f}")
    print(f"  Diversity count: 2 (desert ignored)")
    print(f"  Diversity factor: √2 = {expected_factor:.4f}")
    print(f"  Should be: {base_expected * expected_factor:.4f}")
    print(f"  Match: {abs(weighted - base_expected * expected_factor) < 0.0001}")

    # Test case 7.5: City has same diversity as settlement
    hexes = [
        HexTile('wood', 6),
        HexTile('brick', 8),
        HexTile('wheat', 9)
    ]
    settlement = Settlement(hexes)
    city = Settlement(hexes, is_city=True)

    settlement_weighted = settlement.expected_resources_weighted_by_diversity()
    city_weighted = city.expected_resources_weighted_by_diversity()

    print(f"\nCity vs Settlement (same hexes):")
    print(f"  Settlement weighted: {settlement_weighted:.4f}")
    print(f"  City weighted: {city_weighted:.4f}")
    print(f"  City is double: {abs(city_weighted - settlement_weighted * 2) < 0.0001}")

    # Test case 7.6: Strategic comparison
    print(f"\nStrategic comparison (same base expected value):")
    specialized = Settlement([
        HexTile('wood', 6),
        HexTile('wood', 8),
        HexTile('wood', 9)
    ])
    diverse = Settlement([
        HexTile('wood', 6),
        HexTile('brick', 8),
        HexTile('wheat', 9)
    ])

    spec_base = specialized.expected_resources_per_roll()
    spec_weighted = specialized.expected_resources_weighted_by_diversity()
    div_base = diverse.expected_resources_per_roll()
    div_weighted = diverse.expected_resources_weighted_by_diversity()

    print(f"  Specialized (all wood):")
    print(f"    Base: {spec_base:.4f}, Weighted: {spec_weighted:.4f} (×√1 = ×1.00)")
    print(f"  Diverse (wood/brick/wheat):")
    print(f"    Base: {div_base:.4f}, Weighted: {div_weighted:.4f} (×√3 = ×{math.sqrt(3):.2f})")
    print(f"  Diverse is better by: {((div_weighted/spec_weighted - 1) * 100):.1f}%")
    print(f"  (Balanced: not the 200% advantage of linear multiplier)")

    # ========================================================================
    # Test 8: Probability of Resources Calculation
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 8: Probability of Resources Calculation")
    print("=" * 70)

    # Test case 8.1: Single hex
    hexes = [HexTile('wood', 6)]
    settlement = Settlement(hexes)
    probability = settlement.probability_of_resources_on_roll()
    expected_prob = ROLL_PROBABILITIES[6]
    print(f"\nSingle hex (wood-6):")
    print(f"  Probability: {probability:.4f} ({probability * 100:.2f}%)")
    print(f"  Should be: {expected_prob:.4f} ({expected_prob * 100:.2f}%)")
    print(f"  Match: {abs(probability - expected_prob) < 0.0001}")

    # Test case 8.2: Multiple hexes, different numbers
    hexes = [
        HexTile('wood', 6),
        HexTile('brick', 8),
        HexTile('wheat', 9)
    ]
    settlement = Settlement(hexes)
    probability = settlement.probability_of_resources_on_roll()
    expected_prob = ROLL_PROBABILITIES[6] + ROLL_PROBABILITIES[8] + ROLL_PROBABILITIES[9]
    print(f"\nMultiple hexes, different numbers (6, 8, 9):")
    print(f"  Probability: {probability:.4f} ({probability * 100:.2f}%)")
    print(f"  Should be: {expected_prob:.4f} ({expected_prob * 100:.2f}%)")
    print(f"  Formula: P(6) + P(8) + P(9) = 5/36 + 5/36 + 4/36")
    print(f"  Match: {abs(probability - expected_prob) < 0.0001}")

    # Test case 8.3: Duplicate numbers (critical test!)
    hexes = [
        HexTile('wood', 6),
        HexTile('sheep', 6),
        HexTile('brick', 8)
    ]
    settlement = Settlement(hexes)
    probability = settlement.probability_of_resources_on_roll()
    expected_prob = ROLL_PROBABILITIES[6] + ROLL_PROBABILITIES[8]
    print(f"\nDuplicate numbers (wood-6, sheep-6, brick-8):")
    print(f"  Probability: {probability:.4f} ({probability * 100:.2f}%)")
    print(f"  Should be: {expected_prob:.4f} ({expected_prob * 100:.2f}%)")
    print(f"  Should NOT double-count the 6: P(6) + P(8), not P(6) + P(6) + P(8)")
    print(f"  Match: {abs(probability - expected_prob) < 0.0001}")

    # Test case 8.4: With desert (should be ignored)
    hexes = [
        HexTile('wood', 6),
        HexTile('desert', 0),
        HexTile('brick', 8)
    ]
    settlement = Settlement(hexes)
    probability = settlement.probability_of_resources_on_roll()
    expected_prob = ROLL_PROBABILITIES[6] + ROLL_PROBABILITIES[8]
    print(f"\nWith desert (wood-6, desert-0, brick-8):")
    print(f"  Probability: {probability:.4f} ({probability * 100:.2f}%)")
    print(f"  Should be: {expected_prob:.4f} ({expected_prob * 100:.2f}%)")
    print(f"  Desert (0) ignored: P(6) + P(8)")
    print(f"  Match: {abs(probability - expected_prob) < 0.0001}")

    # Test case 8.5: City vs settlement (same probability)
    hexes = [
        HexTile('wood', 6),
        HexTile('brick', 8),
        HexTile('wheat', 9)
    ]
    settlement = Settlement(hexes)
    city = Settlement(hexes, is_city=True)

    settlement_prob = settlement.probability_of_resources_on_roll()
    city_prob = city.probability_of_resources_on_roll()

    print(f"\nCity vs Settlement (same hexes):")
    print(f"  Settlement probability: {settlement_prob:.4f} ({settlement_prob * 100:.2f}%)")
    print(f"  City probability: {city_prob:.4f} ({city_prob * 100:.2f}%)")
    print(f"  Same probability: {abs(settlement_prob - city_prob) < 0.0001}")
    print(f"  (City gets 2x resources when rolling these numbers, but same chance)")

    # Test case 8.6: Best and worst case scenarios
    best_hexes = [
        HexTile('wood', 6),
        HexTile('brick', 8),
        HexTile('wheat', 5)
    ]
    worst_hexes = [
        HexTile('ore', 2),
        HexTile('wheat', 12),
        HexTile('desert', 0)
    ]

    best = Settlement(best_hexes)
    worst = Settlement(worst_hexes)

    best_prob = best.probability_of_resources_on_roll()
    worst_prob = worst.probability_of_resources_on_roll()

    print(f"\nBest vs Worst case:")
    print(f"  Best (6, 8, 5): {best_prob:.4f} ({best_prob * 100:.2f}%)")
    print(f"  Worst (2, 12, desert): {worst_prob:.4f} ({worst_prob * 100:.2f}%)")
    print(f"  Best is {(best_prob / worst_prob):.1f}x more likely to get resources")

    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "=" * 70)
    print("All tests complete!")
    print("=" * 70)
