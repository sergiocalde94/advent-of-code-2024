import copy
import itertools as it
import operator
import re
from dataclasses import dataclass
from pathlib import Path

REGEX_INITIAL_WIRE_VALUE = re.compile(r"(\w+): (\w+)")
REGEX_OPERATION = re.compile(r"(\w+) (AND|OR|XOR) (\w+) -> (\w+)")
REGEX_NUMERICAL = re.compile(r"(\d+)")


@dataclass
class Operation:
    """Represents a logical operation between two inputs producing a result on
    a wire.

    Attributes:
        left (str): The left input wire.
        right (str): The right input wire.
        logical_operator_str (str): The string representation of the logical
            operator (AND, OR, XOR).
        result_wire (str): The result wire where the output is stored.
    """
    left: bool
    right: bool
    logical_operator_str: str
    result_wire: str

    def __post_init__(self):
        self.logical_operator = (
            operator.and_
            if self.logical_operator_str == "AND"
            else operator.or_
            if self.logical_operator_str == "OR"
            else operator.xor
            if self.logical_operator_str == "XOR"
            else None
        )

def _read_and_process_file(filename: Path) -> tuple:
    """Reads and processes the input file containing initial wire values and
    operations.

    Args:
        filename (Path): Path to the input file.

    Returns:
        tuple: A tuple containing:
            - wire_values (dict): A dictionary of initial wire values.
            - operations (list[Operation]): A list of logical operations.
    """
    with open(filename) as f:
        initial_wire_values_raw, operations_raw = f.read().split("\n\n")

    initial_wire_values = {
        REGEX_INITIAL_WIRE_VALUE.search(initial_wire_value).group(1): int(
            REGEX_INITIAL_WIRE_VALUE.search(initial_wire_value).group(2)
        )
        for initial_wire_value in initial_wire_values_raw.split("\n")
    }

    operations = [
        Operation(
            left=REGEX_OPERATION.search(operation).group(1),
            right=REGEX_OPERATION.search(operation).group(3),
            logical_operator_str=REGEX_OPERATION.search(operation).group(2),
            result_wire=REGEX_OPERATION.search(operation).group(4),
        )
        for operation in operations_raw.split("\n")
    ]

    return initial_wire_values, operations

def _solve_equations(wire_values: dict, operations: list[Operation]) -> None:
    """Solves all logical operations and updates the wire values.

    Args:
        wire_values (dict): A dictionary of initial wire values.
        operations (list[Operation]): A list of logical operations to compute.

    Returns:
        None
    """
    all_wires = set(
        [operation.left for operation in operations]
        + [operation.right for operation in operations]
        + [operation.result_wire for operation in operations]
    )

    solved_equations = set()

    while len(all_wires) > len(wire_values):
        for operation in operations:
            operation_key = (
                operation.left,
                operation.right,
                operation.result_wire,
            )

            if operation_key in solved_equations:
                continue

            is_operation_valid = (
                operation.left in wire_values
                and operation.right in wire_values
            )

            if is_operation_valid:
                wire_values[operation.result_wire] = (
                    operation
                    .logical_operator(
                        wire_values[operation.left],
                        wire_values[operation.right],
                    )
                )

                solved_equations.add(operation_key)

def _filter_wires(wire_values: dict, starts_with: str) -> dict:
    """Filters the wire values based on a prefix.

    Args:
        wire_values (dict): A dictionary of wire values.
        starts_with (str): The prefix to filter the wires.

    Returns:
        dict: A dictionary of filtered wire values.
    """
    return {
        int(REGEX_NUMERICAL.search(wire).group(0)): value
        for wire, value in wire_values.items()
        if wire.startswith(starts_with)
    }

def _find_operation(operations: list[Operation],
                    gate_left: str = None,
                    gate_right: str = None,
                    logical_operator_str: str = None,
                    result_wire: str = None) -> Operation:
    """Finds a specific logical operation based on provided criteria.

    Args:
        operations (list[Operation]): A list of operations to search through.
        gate_left (str, optional): The left input gate for the operation.
            Defaults to None.
        gate_right (str, optional): The right input gate for the operation.
            Defaults to None.
        logical_operator_str (str, optional): The logical operator
            (e.g., XOR, AND, OR). Defaults to None.
        result_wire (str, optional): The result wire for the operation.
            Defaults to None.

    Returns:
        Operation: The matching operation, or None if no match is found.
    """
    return next(
        (
            operation
            for operation in operations
            if (
                (
                    (
                        operation.left == gate_left
                        and operation.right == gate_right
                    )
                    or (
                        operation.left == gate_right
                        and operation.right == gate_left
                    )
                    or (
                        operation.left == gate_left
                        or operation.right == gate_left
                        or operation.left == gate_right
                        or operation.right == gate_right
                    )
                )
                and (operation.logical_operator_str == logical_operator_str)
            )
            or (operation.result_wire == result_wire)
        ),
        None,
    )

def _ripple_carry_adder_correct(wire_values: dict,
                                operations: list[Operation],
                                bit_position: int,
                                carry_in: str) -> tuple:
    """Computes the ripple carry adder for a single bit position.

    Args:
        wire_values (dict): A dictionary mapping wire names to their values.
        operations (list[Operation]): A list of logical operations.
        bit_position (int): The bit position being processed.
        carry_in (str): The carry-in value for the current bit position.

    Returns:
        tuple: A tuple containing:
            - current_bit_sum (int): The sum of the current bit position.
            - carry_out (int): The carry-out value for the current bit position.
    """
    current_bit_sum = (
        wire_values[f"x{bit_position:02d}"]
        ^ wire_values[f"y{bit_position:02d}"]
    ) ^ carry_in

    carry_out = (
        wire_values[f"x{bit_position:02d}"]
        & wire_values[f"y{bit_position:02d}"]
    ) | (
        (
            wire_values[f"x{bit_position:02d}"]
            ^ wire_values[f"y{bit_position:02d}"]
        )
        & carry_in
    )

    return current_bit_sum, carry_out

def _apply_operation(operation: Operation, wire_values: dict) -> int:
    """Applies a logical operation using the provided wire values.

    Args:
        operation (Operation): The logical operation to apply.
        wire_values (dict): A dictionary mapping wire names to their values.

    Returns:
        int: The result of the logical operation.
    """
    return operation.logical_operator(
        wire_values[operation.left], wire_values[operation.right]
    )

def _swap_and_operate(operations: list[Operation],
                      wire_values: dict,
                      wires: dict,
                      carry_gate_in: str,
                      bit_position: int,
                      current_bit_sum: int,
                      carry_gate_out: int) -> list[Operation]:
    """Finds the optimal swap to validate and update logical operations.

    Args:
        operations (list[Operation]): A list of logical operations.
        wire_values (dict): A dictionary mapping wire names to their values.
        wires (dict): A dictionary mapping operation keys to result wires.
        carry_gate_in (str): The carry-in gate name.
        bit_position (int): The bit position being processed.
        current_bit_sum (int): The current sum at the bit position.
        carry_gate_out (int): The expected carry-out value.

    Returns:
        list[Operation]: The updated list of operations with adjusted wiring.
    """
    dict_current_operations = {}

    for operation_key, result_wire in wires.items():
        dict_current_operations[operation_key] = _find_operation(
            operations, result_wire=result_wire
        )

    no_swap = [("No swap", "is needed :)")]
    swap_candidates = list(it.combinations(wires.items(), r=2))

    for operation_results in no_swap + swap_candidates:
        swap_left, swap_right = operation_results

        x_xor_y_key = next(
            key
            for key in dict_current_operations.keys()
            if "_XOR_" in key and "x" in key
        )

        x_xor_y_result = (
            swap_right[1]
            if ("XOR" in swap_left[0] and "x" in swap_left[0])
            else swap_left[1]
            if ("XOR" in swap_right[0] and "x" in swap_right[0])
            else dict_current_operations[x_xor_y_key].result_wire
        )

        x_and_y_key = next(
            key
            for key in dict_current_operations.keys()
            if "_AND_" in key and "x" in key
        )

        x_and_y_result = (
            swap_right[1]
            if ("AND" in swap_left[0] and "x" in swap_left[0])
            else swap_left[1]
            if ("AND" in swap_right[0] and "x" in swap_right[0])
            else dict_current_operations[x_and_y_key].result_wire
        )

        x_xor_y_xor_carry_key = next(
            key
            for key in dict_current_operations.keys()
            if "_XOR_" in key and "x" not in key
        )

        x_xor_y_xor_carry_result = (
            swap_right[1]
            if ("XOR" in swap_left[0] and "x" not in swap_left[0])
            else swap_left[1]
            if ("XOR" in swap_right[0] and "x" not in swap_right[0])
            else dict_current_operations[x_xor_y_xor_carry_key].result_wire
        )

        x_xor_y_and_carry_key = next(
            key
            for key in dict_current_operations.keys()
            if "_AND_" in key and "x" not in key
        )

        x_xor_y_and_carry_result = (
            swap_right[1]
            if ("AND" in swap_left[0] and "x" not in swap_left[0])
            else swap_left[1]
            if ("AND" in swap_right[0] and "x" not in swap_right[0])
            else dict_current_operations[x_xor_y_and_carry_key].result_wire
        )

        x_xor_y_and_carry_or_x_and_y_key = next(
            key
            for key in dict_current_operations.keys()
            if "_OR_" in key
        )

        x_xor_y_and_carry_or_x_and_y_result = (
            swap_right[1]
            if ("_OR_" in swap_left[0])
            else swap_left[1]
            if ("_OR_" in swap_right[0])
            else dict_current_operations[
                x_xor_y_and_carry_or_x_and_y_key
            ].result_wire
        )

        if not x_xor_y_xor_carry_result.startswith("z"):
            continue

        is_and_correct_first = (
            x_xor_y_result in x_xor_y_xor_carry_key
            and carry_gate_in in x_xor_y_xor_carry_key
        )

        is_and_correct_second = (
            x_xor_y_result in x_xor_y_and_carry_key
            and carry_gate_in in x_xor_y_and_carry_key
        )

        is_or_correct = (
            x_xor_y_and_carry_result in x_xor_y_and_carry_or_x_and_y_key
            and x_and_y_result in x_xor_y_and_carry_or_x_and_y_key
        )

        if (not is_and_correct_first
            or not is_and_correct_second
            or not is_or_correct):
            continue

        wire_values[x_xor_y_result] = _apply_operation(
            Operation(
                left=f"x{bit_position:02d}",
                right=f"y{bit_position:02d}",
                logical_operator_str="XOR",
                result_wire=x_xor_y_result,
            ),
            wire_values,
        )

        wire_values[x_and_y_result] = _apply_operation(
            Operation(
                left=f"x{bit_position:02d}",
                right=f"y{bit_position:02d}",
                logical_operator_str="AND",
                result_wire=x_and_y_result,
            ),
            wire_values,
        )

        wire_values[x_xor_y_xor_carry_result] = _apply_operation(
            Operation(
                left=x_xor_y_result,
                right=carry_gate_in,
                logical_operator_str="XOR",
                result_wire=x_xor_y_xor_carry_result,
            ),
            wire_values,
        )

        wire_values[x_xor_y_and_carry_result] = _apply_operation(
            Operation(
                left=x_xor_y_result,
                right=carry_gate_in,
                logical_operator_str="AND",
                result_wire=x_xor_y_and_carry_result,
            ),
            wire_values,
        )

        wire_values[x_xor_y_and_carry_or_x_and_y_result] = _apply_operation(
            Operation(
                left=x_xor_y_and_carry_result,
                right=x_and_y_result,
                logical_operator_str="OR",
                result_wire=x_xor_y_and_carry_or_x_and_y_result,
            ),
            wire_values,
        )

        current_bit_sum_is_valid = (
            current_bit_sum == wire_values[x_xor_y_xor_carry_result]
        )

        carry_gate_out_is_valid = (
            carry_gate_out
            == wire_values[x_xor_y_and_carry_or_x_and_y_result]
        )

        if current_bit_sum_is_valid and carry_gate_out_is_valid:
            index_operation_x_xor_y = operations.index(
                _find_operation(
                    operations,
                    gate_left=f"x{bit_position:02d}",
                    gate_right=f"y{bit_position:02d}",
                    logical_operator_str="XOR",
                )
            )

            operations[index_operation_x_xor_y].result_wire = x_xor_y_result

            index_operation_x_and_y = operations.index(
                _find_operation(
                    operations,
                    gate_left=f"x{bit_position:02d}",
                    gate_right=f"y{bit_position:02d}",
                    logical_operator_str="AND",
                )
            )

            operations[index_operation_x_and_y].result_wire = x_and_y_result

            index_operation_x_xor_y_xor_carry = operations.index(
                _find_operation(
                    operations,
                    gate_left=x_xor_y_result,
                    gate_right=carry_gate_in,
                    logical_operator_str="XOR",
                )
            )

            operations[
                index_operation_x_xor_y_xor_carry
            ].result_wire = x_xor_y_xor_carry_result

            index_operation_x_xor_y_and_carry = operations.index(
                _find_operation(
                    operations,
                    gate_left=x_xor_y_result,
                    gate_right=carry_gate_in,
                    logical_operator_str="AND",
                )
            )

            operations[
                index_operation_x_xor_y_and_carry
            ].result_wire = x_xor_y_and_carry_result

            index_operation_x_xor_y_and_carry_or_x_and_y = operations.index(
                _find_operation(
                    operations,
                    gate_left=x_xor_y_and_carry_result,
                    gate_right=x_and_y_result,
                    logical_operator_str="OR",
                )
            )

            operations[
                index_operation_x_xor_y_and_carry_or_x_and_y
            ].result_wire = x_xor_y_and_carry_or_x_and_y_result

            break

    return (
        wire_values[x_xor_y_xor_carry_result],
        x_xor_y_and_carry_or_x_and_y_result,
    )

def _ripple_carry_adder(wire_values: dict,
                        operations: list[Operation],
                        bit_position: int,
                        carry_gate_in: str) -> tuple:
    """Executes a ripple-carry adder for multiple bit positions.

    Args:
        wire_values (dict): A dictionary mapping wire names to their values.
        operations (list[Operation]): A list of logical operations.
        bit_position (int): The bit position being processed.
        carry_gate_in (str): The carry-in gate name.

    Returns:
        tuple: The result of the bit addition and the carry-out gate.
    """
    current_bit_sum, carry_gate_out = _ripple_carry_adder_correct(
        wire_values, operations, bit_position, wire_values.get(carry_gate_in, 0)
    )

    x_xor_y = _find_operation(
        operations, f"x{bit_position:02d}", f"y{bit_position:02d}", "XOR"
    )

    x_and_y = _find_operation(
        operations, f"x{bit_position:02d}", f"y{bit_position:02d}", "AND"
    )

    if bit_position == 0:
        wire_values[x_xor_y.result_wire] = x_xor_y.logical_operator(
            wire_values[x_xor_y.left], wire_values[x_xor_y.right]
        )

        wire_values[x_and_y.result_wire] = x_and_y.logical_operator(
            wire_values[x_and_y.left], wire_values[x_and_y.right]
        )

        _is_current_operation_valid = (
            current_bit_sum == wire_values[f"z{bit_position:02d}"]
            and carry_gate_out == wire_values[x_and_y.result_wire]
        )

        if _is_current_operation_valid:
            return current_bit_sum, x_and_y.result_wire
        else:
            raise ValueError("No valid input, first operation is not valid")

    z_operation = _find_operation(
        operations, result_wire=f"z{bit_position:02d}"
    )

    z_operation_key = (
        (
            f"{z_operation.left}_"
            f"{z_operation.logical_operator_str}_"
            f"{z_operation.right}"
        )
        if z_operation.left < z_operation.right
        else (
            f"{z_operation.right}_"
            f"{z_operation.logical_operator_str}_"
            f"{z_operation.left}"
        )
    )

    possible_results = {
        f"x{bit_position:02d}_XOR_y{bit_position:02d}": x_xor_y.result_wire,
        f"x{bit_position:02d}_AND_y{bit_position:02d}": x_and_y.result_wire,
    }

    if z_operation_key not in possible_results:
        possible_results[z_operation_key] = z_operation.result_wire

    possible_carry_gates = ["XOR", "AND"]

    for carry_gate in possible_carry_gates:
        operation = _find_operation(
            operations, gate_left=carry_gate_in, logical_operator_str=carry_gate
        )

        if operation:
            operation_key = (
                (
                    f"{operation.left}_{operation.logical_operator_str}_{operation.right}"
                )
                if operation.left < operation.right
                else (
                    f"{operation.right}_{operation.logical_operator_str}_{operation.left}"
                )
            )

            if operation_key not in possible_results:
                possible_results[operation_key] = operation.result_wire

    for wire_output in possible_results.values():
        operation = _find_operation(
            operations, gate_left=wire_output, logical_operator_str="OR"
        )

        if operation:
            operation_key = (
                (f"{operation.left}_OR_{operation.right}")
                if operation.left < operation.right
                else (f"{operation.right}_OR_{operation.left}")
            )

            if operation_key not in possible_results:
                possible_results[operation_key] = operation.result_wire
                break

    return _swap_and_operate(
        operations=operations,
        wire_values=wire_values,
        wires=possible_results,
        carry_gate_in=carry_gate_in,
        bit_position=bit_position,
        current_bit_sum=current_bit_sum,
        carry_gate_out=carry_gate_out,
    )

def first_exercise(filename: Path) -> int:
    wire_values, operations = _read_and_process_file(filename)

    _solve_equations(wire_values, operations)

    z_wires = _filter_wires(wire_values, starts_with="z")

    return sum(2**power for power, flag in z_wires.items() if flag == 1)

def second_exercise(filename: Path):
    wire_values, operations = _read_and_process_file(filename)

    operations_clean = copy.deepcopy(operations)

    n_bits = sum(
        1 for operation in operations if operation.result_wire.startswith("z")
    )

    carry = None
    for i in range(n_bits - 1):
        pos, carry = _ripple_carry_adder(wire_values, operations, i, carry)

    return ",".join(
        sorted([
            operation.result_wire
            for operation in operations
            if operation not in operations_clean
        ])
    )
