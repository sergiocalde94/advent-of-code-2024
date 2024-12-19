import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Button:
    """Represents a button on the machine.

    Attributes:
        right (int): The X-coordinate increment when the button is pressed.
        forward (int): The Y-coordinate increment when the button is pressed.
    """
    right: int
    forward: int


@dataclass
class Machine:
    """Represents a machine with two buttons and a prize location.

    Attributes:
        button_a (Button): The first button on the machine.
        button_b (Button): The second button on the machine.
        prize (tuple): The coordinates (X, Y) of the prize location.
    """
    button_a: Button
    button_b: Button
    prize: tuple


REGEX_BUTTON_A = re.compile(r"Button A: X\+(\d+), Y\+(\d+)")
REGEX_BUTTON_B = re.compile(r"Button B: X\+(\d+), Y\+(\d+)")
REGEX_PRIZE = re.compile(r"Prize: X=(\d+), Y=(\d+)")

PRICE_TOKEN_A = 3
PRICE_TOKEN_B = 1

ESTIMATED_MAX_TIMES = 100

def _read_and_process_file(filename: Path):
    """Reads and processes the input file to create a list of Machine objects.

    The file contains definitions of machines, where each machine specifies:
    - Button A's increments for X and Y.
    - Button B's increments for X and Y.
    - The prize's coordinates (X, Y).

    Args:
        filename (Path): Path to the input file.

    Returns:
        list: A list of Machine objects parsed from the file.
    """
    with open(filename) as f:
        machines = f.read().split("\n\n")

    machines = [
        Machine(
            button_a=Button(
                int(REGEX_BUTTON_A.search(machine).group(1)),
                int(REGEX_BUTTON_A.search(machine).group(2)),
            ),
            button_b=Button(
                int(REGEX_BUTTON_B.search(machine).group(1)),
                int(REGEX_BUTTON_B.search(machine).group(2)),
            ),
            prize=(
                int(REGEX_PRIZE.search(machine).group(1)),
                int(REGEX_PRIZE.search(machine).group(2)),
            ),
        )
        for machine in machines
    ]

    return machines


def _best_play(machine: Machine, use_estimation: bool = True) -> int:
    """Calculates the optimal play cost to reach the prize using the machine's
    buttons.

    Solves a system of linear equations to determine the number of times each
    button must be pressed to reach the prize. If no valid integer solution
    exists, returns a cost of 0.

    Args:
        machine (Machine): The machine to solve for.
        use_estimation (bool, optional): Whether to use an estimation approach.
            Defaults to True.

    Returns:
        int: The total cost in tokens to reach the prize, or 0 if no solution
            exists.
    """
    prize_x, prize_y = machine.prize

    right_a = machine.button_a.right
    right_b = machine.button_b.right
    forward_a = machine.button_a.forward
    forward_b = machine.button_b.forward

    determinant = right_a * forward_b - forward_a * right_b

    x = (prize_x * forward_b - prize_y * right_b) / determinant
    y = (right_a * prize_y - forward_a * prize_x) / determinant

    if x != int(x) or y != int(y):
        return 0

    solution_x = int(x) * PRICE_TOKEN_A
    solution_y = int(y) * PRICE_TOKEN_B

    return solution_x + solution_y

def _unit_conversion(machine: Machine) -> Machine:
    """Converts the prize coordinates by adding a large offset.

    This transformation adjusts the prize location to ensure numerical stability
    or compatibility with other operations.

    Args:
        machine (Machine): The machine whose prize coordinates are to be
            converted.

    Returns:
        Machine: A new Machine object with adjusted prize coordinates.
    """
    return Machine(
        button_a=machine.button_a,
        button_b=machine.button_b,
        prize=(
            machine.prize[0] + 10_000_000_000_000,
            machine.prize[1] + 10_000_000_000_000,
        )
    )

def first_exercise(filename: Path):
    machines = _read_and_process_file(filename)

    return sum(
        _best_play(machine)
        for machine in machines
    )


def second_exercise(filename: Path):
    machines = _read_and_process_file(filename)

    return sum(
        _best_play(
            _unit_conversion(machine), use_estimation=False
        )
        for machine in machines
    )
