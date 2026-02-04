"""
Settlement class for analyzing Catan settlement placements.

A settlement can be built at an intersection touching up to 3 hex tiles.
This module provides methods to calculate various metrics about settlement quality.
"""

import math
from catan_tracker.probabilities import ROLL_PROBABILITIES
from catan_tracker.hex_tile import HexTile


class Settlement:
    """Represents a settlement or city placement in Catan."""

    def __init__(self, hexes, is_city=False):
        """
        Create a new settlement.

        Args:
            hexes (list): List of HexTile objects adjacent to this settlement
                         (1-3 hexes)
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

        # Validate settlement can have 1-3 hexes
        if len(hexes) < 1 or len(hexes) > 3:
            raise ValueError(
                f"A settlement must touch 1-3 hexes, got {len(hexes)}"
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
            >>> hexes = [
            ...     HexTile('wood', 6),
            ...     HexTile('brick', 8),
            ...     HexTile('wheat', 9)
            ... ]
            >>> settlement = Settlement(hexes)
            >>> settlement.expected_resources_weighted_by_diversity()
            0.6728
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
        resources for this settlement. Numbers are deduplicated - if multiple
        hexes share the same number, it only counts once (since you either
        roll that number or you don't).

        Returns:
            float: Probability of getting resources (0.0 to 1.0)

        Example:
            >>> hexes = [
            ...     HexTile('wood', 6),
            ...     HexTile('brick', 8),
            ...     HexTile('wheat', 9)
            ... ]
            >>> settlement = Settlement(hexes)
            >>> settlement.probability_of_resources_on_roll()
            0.3889
        """
        # Collect unique dice numbers (excluding desert/0)
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