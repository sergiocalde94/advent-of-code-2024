from pathlib import Path

from utils.resolvers import first_exercise, second_exercise

PATH_INPUTS = Path("inputs")

filename_example = PATH_INPUTS / "example.txt"
filename_example_2 = PATH_INPUTS / "example_2.txt"
filename_exercise = PATH_INPUTS / "exercise.txt"

assert first_exercise(filename_example) == 37_327_623

print("First exercise result:", first_exercise(filename_exercise))

assert second_exercise(filename_example_2) == 23

print("Second exercise result:", second_exercise(filename_exercise))
