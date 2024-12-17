from pathlib import Path

from utils.resolvers import first_exercise, second_exercise

PATH_INPUTS = Path("inputs")

filename_example = PATH_INPUTS / "example.txt"
filename_exercise = PATH_INPUTS / "exercise.txt"

assert first_exercise(filename_example, number_of_blinks=1) == 3
assert first_exercise(filename_example, number_of_blinks=2) == 4
assert first_exercise(filename_example, number_of_blinks=3) == 5
assert first_exercise(filename_example, number_of_blinks=4) == 9
assert first_exercise(filename_example, number_of_blinks=5) == 13
assert first_exercise(filename_example, number_of_blinks=6) == 22

print("First exercise result:", first_exercise(filename_exercise))
print("Second exercise result:", second_exercise(filename_exercise))
