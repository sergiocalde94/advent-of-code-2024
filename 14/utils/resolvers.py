import itertools as it
import re
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PATH_IMAGES = Path("images")


@dataclass
class Robot:
    """Represents a robot with a position and velocity.

    Attributes:
        position (tuple): The current (x, y) position of the robot.
        velocity (tuple): The current (x, y) velocity of the robot.
    """
    position: tuple
    velocity: tuple

    def teleport(self, max_x: int, max_y: int) -> None:
        """Moves the robot based on its velocity and wraps around if it goes
        outside the boundaries.

        Args:
            max_x (int): The maximum x-coordinate of the map.
            max_y (int): The maximum y-coordinate of the map.
        """
        def _teleport_axis(position, max_axis) -> int:
            if position < 0:
                while position < 0:
                    position = position + max_axis

                return position
            elif position >= max_axis:
                while position >= max_axis:
                    position = position - max_axis

                return position

            return position

        new_x = self.position[0] + self.velocity[0]
        new_y = self.position[1] + self.velocity[1]

        new_x = _teleport_axis(new_x, max_x)

        new_y = _teleport_axis(new_y, max_y)

        self.position = (new_x, new_y)


@dataclass
class RobotMap:
    """Represents the map containing robots and its boundaries.

    Attributes:
        robots (list): A list of Robot objects.
        max_x (int): The maximum x-coordinate of the map.
        max_y (int): The maximum y-coordinate of the map.
    """
    robots: list
    max_x: int
    max_y: int


REGEX_POSITION = re.compile(r"p=(-?\d+),(-?\d+)")
REGEX_VELOCITY = re.compile(r"v=(-?\d+),(-?\d+)")


def _read_and_process_file(filename: Path):
    """Reads a file and processes it into a RobotMap.

    The file contains robots, each defined by position and velocity.

    Args:
        filename (Path): Path to the file containing robot data.

    Returns:
        RobotMap: A RobotMap object containing robots and the map boundaries.
    """
    with open(filename) as f:
        robots_raw = f.read().split("\n")

    robots = [
        Robot(
            position=tuple(map(int, REGEX_POSITION.search(robot).groups())),
            velocity=tuple(map(int, REGEX_VELOCITY.search(robot).groups())),
        )
        for robot in robots_raw
    ]

    return RobotMap(
        robots=robots,
        max_x=max(robot.position[0] for robot in robots) + 1,
        max_y=max(robot.position[1] for robot in robots) + 1,
    )

def _print_map(robots_map: RobotMap, iteration: int) -> None:
    """Visualizes the robot positions on the map and saves the image.

    Args:
        robots_map (RobotMap): The map containing robots.
        iteration (int): The iteration number, used for naming the output file.
    """
    max_x, max_y = robots_map.max_x, robots_map.max_y

    map_ = np.full((max_x, max_y), 0)
    for robot in robots_map.robots:
        map_[robot.position] = 1

    fig, ax = plt.subplots()
    ax.matshow(map_)
    fig.savefig(PATH_IMAGES / f"christmas_tree_{iteration}.png")

def first_exercise(filename: Path):
    robots_map = _read_and_process_file(filename)

    max_x, max_y = robots_map.max_x, robots_map.max_y

    result_quadrant_1 = 0
    result_quadrant_2 = 0
    result_quadrant_3 = 0
    result_quadrant_4 = 0

    mid_x = max_x // 2
    mid_y = max_y // 2

    for robot in robots_map.robots:
        [robot.teleport(max_x, max_y) for _ in range(100)]
        if robot.position[0] < mid_x and robot.position[1] < mid_y:
            result_quadrant_1 += 1
        elif robot.position[0] > mid_x and robot.position[1] < mid_y:
            result_quadrant_2 += 1
        elif robot.position[0] < mid_x and robot.position[1] > mid_y:
            result_quadrant_3 += 1
        elif robot.position[0] > mid_x and robot.position[1] > mid_y:
            result_quadrant_4 += 1

    return (
        result_quadrant_1
        * result_quadrant_2
        * result_quadrant_3
        * result_quadrant_4
    )

def second_exercise(filename: Path):
    robots_map = _read_and_process_file(filename)

    max_x, max_y = robots_map.max_x, robots_map.max_y

    for i in it.count(start=1):
        for robot in robots_map.robots:
            robot.teleport(max_x, max_y)

        sorted_robots = sorted(robots_map.robots, key=lambda x: x.position)

        horizontal_stack = 1
        vertical_stack = 1

        for robot_left, robot_right in zip(sorted_robots, sorted_robots[1:]):
            if robot_left.position[0] == robot_right.position[0]:
                if robot_left.position[1] + 1 == robot_right.position[1]:
                    horizontal_stack += 1
                    if horizontal_stack == 8:
                        break
                else:
                    horizontal_stack = 1
            else:
                horizontal_stack = 1

            if robot_left.position[1] == robot_right.position[1]:
                if robot_left.position[0] + 1 == robot_right.position[0]:
                    vertical_stack += 1
                    if vertical_stack == 8:
                        break
                else:
                    vertical_stack = 1
            else:
                vertical_stack = 1

        if horizontal_stack == 8 or vertical_stack == 8:
            _print_map(robots_map, iteration=i)
            return i
