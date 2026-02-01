class HexTile:
    """Represents a single hex tile on the Catan board."""

    # Class attribute: probability of each dice roll (2d6)
    ROLL_PROBABILITIES = {
        2: 1 / 36,
        3: 2 / 36,
        4: 3 / 36,
        5: 4 / 36,
        6: 5 / 36,
        7: 6 / 36,
        8: 5 / 36,
        9: 4 / 36,
        10: 3 / 36,
        11: 2 / 36,
        12: 1 / 36,
    }

    # Valid resources in the game
    VALID_RESOURCES = {'wood', 'brick', 'sheep', 'wheat', 'ore', 'desert'}

    def __init__(self, resource, number):
        """
        Create a new hex tile.

        Args:
            resource: The resource type ('wood', 'brick', 'sheep', 'wheat', 'ore', or 'desert')
            number: The dice number on this tile (2-12, or None for desert)
        """
        # Validate inputs
        if resource not in self.VALID_RESOURCES:
            raise ValueError(f"Invalid resource: {resource}. Must be one of {self.VALID_RESOURCES}")

        if resource == 'desert':
            self.number = None
        else:
            if number is None or number < 2 or number > 12 or number == 7:
                raise ValueError(f"Invalid number: {number}. Must be 2-6 or 8-12")
            self.number = number

        self.resource = resource

    def probability(self):
        """Return the probability this tile produces on any given roll."""
        if self.resource == 'desert' or self.number is None:
            return 0
        return self.ROLL_PROBABILITIES[self.number]

    def __repr__(self):
        """String representation for debugging."""
        return f"HexTile({self.resource!r}, {self.number})"

class Settlement:
    """Represents a settlement location (intersection of up to 3 hexes)."""

    def __init__(self, hex_tiles):
        """
        Create a settlement from adjacent hex tiles.

        Args:
            hex_tiles: A list of HexTile objects (1-3 tiles)
        """
        if not hex_tiles:
            raise ValueError("Settlement must have at least one adjacent hex")
        if len(hex_tiles) > 3:
            raise ValueError("Settlement can have at most 3 adjacent hexes")

        self.hex_tiles = hex_tiles

    def expected_resources_per_roll(self):
        """
        Calculate expected number of resources per dice roll.
        This is the sum of probabilities of all adjacent hexes.
        """
        return sum(tile.probability() for tile in self.hex_tiles)

    def resource_diversity(self):
        """
        Return the set of unique resources this settlement can produce.
        Excludes desert.
        """
        resources = set()
        for tile in self.hex_tiles:
            if tile.resource != 'desert':
                resources.add(tile.resource)
        return resources

    def probability_of_any_resource(self):
        """
        Calculate probability of getting at least one resource on any roll.
        Uses inclusion-exclusion principle for overlapping dice numbers.
        """
        # Get all unique numbers on non-desert tiles
        numbers = set()
        for tile in self.hex_tiles:
            if tile.number is not None:
                numbers.add(tile.number)

        # Sum probabilities for each unique number
        total_prob = 0
        for number in numbers:
            total_prob += HexTile.ROLL_PROBABILITIES[number]

        return total_prob

    def __repr__(self):
        return f"Settlement({self.hex_tiles})"