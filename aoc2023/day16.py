"""Day N."""

from enum import IntEnum
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day16')


class Direction(IntEnum):
    # Ordered clockwise
    LEFT = 0
    UP = 1
    RIGHT = 2
    DOWN = 3


def part1(data: str) -> int:
    wall_width = data.find('\n')
    wall_height = data.count('\n')
    Beam.wall_width = wall_width
    Beam.wall_height = wall_height

    for y, row in enumerate(reversed(data.splitlines())):
        for x, char in enumerate(row):
            if char == ".":
                continue
            # print(f"{char} at {x}, {y}")
            Beam.actors[(x, y)] = char

    beams = set()
    beams.add(Beam(-1, wall_height - 1, Direction.RIGHT))

    for i in range(10000):
        # print(beams)
        new_beams = set()
        dead_beams = set()
        for beam in beams:
            # beam.print_me()
            is_on_wall = beam.step()
            if not is_on_wall:
                # print("off the wall!")
                dead_beams.add(beam)
                continue
            if new_beam := beam.act_on_position():
                # A new beam was returned due to a split.
                new_beams.add(new_beam)
        beams.update(new_beams)
        beams.difference_update(dead_beams)
        if not beams:
            break
    # print(Beam.visited)
    # Beam.print_visited()
    # Subtract 1 because I'm starting off screen.
    return len(Beam.visited) - 1

# 1xxx too low
# 7544 too high

def part2(data: str) -> int:
    wall_width = data.find('\n')
    wall_height = data.count('\n')
    Beam.wall_width = wall_width
    Beam.wall_height = wall_height

    for y, row in enumerate(reversed(data.splitlines())):
        for x, char in enumerate(row):
            if char == ".":
                continue
            # print(f"{char} at {x}, {y}")
            Beam.actors[(x, y)] = char

    beams = set()
    starting_positions = [(x-1, -1, Direction.UP) for x in range(wall_width)]
    starting_positions.extend([(x-1, wall_height, Direction.DOWN) for x in range(wall_width)])
    starting_positions.extend([(-1, y-1, Direction.RIGHT) for y in range(wall_height)])
    starting_positions.extend([(wall_width, y-1, Direction.UP) for y in range(wall_height)])

    total = 0
    for starting_position in starting_positions:
        beams = set()
        Beam.visited_dir = set()
        beams.add(Beam(*starting_position))
        for i in range(10000):
            # print(beams)
            new_beams = set()
            dead_beams = set()
            for beam in beams:
                # beam.print_me()
                is_on_wall = beam.step()
                if not is_on_wall:
                    # print("off the wall!")
                    dead_beams.add(beam)
                    continue
                if new_beam := beam.act_on_position():
                    # A new beam was returned due to a split.
                    new_beams.add(new_beam)
            beams.update(new_beams)
            beams.difference_update(dead_beams)
            if not beams:
                break
        # Subtract 1 because I'm starting off-screen.
        total = max(total, len(Beam.visited) - 1)
    return total


class Beam:
    # Class properties.
    wall_width = 0
    wall_height = 0
    actors = dict()
    # Set of tuples (x, y, dir)
    visited_dir = set()

    def __init__(self, x: int, y: int, direction: Direction) -> None:
        self.x = x
        self.y = y
        self.dir = direction

    def __repr__(self):
        return f"Beam ({self.x}, {self.y}) going {self.dir}"

    @property
    def position(self) -> tuple[int]:
        return self.x, self.y

    @classmethod
    @property
    def visited(cls) -> set[tuple[int]]:
        """Return without direction."""
        return set([(x, y) for x, y, _ in cls.visited_dir])

    def step(self) -> bool:
        """Returns True if still on the map and not repeating a previous
        path."""
        pos_dir = (*self.position, self.dir)
        if pos_dir in self.visited_dir:
            return False

        self.visited_dir.add(pos_dir)
        if self.dir == Direction.LEFT:
            self.x -= 1
        elif self.dir == Direction.RIGHT:
            self.x += 1
        elif self.dir == Direction.DOWN:
            self.y -= 1
        elif self.dir == Direction.UP:
            self.y += 1
        if self.x < 0 or self.x >= self.wall_width or self.y < 0 or self.y >= self.wall_height:
            return False
        return True

    def act_on_position(self):
        """Returns the split beam if split."""
        tile_type = self.actors.get(self.position, "")
        if not tile_type:
            return
        # Turn direction depends on if the thing is moving in a right-handed or
        # left-handed direction (odd or even). Use this as a sign on the turn.
        #
        # --> \ results in down. \ <-- results in up (right turns). up \ results
        # in left, down \ results in right (left turns). left and right are
        # even, so handedness will be set to 1.
        handedness = -1 if self.dir % 2 else 1
        if tile_type == "\\":
            # Turn to the right (clockwise).
            self.turn(handedness)
        elif tile_type == "/":
            # Turn to the left (counterclockwise).
            self.turn(-1*handedness)
        elif tile_type == "|":
            if self.dir == Direction.UP or self.dir == Direction.DOWN:
                return
            # Split.
            self.dir = Direction.UP
            return Beam(*self.position, Direction.DOWN)
        elif tile_type == "-":
            if self.dir == Direction.LEFT or self.dir == Direction.RIGHT:
                return
            # Split.
            self.dir = Direction.LEFT
            return Beam(*self.position, Direction.RIGHT)

    def turn(self, hand):
        if hand == 1:
            self.dir = self.dir + 1 if self.dir < max(Direction) else min(Direction)
        elif hand == -1:
            self.dir = self.dir - 1 if self.dir > min(Direction) else max(Direction)
        else:
            raise ValueError(f"{hand} isn't a valid handedness to turn!")

    def print_me(self) -> None:
        print(self)
        for y in reversed(range(self.wall_height)):
            for x in range(self.wall_width):
                if (x, y) in self.actors:
                    if x == self.x and y == self.y:
                        print("*", end="")
                    else:
                        print(self.actors[(x, y)], end="")
                elif x == self.x and y == self.y:
                    if self.dir == Direction.LEFT:
                        print("<", end="")
                    elif self.dir == Direction.RIGHT:
                        print(">", end="")
                    elif self.dir == Direction.DOWN:
                        print("v", end="")
                    elif self.dir == Direction.UP:
                        print("^", end="")
                else:
                    print(".", end="")
            print()

    @classmethod
    def print_visited(cls) -> None:
        for y in reversed(range(cls.wall_height)):
            for x in range(cls.wall_width):
                if (x, y) in cls.visited:
                    print("#", end="")
                else:
                    print(".", end="")
            print()

if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
