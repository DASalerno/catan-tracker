"""Tests for Settlement class."""

import unittest
import math
from catan_tracker import HexTile, Settlement, ROLL_PROBABILITIES


class TestSettlementCreation(unittest.TestCase):
    """Test Settlement object creation."""

    def test_create_settlement(self):
        """Test creating a valid settlement."""
        hexes = [HexTile('wood', 6), HexTile('brick', 8)]
        settlement = Settlement(hexes)
        self.assertEqual(len(settlement.hexes), 2)
        self.assertFalse(settlement.is_city)
        self.assertEqual(settlement.multiplier, 1)

    def test_create_city(self):
        """Test creating a city."""
        hexes = [HexTile('wood', 6)]
        city = Settlement(hexes, is_city=True)
        self.assertTrue(city.is_city)
        self.assertEqual(city.multiplier, 2)

    def test_repr_settlement(self):
        """Test settlement string representation."""
        hexes = [HexTile('wood', 6)]
        settlement = Settlement(hexes)
        self.assertEqual(repr(settlement), "Settlement(1 hexes)")

    def test_repr_city(self):
        """Test city string representation."""
        hexes = [HexTile('wood', 6)]
        city = Settlement(hexes, is_city=True)
        self.assertEqual(repr(city), "City(1 hexes)")


class TestSettlementValidation(unittest.TestCase):
    """Test Settlement input validation."""

    def test_empty_hexes(self):
        """Test empty hex list raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            Settlement([])
        self.assertIn('must touch 1-3 hexes', str(cm.exception))

    def test_too_many_hexes(self):
        """Test more than 3 hexes raises ValueError."""
        hexes = [
            HexTile('wood', 6),
            HexTile('brick', 8),
            HexTile('wheat', 9),
            HexTile('ore', 10)
        ]
        with self.assertRaises(ValueError) as cm:
            Settlement(hexes)
        self.assertIn('must touch 1-3 hexes', str(cm.exception))

    def test_invalid_hex_type(self):
        """Test non-HexTile objects raise ValueError."""
        with self.assertRaises(ValueError) as cm:
            Settlement(['wood', 'brick'])
        self.assertIn('must be HexTile objects', str(cm.exception))


class TestExpectedResources(unittest.TestCase):
    """Test expected_resources_per_roll method."""

    def test_single_hex(self):
        """Test expected resources for single hex."""
        hexes = [HexTile('wood', 6)]
        settlement = Settlement(hexes)
        expected = settlement.expected_resources_per_roll()
        self.assertAlmostEqual(expected, 5 / 36, places=4)

    def test_multiple_hexes(self):
        """Test expected resources for multiple hexes."""
        hexes = [
            HexTile('wood', 6),
            HexTile('brick', 8),
            HexTile('wheat', 9)
        ]
        settlement = Settlement(hexes)
        expected = settlement.expected_resources_per_roll()
        manual_calc = 5 / 36 + 5 / 36 + 4 / 36
        self.assertAlmostEqual(expected, manual_calc, places=4)

    def test_city_doubles_resources(self):
        """Test city produces 2x resources."""
        hexes = [HexTile('wood', 6)]
        settlement = Settlement(hexes)
        city = Settlement(hexes, is_city=True)

        settlement_expected = settlement.expected_resources_per_roll()
        city_expected = city.expected_resources_per_roll()

        self.assertAlmostEqual(city_expected, settlement_expected * 2, places=4)

    def test_desert_ignored(self):
        """Test desert hexes are ignored."""
        hexes = [HexTile('wood', 6), HexTile('desert', 0)]
        settlement = Settlement(hexes)
        expected = settlement.expected_resources_per_roll()
        self.assertAlmostEqual(expected, 5 / 36, places=4)


class TestDiversityWeighting(unittest.TestCase):
    """Test expected_resources_weighted_by_diversity method."""

    def test_single_resource_type(self):
        """Test diversity weighting with one resource type."""
        hexes = [
            HexTile('wood', 6),
            HexTile('wood', 8),
            HexTile('wood', 9)
        ]
        settlement = Settlement(hexes)
        base = settlement.expected_resources_per_roll()
        weighted = settlement.expected_resources_weighted_by_diversity()

        # Should be base × √1 = base × 1.0
        self.assertAlmostEqual(weighted, base * 1.0, places=4)

    def test_two_resource_types(self):
        """Test diversity weighting with two resource types."""
        hexes = [
            HexTile('wood', 6),
            HexTile('wood', 8),
            HexTile('brick', 9)
        ]
        settlement = Settlement(hexes)
        base = settlement.expected_resources_per_roll()
        weighted = settlement.expected_resources_weighted_by_diversity()

        # Should be base × √2
        self.assertAlmostEqual(weighted, base * math.sqrt(2), places=4)

    def test_three_resource_types(self):
        """Test diversity weighting with three resource types."""
        hexes = [
            HexTile('wood', 6),
            HexTile('brick', 8),
            HexTile('wheat', 9)
        ]
        settlement = Settlement(hexes)
        base = settlement.expected_resources_per_roll()
        weighted = settlement.expected_resources_weighted_by_diversity()

        # Should be base × √3
        self.assertAlmostEqual(weighted, base * math.sqrt(3), places=4)

    def test_desert_not_counted_in_diversity(self):
        """Test desert doesn't count toward diversity."""
        hexes = [
            HexTile('wood', 6),
            HexTile('brick', 8),
            HexTile('desert', 0)
        ]
        settlement = Settlement(hexes)
        base = settlement.expected_resources_per_roll()
        weighted = settlement.expected_resources_weighted_by_diversity()

        # Should be base × √2 (wood and brick only)
        self.assertAlmostEqual(weighted, base * math.sqrt(2), places=4)


class TestProbabilityOfResources(unittest.TestCase):
    """Test probability_of_resources_on_roll method."""

    def test_single_number(self):
        """Test probability for single number."""
        hexes = [HexTile('wood', 6)]
        settlement = Settlement(hexes)
        prob = settlement.probability_of_resources_on_roll()
        self.assertAlmostEqual(prob, ROLL_PROBABILITIES[6], places=4)

    def test_multiple_numbers(self):
        """Test probability for multiple numbers."""
        hexes = [
            HexTile('wood', 6),
            HexTile('brick', 8),
            HexTile('wheat', 9)
        ]
        settlement = Settlement(hexes)
        prob = settlement.probability_of_resources_on_roll()
        expected = ROLL_PROBABILITIES[6] + ROLL_PROBABILITIES[8] + ROLL_PROBABILITIES[9]
        self.assertAlmostEqual(prob, expected, places=4)

    def test_duplicate_numbers_not_double_counted(self):
        """Test duplicate numbers are not double-counted."""
        hexes = [
            HexTile('wood', 6),
            HexTile('sheep', 6),
            HexTile('brick', 8)
        ]
        settlement = Settlement(hexes)
        prob = settlement.probability_of_resources_on_roll()
        expected = ROLL_PROBABILITIES[6] + ROLL_PROBABILITIES[8]
        self.assertAlmostEqual(prob, expected, places=4)

    def test_desert_ignored(self):
        """Test desert is ignored in probability."""
        hexes = [HexTile('wood', 6), HexTile('desert', 0)]
        settlement = Settlement(hexes)
        prob = settlement.probability_of_resources_on_roll()
        self.assertAlmostEqual(prob, ROLL_PROBABILITIES[6], places=4)

    def test_city_same_probability_as_settlement(self):
        """Test city has same probability as settlement."""
        hexes = [HexTile('wood', 6), HexTile('brick', 8)]
        settlement = Settlement(hexes)
        city = Settlement(hexes, is_city=True)

        settlement_prob = settlement.probability_of_resources_on_roll()
        city_prob = city.probability_of_resources_on_roll()

        self.assertAlmostEqual(settlement_prob, city_prob, places=4)


if __name__ == '__main__':
    unittest.main()