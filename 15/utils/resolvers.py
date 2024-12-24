from pathlib import Path

import numpy as np

ROBOT = "@"
WALL = "#"
BOX = "O"
BOX_WIDER_LEFT = "["
BOX_WIDER_RIGHT = "]"
EMPTY = "."

DICT_MOVEMENTS = {
    "<": np.array([0, -1]),
    ">": np.array([0, 1]),
    "^": np.array([-1, 0]),
    "v": np.array([1, 0]),
}

GPS_ROW = 100
GPS_COLUMN = 1


def _read_and_process_file(filename: Path) -> tuple:
    """Reads and processes the input file into a warehouse map and a
    sequence of movements.

    The file contains a 2D map of the warehouse and a sequence of movements.

    Args:
        filename (Path): Path to the input file.

    Returns:
        tuple: A tuple containing:
            - warehouse (np.array): A 2D numpy array representing
                the warehouse.
            - movements (str): A string of movement directions.
    """
    with open(filename) as f:
        warehouse_raw, movements_raw = f.read().split("\n\n")

    warehouse = np.array([list(line) for line in warehouse_raw.split("\n")])
    movements = movements_raw.replace("\n", "")

    return warehouse, movements

def _sum_gps_coordinates(warehouse: np.array) -> int:
    """Calculates the GPS coordinates sum of all boxes in the warehouse.

    The GPS sum is calculated using the formula:
    `(row_index * GPS_ROW) + (column_index * GPS_COLUMN)` for each box.

    Args:
        warehouse (np.array): A 2D numpy array representing the warehouse.

    Returns:
        int: The sum of GPS coordinates for all boxes.
    """
    result = 0
    mask_boxes = (warehouse == BOX) | (warehouse == BOX_WIDER_LEFT)

    for row, column in np.argwhere(mask_boxes):
        result += (row * GPS_ROW) + (column * GPS_COLUMN)

    return result

def _widen_map(warehouse: np.array) -> np.array:
    """Expands the warehouse map horizontally to handle wide boxes.

    Args:
        warehouse (np.array): A 2D numpy array representing the warehouse.

    Returns:
        np.array: A horizontally expanded warehouse map.
    """
    n_rows, n_columns = warehouse.shape
    bigger_warehouse = np.empty((n_rows, n_columns * 2), dtype=object)

    map_old_and_new = list(
        zip(
            range(n_columns),
            zip(range(0, n_columns * 2, 2), range(1, n_columns * 2, 2)),
        )
    )

    for row in range(n_rows):
        for column, new_columns in map_old_and_new:
            if warehouse[row, column] == WALL:
                bigger_warehouse[row, new_columns] = WALL
            elif warehouse[row, column] == BOX:
                bigger_warehouse[row, new_columns] = [
                    BOX_WIDER_LEFT,
                    BOX_WIDER_RIGHT,
                ]

            elif warehouse[row, column] == EMPTY:
                bigger_warehouse[row, new_columns] = EMPTY
            elif warehouse[row, column] == ROBOT:
                bigger_warehouse[row, new_columns] = [ROBOT, EMPTY]

    return bigger_warehouse

def _apply_movements(warehouse: np.array, movements: str, debug=False) -> int:
    """Simulates the movements of the robot in the warehouse and calculates
    the GPS sum.

    Handles pushing boxes and wide boxes according to the movement directions.

    Args:
        warehouse (np.array): A 2D numpy array representing the warehouse.
        movements (str): A string of movement directions.
        debug (bool, optional): If True, enables debug mode. Defaults to False.

    Returns:
        int: The GPS sum of all boxes after applying the movements.
    """
    for movement in movements:
        robot_position = np.argwhere(warehouse == ROBOT)[0]
        next_position = robot_position + DICT_MOVEMENTS[movement]

        if warehouse[*next_position] == EMPTY:
            warehouse[*robot_position] = EMPTY
            warehouse[*next_position] = ROBOT

        elif warehouse[*next_position] == BOX:
            box_next_position = next_position + DICT_MOVEMENTS[movement]
            boxes_to_move = [box_next_position]

            while warehouse[*box_next_position] == BOX:
                box_next_position = box_next_position + DICT_MOVEMENTS[movement]
                boxes_to_move.append(box_next_position)

            if warehouse[*box_next_position] == EMPTY:
                warehouse[*robot_position] = EMPTY
                warehouse[*next_position] = ROBOT
                for box in boxes_to_move:
                    warehouse[*box] = BOX

        elif warehouse[*next_position] in (BOX_WIDER_LEFT, BOX_WIDER_RIGHT):
            if movement in ("<", ">"):
                box_next_position = next_position
                boxes_to_move = [
                    (box_next_position, warehouse[*box_next_position])
                ]

                while warehouse[*box_next_position] in (
                    BOX_WIDER_LEFT,
                    BOX_WIDER_RIGHT,
                ):
                    box_next_position = (
                        box_next_position + DICT_MOVEMENTS[movement]
                    )

                    if warehouse[*box_next_position] in (
                        BOX_WIDER_LEFT,
                        BOX_WIDER_RIGHT,
                    ):
                        boxes_to_move.append(
                            (box_next_position, warehouse[*box_next_position])
                        )

                next_is_empty = warehouse[*box_next_position] == EMPTY
            else:
                box_next_positions = [next_position]
                boxes_to_move = []

                while any(
                    warehouse[*next_cell] in (BOX_WIDER_LEFT, BOX_WIDER_RIGHT)
                    for next_cell in box_next_positions
                ):
                    box_next_positions_copy = box_next_positions.copy()
                    box_next_positions = []

                    for box_next_position in box_next_positions_copy:
                        if warehouse[*box_next_position] == BOX_WIDER_LEFT:
                            box_next_position_other_side = (
                                box_next_position + DICT_MOVEMENTS[">"]
                            )

                        elif warehouse[*box_next_position] == BOX_WIDER_RIGHT:
                            box_next_position_other_side = (
                                box_next_position + DICT_MOVEMENTS["<"]
                            )

                        else:
                            continue

                        box_next_positions.append(
                            box_next_position
                            + DICT_MOVEMENTS[movement]
                        )

                        box_next_positions.append(
                            box_next_position_other_side
                            + DICT_MOVEMENTS[movement]
                        )

                        boxes_to_move.append(
                            (
                                box_next_position,
                                warehouse[*box_next_position]
                            )
                        )

                        boxes_to_move.append(
                            (
                                box_next_position_other_side,
                                warehouse[*box_next_position_other_side],
                            )
                        )

                    next_is_wall = any(
                        warehouse[*box_next_position] == WALL
                        for box_next_position in box_next_positions
                    )

                    if next_is_wall:
                        break

                next_is_empty = all(
                    warehouse[*box_next_position] == EMPTY
                    for box_next_position in box_next_positions
                )

            if next_is_empty:
                warehouse[*robot_position] = EMPTY
                warehouse[*next_position] = ROBOT
                for box in boxes_to_move:
                    box_position, box_value = box

                    if warehouse[*box_position] != ROBOT:
                        warehouse[*box_position] = EMPTY

                for box in boxes_to_move:
                    box_position, box_value = box

                    box_position = box_position + DICT_MOVEMENTS[movement]
                    warehouse[*box_position] = box_value

    return _sum_gps_coordinates(warehouse)

def first_exercise(filename: Path):
    warehouse, movements = _read_and_process_file(filename)

    return _apply_movements(
        warehouse=warehouse,
        movements=movements)

def second_exercise(filename: Path):
    warehouse, movements = _read_and_process_file(filename)

    return _apply_movements(
        warehouse=_widen_map(warehouse),
        movements=movements
    )
