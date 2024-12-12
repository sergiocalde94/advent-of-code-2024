from pathlib import Path

from utils.resolvers import first_exercise, second_exercise

PATH_INPUTS = Path("inputs")

filename_example = PATH_INPUTS / "example.txt"
filename_exercise = PATH_INPUTS / "exercise.txt"

assert first_exercise(filename_example) == 3_749

print("First exercise result:", first_exercise(filename_exercise))

assert second_exercise(filename_example) == 11_387

print("Second exercise result:", second_exercise(filename_exercise))