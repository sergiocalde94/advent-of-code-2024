from pathlib import Path

from utils.resolvers import first_exercise, second_exercise

PATH_INPUTS = Path("inputs")

filename_example = PATH_INPUTS / "example.txt"
filename_example_2 = PATH_INPUTS / "example_2.txt"
filename_exercise = PATH_INPUTS / "exercise.txt"

assert first_exercise(filename_example) == 7_036
assert first_exercise(filename_example_2) == 11_048

print("First exercise result:", first_exercise(filename_exercise))

assert second_exercise(filename_example) == 45
assert second_exercise(filename_example_2) == 64

print("Second exercise result:", second_exercise(filename_exercise))
