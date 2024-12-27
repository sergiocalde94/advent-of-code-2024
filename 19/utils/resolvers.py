from functools import lru_cache
from pathlib import Path


def _read_and_process_file(filename: Path) -> tuple:
    """Reads and processes the input file containing towel patterns and
    desired designs.

    Args:
        filename (Path): Path to the input file.

    Returns:
        tuple: A tuple containing:
            - towel_patterns (list): A list of towel patterns as strings.
            - desired_designs (list): A list of desired designs as strings.
    """
    with open(filename) as f:
        towel_patterns_raw, desired_designs_raw = f.read().split("\n\n")

    towel_patterns = list(towel_patterns_raw.split(", "))
    desired_designs = desired_designs_raw.split()

    return towel_patterns, desired_designs

def _can_be_designed(towel_patterns: list, desired_design: str) -> bool:
    """Determines if a desired design can be created using the available
    towel patterns.

    Args:
        towel_patterns (list): A list of available towel patterns.
        desired_design (str): The desired design string.

    Returns:
        bool: True if the desired design can be created, False otherwise.
    """
    @lru_cache
    def _can_be_designed_remaining(remaining: str) -> bool:
        if not remaining:
            return True

        for towel_pattern in towel_patterns:
            if remaining.startswith(towel_pattern):
                next_remaining = remaining[len(towel_pattern):]
                if _can_be_designed_remaining(next_remaining):
                    return True

        return False

    return _can_be_designed_remaining(desired_design)

def _count_ways_designed(towel_patterns: list, desired_design: str) -> int:
    """Counts the number of ways a desired design can be created using
    the towel patterns.

    Args:
        towel_patterns (list): A list of available towel patterns.
        desired_design (str): The desired design string.

    Returns:
        int: The number of possible ways to create the desired design.
    """
    @lru_cache
    def _count_ways_designed_remaining(remaining: str) -> int:
        if not remaining:
            return 1

        total_count = 0
        for towel_pattern in towel_patterns:
            if remaining.startswith(towel_pattern):
                next_remaining = remaining[len(towel_pattern):]
                total_count += _count_ways_designed_remaining(next_remaining)

        return total_count

    return _count_ways_designed_remaining(desired_design)

def first_exercise(filename: Path):
    towel_patterns, desired_designs = _read_and_process_file(filename)

    return sum(
        _can_be_designed(towel_patterns, desired_design)
        for desired_design in desired_designs
    )

def second_exercise(filename: Path):
    towel_patterns, desired_designs = _read_and_process_file(filename)

    return sum(
        _count_ways_designed(towel_patterns, desired_design)
        for desired_design in desired_designs
    )
