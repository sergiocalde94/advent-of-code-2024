import re
from pathlib import Path

REGEX_REGISTER = re.compile(r"Register (\w*): (\d+)")
REGEX_PROGRAM = re.compile(r"Program: (.*)")


def _adv(registers, operand):
    """Divides register A by 2^operand and stores the result in register A.

    Args:
        registers (dict): A dictionary of register values.
        operand (int): The division operand.
    """
    registers["A"] //= 2**operand


def _bxl(registers, operand):
    """Performs an XOR operation on register B with the operand.

    Args:
        registers (dict): A dictionary of register values.
        operand (int): The value to XOR with.
    """
    registers["B"] ^= operand


def _bst(registers, operand):
    """Sets register B to the modulus of the operand with 8.

    Args:
        registers (dict): A dictionary of register values.
        operand (int): The value to modulus with.
    """
    registers["B"] = operand % 8


def _jnz(registers, operand):
    """Returns the operand as the new instruction pointer if register A is non-zero.

    Args:
        registers (dict): A dictionary of register values.
        operand (int): The new instruction pointer.

    Returns:
        int | None: The new instruction pointer or None.
    """
    if registers["A"] != 0:
        return operand


def _bxc(registers, operand):
    """Performs an XOR operation on register B with the value of register C.

    Args:
        registers (dict): A dictionary of register values.
        operand (int): Unused operand.
    """
    registers["B"] ^= registers["C"]


def _out(registers, operand):
    """Outputs the operand modulus 8.

    Args:
        registers (dict): A dictionary of register values.
        operand (int): The value to modulus with.

    Returns:
        int: The result of the operand modulus 8.
    """
    return operand % 8


def _bdv(registers, operand):
    """Divides register A by 2^operand and stores the result in register B.

    Args:
        registers (dict): A dictionary of register values.
        operand (int): The division operand.
    """
    registers["B"] = registers["A"] // 2**operand


def _cdv(registers, operand):
    """Divides register A by 2^operand and stores the result in register C.

    Args:
        registers (dict): A dictionary of register values.
        operand (int): The division operand.
    """
    registers["C"] = registers["A"] // 2**operand


OPCODES = {
    0: _adv,
    1: _bxl,
    2: _bst,
    3: _jnz,
    4: _bxc,
    5: _out,
    6: _bdv,
    7: _cdv,
}

COMBO_OPCODES = {0, 2, 5, 6, 7}


def _read_and_process_file(filename: Path) -> tuple:
    """Reads and processes the input file into registers and program
    instructions.

    Args:
        filename (Path): Path to the input file.

    Returns:
        tuple: A tuple containing:
            - registers (dict): A dictionary of registers and their
                initial values.
            - program (list): A list of program instructions as
                (opcode, operand) tuples.
    """
    with open(filename) as f:
        registers_raw, program_raw = f.read().split("\n\n")

    registers = {
        REGEX_REGISTER.search(program).group(1): int(
            REGEX_REGISTER.search(program).group(2)
        )
        for program in registers_raw.split("\n")
    }

    program_raw_list = REGEX_PROGRAM.search(program_raw).group(1).split(",")

    program = list(
        zip(map(int, program_raw_list[::2]), map(int, program_raw_list[1::2]))
    )

    return registers, program


def _translate_operand(registers: dict, operand: int) -> int:
    """Translates operands for the combos.

    Args:
        registers (dict): A dictionary of register values.
        operand (int): The operand to translate.

    Returns:
        int: The translated operand.
    """
    operand_translated = operand
    if operand == 4:
        operand_translated = registers["A"]
    elif operand == 5:
        operand_translated = registers["B"]
    elif operand == 6:
        operand_translated = registers["C"]
    elif operand == 7:
        operand_translated = None

    return operand_translated


def _apply_program(registers: dict, program: list) -> dict:
    """Executes the program instructions on the registers.

    Args:
        registers (dict): A dictionary of register values.
        program (list): A list of program instructions as (opcode, operand)
            tuples.

    Returns:
        str: The output of the program as a comma-separated string.
    """
    outputs = []
    instruction_pointer = 0
    while True:
        opcode, operand = program[instruction_pointer]

        opcode_func = OPCODES[opcode]

        if opcode in COMBO_OPCODES:
            operand_translated = _translate_operand(registers, operand)
        else:
            operand_translated = operand

        output = opcode_func(registers, operand_translated)

        if opcode == 3:
            if output is not None:
                instruction_pointer = output
                continue
        elif opcode == 5:
            outputs.append(output)

        instruction_pointer += 1

        if instruction_pointer == len(program):
            break

    return ",".join(map(str, outputs))


def first_exercise(filename: Path):
    registers, program = _read_and_process_file(filename)

    return _apply_program(registers, program)


def second_exercise(filename: Path):
    registers, program = _read_and_process_file(filename)

    program_str = ",".join(map(str, [num for pair in program for num in pair]))

    output = _apply_program(registers.copy(), program)

    registers["A"] = 0
    program_len = len(program_str.split(","))
    for i in reversed(range(program_len)):
        registers["A"] <<= 3
        output = _apply_program(registers.copy(), program)
        while output != ",".join(program_str.split(",")[i:]):
            registers["A"] += 1
            output = _apply_program(registers.copy(), program)

    return registers["A"]
