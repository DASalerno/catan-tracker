"""Tests for probabilities module."""

import unittest
from catan_tracker.probabilities import ROLL_PROBABILITIES


class TestProbabilities(unittest.TestCase):
    """Test probability constants."""

    def test_probabilities_sum_to_one(self):
        """Verify all probabilities sum to 1.0."""
        total = sum(ROLL_PROBABILITIES.values())
        self.assertAlmostEqual(total, 1.0, places=10)

    def test_all_numbers_present(self):
        """Verify all numbers 2-12 are in dictionary."""
        expected_numbers = set(range(2, 13))
        actual_numbers = set(ROLL_PROBABILITIES.keys())
        self.assertEqual(actual_numbers, expected_numbers)

    def test_seven_most_likely(self):
        """Verify 7 has highest probability."""
        max_prob = max(ROLL_PROBABILITIES.values())
        self.assertEqual(ROLL_PROBABILITIES[7], max_prob)
        self.assertAlmostEqual(max_prob, 6 / 36)

    def test_symmetry(self):
        """Verify probability distribution is symmetric."""
        self.assertEqual(ROLL_PROBABILITIES[2], ROLL_PROBABILITIES[12])
        self.assertEqual(ROLL_PROBABILITIES[3], ROLL_PROBABILITIES[11])
        self.assertEqual(ROLL_PROBABILITIES[4], ROLL_PROBABILITIES[10])
        self.assertEqual(ROLL_PROBABILITIES[5], ROLL_PROBABILITIES[9])
        self.assertEqual(ROLL_PROBABILITIES[6], ROLL_PROBABILITIES[8])


if __name__ == '__main__':
    unittest.main()