import itertools as it
from pathlib import Path

import polars as pl

EMPTY = "."
FILLED = "#"


def _read_and_process_file(filename: Path) -> tuple:
    with open(filename) as f:
        locks_and_keys_raw = f.read().split("\n\n")

    map_items = {
        EMPTY: 0,
        FILLED: 1
    }

    locks = [
        pl.DataFrame(lock).transpose().select(pl.all().replace_strict(map_items))
        for lock in [
            list(map(list, lock_or_key.split("\n")))
            for lock_or_key in locks_and_keys_raw
            if lock_or_key.startswith(FILLED)
        ]
    ]

    keys = [
        pl.DataFrame(key).transpose().select(pl.all().replace_strict(map_items))
        for key in [
            list(map(list, lock_or_key.split("\n")))
            for lock_or_key in locks_and_keys_raw
            if lock_or_key.startswith(EMPTY)
        ]
    ]

    return locks, keys

def first_exercise(filename: Path) -> int:
    locks, keys = _read_and_process_file(filename)

    result = 0
    for lock, key in it.product(locks, keys):
        is_key_for_this_lock = (
            (lock + key)
            .select(pl.all().le(1).all())
            .min_horizontal()
            .first()
        )

        if is_key_for_this_lock:
            result += 1

    return result
