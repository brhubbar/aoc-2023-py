"""Day N."""

from functools import partial
from math import ceil, floor
from pathlib import Path

from aoc2023.day9 import find_next_point

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day21')

N_STEPS_P1 = 64
N_STEPS_P2 = 26501365
# Test value:
# N_STEPS_P1 = 6
N_STEPS_P2 = 500


def part1(data: str) -> int:
    # Travel in all allowed directions.
    #
    # If a spot has been visited before, it's determined already if it's
    # reachable. If a spot is even, it's reachable iff the total number of steps
    # is even. The same is true for odd spots.
    #
    # Each spot has up to 4 neighbors. Neighbors which are rocks or have been
    # visited are excluded.
    width = data.find('\n')
    height = data.count('\n')

    # Set of locations (x, y)
    rocks = set()
    start_point = None

    for y, row in enumerate(data.splitlines()):
        for x, char in enumerate(row):
            if char == '.':
                continue
            elif char == '#':
                rocks.add((x, y))
            elif char == 'S' and start_point is None:
                start_point = (x, y)
            else:
                raise ValueError(f"Unexpected point type {char}")
    return get_n_for_n_steps(N_STEPS_P1, start_point, rocks, width, height)


def part2(data: str) -> int:
    width = data.find('\n')
    height = data.count('\n')

    # Set of locations (x, y)
    rocks = set()
    start_point = None

    for y, row in enumerate(data.splitlines()):
        for x, char in enumerate(row):
            if char == '.':
                continue
            elif char == '#':
                rocks.add((x, y))
            elif char == 'S' and start_point is None:
                start_point = (x, y)
            else:
                raise ValueError(f"Unexpected point type {char}")

    # Some observant people observantly observed that the number of steps is
    # equal to 65 + 202300 * map_width, where map_width = 131. The number of
    # occupiable spots can be determined by a polynomial - therefore, it's
    # differentiable. Using 65+131 and 65+2*131, I can establish a series to
    # then extrapolate (day 9) to the number of occupied spots as demanded by
    # eric.
    #
    # Source:
    # https://www.reddit.com/r/adventofcode/comments/18orn0s/2023_day_21_part_2_links_between_days/

    series = [
        get_n_for_n_steps(65, start_point, rocks, width, height),
        get_n_for_n_steps(65 + 131, start_point, rocks, width, height),
        get_n_for_n_steps(65 + 131*2, start_point, rocks, width, height),
        get_n_for_n_steps(65 + 131*3, start_point, rocks, width, height),
    ]

    # print(get_n_for_n_steps(65 + 131*4, start_point, rocks, width, height))
    # print(get_n_for_n_steps(65 + 131*5, start_point, rocks, width, height))
    # print(get_n_for_n_steps(65 + 131*6, start_point, rocks, width, height))

    for i in range(202300-3):
        # if i < 10 or i % 100 == 0:
        #     # print(f"{i=}")# , {series=}")
        #     series = series[-100:]
        # breakpoint()
        next_ = find_next_point(series)
        # People pointed out that this is quadratic, so 4 points should be
        # plenty to hang onto.
        series.pop(0)
    return next_
# 607340330259531 is too high!



def get_n_for_n_steps(n_steps, start, rocks, width, height) -> int:
    even_spots = set()
    odd_spots = set()
    current_spots = set([start])
    is_a_rock = partial(check_for_tiled_rock, rocks=rocks, width=width, height=height)
    for i_step in range(1, n_steps+1):
        next_current_spots = set()
        for spot in current_spots:
            for neighbor in get_neighbors(*spot):
                if neighbor in even_spots or neighbor in odd_spots:
                    # ALready evaluated - skip.
                    continue
                if is_a_rock(*neighbor):
                    # Invalid position - skip.
                    continue

                if i_step % 2 == 0:
                    # Even.
                    even_spots.add(neighbor)
                else:
                    # Odd.
                    odd_spots.add(neighbor)
                next_current_spots.add(neighbor)
        current_spots = next_current_spots
        # print(f"\nStep {i_step}")
        # print_stuff(width, height, rocks, odd_spots, even_spots)

    if n_steps % 2 == 0:
        return len(even_spots)
    return len(odd_spots)

def get_neighbors(x, y) -> tuple[int]:
    yield x + 1, y
    yield x - 1, y
    yield x, y + 1
    yield x, y - 1


def check_for_tiled_rock(x, y, rocks, width, height) -> bool:
    # (x, y) maps to the nth tile in the x direction and the mth tile in the y
    # direction. Find n and m by floor([x|y] / [w|h]). Map to the base tile by
    # [x|y] - [n|m]*[w|h].
    n = floor(x / width)
    m = floor(y / height)

    x0 = x - n*width
    y0 = y - m*height

    return (x0, y0) in rocks

def print_stuff(
    width: int,
    height: int,
    rocks: set[tuple[int]],
    odd: set[tuple[int]],
    even: set[tuple[int]],
) -> None:
    for y in range(height):
        for x in range(width):
            if (x, y) in rocks:
                print("#", end="")
            elif (x, y) in odd:
                print("O", end="")
            elif (x, y) in even:
                print("E", end="")
            else:
                print(".", end="")
        print()

def print_stuff_p2(
    width: int,
    height: int,
    rocks: set[tuple[int]],
    reachable: set[tuple[int]],
) -> None:
    min_x = min_y = max_x = max_y = 0
    for spot in reachable:
        min_x = min(min_x, spot[0])
        max_x = max(max_x, spot[0])
        min_y = min(min_y, spot[1])
        max_y = max(max_y, spot[1])

    print(f"{min_x=}, {max_x=}, {min_y=}, {max_y=}")

    x_range = floor(min_x/width)*width, (1 + floor(max_x/width))*width
    y_range = floor(min_y/height)*height, (1 + floor(max_y/height))*height
    print(f"{x_range=}, {y_range=}")
    print(f"{len(reachable)=}")

    return
    for y in range(*y_range):
        for x in range(*x_range):
            if check_for_tiled_rock(x, y, rocks, width, height):
                print("#", end="")
            elif (x, y) in reachable:
                print("O", end="")
            else:
                print(".", end="")
        print()

if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
