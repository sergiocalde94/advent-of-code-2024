import itertools as it
from collections import Counter
from functools import lru_cache, partial
from pathlib import Path


def _read_and_process_file(filename: Path) -> Counter:
    """Reads a file and processes its contents into a Counter of stones.

    Each stone is separated by a space and counted for occurrences.

    Args:
        filename (Path): Path to the file containing the stone data.

    Returns:
        Counter: A Counter object where keys are stone values (str) and
            values are their respective counts.
    """
    with open(filename) as f:
        stones = Counter(f.read().split(" "))

    return stones

@lru_cache
def _apply_rules(stone: str) -> str | list:
    """Applies transformation rules to a given stone.

    Transformation rules:
    - If the stone is "0", it transforms to "1".
    - If the stone length is even, it splits into two parts:
      - The first half as a string.
      - The second half as an integer converted back to a string.
    - If the stone length is odd, it multiplies the integer value of
        the stone by 2024.

    Args:
        stone (str): The stone to apply rules to.

    Returns:
        str | list: A transformed stone value as a string, or a list of strings 
                    if the stone is split.
    """
    if stone == "0":
        return "1"
    elif len(stone) % 2 == 0:
        half = len(stone) // 2

        return [stone[:half], str(int(stone[half:]))]
    else:
        return str(int(stone) * 2024)

def _solve(filename: Path, number_of_blinks: int):
    """Solves the stone transformation process for a given number
    of iterations (blinks).

    At each iteration:
    - Reads the current stone counts.
    - Applies the transformation rules.
    - Updates the stone counts based on the transformations.

    Args:
        filename (Path): Path to the file containing the initial stone data.
        number_of_blinks (int): The number of iterations (blinks) to perform.

    Returns:
        int: The total count of stones after all iterations.
    """
    stones = _read_and_process_file(filename)

    for _ in range(number_of_blinks):
        new_stones = Counter()
        for stone in stones:
            result = _apply_rules(stone)
            if isinstance(result, list):
                for r in result:
                    new_stones[r] += stones[stone]
            else:
                new_stones[result] += stones[stone]
        stones = new_stones

    return sum(stones.values())

first_exercise = partial(_solve, number_of_blinks=25)
second_exercise = partial(_solve, number_of_blinks=75)
