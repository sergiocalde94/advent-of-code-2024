from pathlib import Path

from utils.resolvers import first_exercise, second_exercise

PATH_INPUTS = Path("inputs")

filename_example = PATH_INPUTS / "example.txt"
filename_example_2 = PATH_INPUTS / "example_2.txt"
filename_example_3 = PATH_INPUTS / "example_3.txt"
filename_example_4 = PATH_INPUTS / "example_4.txt"
filename_example_5 = PATH_INPUTS / "example_5.txt"
filename_exercise = PATH_INPUTS / "exercise.txt"

assert first_exercise(filename_example) == 140
assert first_exercise(filename_example_2) == 772
assert first_exercise(filename_example_3) == 1_930

print("First exercise result:", first_exercise(filename_exercise))

assert second_exercise(filename_example) == 80
assert second_exercise(filename_example_2) == 436
assert second_exercise(filename_example_3) == 1_206
assert second_exercise(filename_example_4) == 236
assert second_exercise(filename_example_5) == 368

print("Second exercise result:", second_exercise(filename_exercise))
