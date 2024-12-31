import itertools as it
from pathlib import Path

EMPTY = "."

def _read_and_process_file(filename: Path) -> list:
    """Reads and processes a file to generate a disk map as a flat list.

    The file is expected to contain a dense representation of a disk map.
    The function interprets alternating values in the file as:

    - Non-empty sections (mapped to unique IDs).
    - Empty sections (filled with the `EMPTY` constant).

    Args:
        filename (Path): Path to the input file containing the dense disk map.

    Returns:
        list: A flat list representing the disk map, where:
              - Non-empty sections are assigned unique IDs.
              - Empty sections are represented by the `EMPTY` constant.
    """
    with open(filename) as f:
        disk_map_dense = f.read()

    index_iterator = it.count()

    return list(
        it.chain.from_iterable([
            (
                [next(index_iterator)] * int(pos) if index % 2 == 0
                else [EMPTY] * int(pos)
            )
            for index, pos in enumerate(disk_map_dense)
        ])
    )

def _is_the_rest_empty(disk_map: str) -> bool:
    """Checks if the remaining portion of the disk map consists only
    of empty spaces.

    Args:
        disk_map (str): The disk map as a string, where empty spaces
            are represented by `EMPTY`.

    Returns:
        bool: True if the end of the disk map contains only empty spaces,
            False otherwise.
    """
    n_empties = disk_map.count(EMPTY)

    return disk_map[-n_empties:] == (["."] * n_empties)

def _fill_first_empty_with_last(disk_map: str) -> str:
    """Fills the first empty space in the disk map with the last
    non-empty value.

    The function swaps the last non-empty value in the disk map with
    the first empty space, maintaining the overall structure.

    Args:
        disk_map (str): The disk map as a string, where empty spaces
            are represented by `EMPTY`.

    Returns:
        str: The updated disk map after filling the first empty space.
    """
    first_empty_index = disk_map.index(EMPTY)
    last_empty_index = "".join(map(str, disk_map)).rindex(EMPTY)
    disk_map_length = len(disk_map[:last_empty_index])

    for i in range(disk_map_length - 1, -1, -1):
        current_position = disk_map[i]
        if current_position != EMPTY:
            disk_map[first_empty_index] = current_position
            disk_map[i] = EMPTY
            return disk_map

def _apply_checksum(disk_map: str) -> int:
    """Computes a checksum for the disk map.

    The checksum is calculated as the sum of `index * value` for all non-empty
    values in the disk map.

    Args:
        disk_map (str): The disk map as a string, where empty spaces are
            represented by `EMPTY`.

    Returns:
        int: The checksum value of the disk map.
    """
    return sum(
        index * int(value)
        for index, value in enumerate(disk_map)
        if value != EMPTY
    )

def first_exercise(filename: Path):
    disk_map = _read_and_process_file(filename) + [EMPTY]

    while not _is_the_rest_empty(disk_map):
        disk_map = _fill_first_empty_with_last(disk_map)

    return _apply_checksum(disk_map)

def second_exercise(filename: Path):
    disk_map = _read_and_process_file(filename)

    file_ids = sorted(
        set(filter(lambda x: x != EMPTY, disk_map)),
        reverse=True
    )

    for file_id in file_ids:
        index_start = disk_map.index(file_id)
        index_end = len(disk_map) - list(reversed(disk_map)).index(file_id)

        step = index_end - index_start

        for i in range(index_start):
            if disk_map[i:i + step] == [EMPTY] * step:
                disk_map[i:i + step] = [file_id] * step
                disk_map[index_start:index_end] = [EMPTY] * step
                break

    return _apply_checksum(disk_map)
