import operator
from collections import defaultdict
from functools import cache, partial
from pathlib import Path

OPERATIONS = [
    partial(operator.mul, 2**6),
    lambda secret_number: operator.floordiv(secret_number, 2**5),
    partial(operator.mul, 2**11)
]

PRUNE_NUMBER = 16_777_216
N_ROUNDS = 2_000
COMBINATIONS_LENGTH = 4

def _read_and_process_file(filename: Path) -> tuple:
    """Reads and processes the input file containing initial secret numbers.

    Args:
        filename (Path): Path to the input file.

    Returns:
        list: A list of integers representing the initial secret numbers.
    """
    with open(filename) as f:
        initial_secret_numbers = list(map(int, f.read().split()))

    return initial_secret_numbers

def _mix(number: int, secret: int) -> int:
    """Mixes a number with a secret using XOR.

    Args:
        number (int): The input number.
        secret (int): The secret number.

    Returns:
        int: The mixed number after applying XOR.
    """
    return number ^ secret

def _prune(number: int) -> int:
    """Prunes a number by applying modulo operation.

    Args:
        number (int): The input number.

    Returns:
        int: The pruned number after applying modulo PRUNE_NUMBER.
    """
    return number % PRUNE_NUMBER

def _mix_and_prune(number: int, secret: int) -> int:
    """Applies mixing and pruning operations on a number.

    Args:
        number (int): The input number.
        secret (int): The secret number.

    Returns:
        int: The final result after mixing and pruning.
    """
    return _prune(_mix(number, secret))

@cache
def _next_secret_number(secret_number: int) -> int:
    """Computes the next secret number using a sequence of operations.

    Args:
        secret_number (int): The initial secret number.

    Returns:
        int: The transformed secret number.
    """
    for operation in OPERATIONS:
        secret_number = _mix_and_prune(
            number=operation(secret_number),
            secret=secret_number
        )

    return secret_number

def _best_banana_trade(dict_secret_numbers: dict) -> int:
    """Identifies the best banana trade by analyzing secret number sequences.

    Args:
        dict_secret_numbers (dict): A dictionary mapping buyer IDs to their
                                    sequence of secret numbers.

    Returns:
        int: The maximum banana trade value based on the computed differences.
    """
    dict_differences = defaultdict(int)

    for buyer_id, buyer_secret_numbers in dict_secret_numbers.items():
        visited_differences = set()
        for i in range(0, len(buyer_secret_numbers) - COMBINATIONS_LENGTH):
            subset_bananas = buyer_secret_numbers[i:i+COMBINATIONS_LENGTH+1]
            subset_bananas_difference = [
                banana % 10 - banana_previous % 10
                for banana_previous, banana in zip(
                    subset_bananas,
                    subset_bananas[1:]
                )
            ]

            differences_key = tuple(subset_bananas_difference)

            if differences_key in visited_differences:
                continue

            visited_differences.add(differences_key)

            dict_differences[differences_key] += (
                subset_bananas[-1] % 10
            )

    return max(dict_differences.values())

def first_exercise(filename: Path) -> int:
    initial_secret_numbers = _read_and_process_file(filename)

    secrets_sum = 0

    for secret_number in initial_secret_numbers:
        for _ in range(N_ROUNDS):
            secret_number = _next_secret_number(
                secret_number
            )

        secrets_sum += secret_number

    return secrets_sum

def second_exercise(filename: Path):
    initial_secret_numbers = _read_and_process_file(filename)

    dict_secret_numbers = {
        buyer_id: [initial_secret_number]
        for buyer_id, initial_secret_number in enumerate(initial_secret_numbers)
    }

    for buyer_id, secret_number in enumerate(initial_secret_numbers):
        for _ in range(N_ROUNDS):
            secret_number = _next_secret_number(
                secret_number
            )

            dict_secret_numbers[buyer_id].append(secret_number)

    return _best_banana_trade(dict_secret_numbers)
