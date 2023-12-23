"""Day N."""

from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day18')


def part1(data: str) -> int:
    digger = Digger()
    for step in data.splitlines():
        direction_s, number_s, color_s = step.split()
        n = int(number_s)
        color = int(color_s.strip("#()"), base=16)
        digger.move(direction_s, n, color)

    return digger.hole_volume


def part2(data: str) -> int:
    digger = Digger()
    directions = ['r', 'd', 'l', 'u']
    for step in data.splitlines():
        _, _, color_s = step.split()
        color_s = color_s.strip("#()")
        digger.move(directions[int(color_s[-1])], int(color_s[:-1], base=16), "")

    return digger.hole_volume



class Digger:
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.visited_pos = [self.position]
        self.perimeter = 0

    @property
    def position(self) -> tuple[int]:
        return self.x, self.y

    @property
    def hole_volume(self) -> int:
        area = 0
        vertices = self.visited_pos
        n_vertices = len(vertices) - 1
        for i in range(n_vertices):
            p_i = vertices[i]
            p_i_p1 = vertices[i+1]
            # Trapezoid formula/Shoelace formula. Compute trapezoidal areas to
            # the bounding box with a sign depending on the direction of the
            # segment on the polygon being measured. Alternating signs cancels
            # out any external area. Math!
            area += (p_i[1] + p_i_p1[1]) * (p_i[0] - p_i_p1[0])
        area /= 2
        # Assert counterclockwiseness.
        area = abs(area)

        # Pick's theorem
        n_internal_points = area - self.perimeter/2 + 1
        print(n_vertices, area, n_internal_points)
        return n_internal_points + self.perimeter

    def move(self, dir: str, n: int, color: int) -> None:
        # Mark the current position as two-directional.
        self._move_dir(dir, n)
        self.visited_pos.append(self.position)
        self.perimeter += n
        print(self.position, dir, color)

    def _move_dir(self, dir: str, n_steps: int) -> None:
        dir = dir.casefold()
        if dir == "r":
            self.x += n_steps
            # return Direction.RIGHT
        elif dir == "d":
            self.y -= n_steps
            # return Direction.DOWN
        elif dir == "l":
            self.x -= n_steps
            # return Direction.LEFT
        elif dir == "u":
            self.y += n_steps
            # return Direction.UP
        else:
            raise ValueError(f"Invalid direction {dir}")


if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
