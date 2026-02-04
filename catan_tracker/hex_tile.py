"""
HexTile class representing a single hex on the Catan board.

A hex tile has a resource type (wood, brick, sheep, wheat, ore, desert)
and a dice number (2-12, or 0 for desert).
"""


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