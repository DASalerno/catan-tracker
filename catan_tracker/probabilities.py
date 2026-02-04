"""
Probability distributions for Catan dice rolls.

This module contains constants related to probability calculations
for the game of Catan, specifically the 2d6 dice roll distribution.
"""

# Dice roll probabilities for 2d6
ROLL_PROBABILITIES = {
    2: 1 / 36,  # 2.78%
    3: 2 / 36,  # 5.56%
    4: 3 / 36,  # 8.33%
    5: 4 / 36,  # 11.11%
    6: 5 / 36,  # 13.89%
    7: 6 / 36,  # 16.67%
    8: 5 / 36,  # 13.89%
    9: 4 / 36,  # 11.11%
    10: 3 / 36,  # 8.33%
    11: 2 / 36,  # 5.56%
    12: 1 / 36,  # 2.78%
}


def validate_probabilities():
    """
    Validate that probabilities sum to 1.0.

    Returns:
        bool: True if valid

    Raises:
        ValueError: If probabilities don't sum to 1.0
    """
    total = sum(ROLL_PROBABILITIES.values())
    if abs(total - 1.0) > 0.0001:
        raise ValueError(f"Probabilities sum to {total}, expected 1.0")
    return True


# Validate on import
validate_probabilities()