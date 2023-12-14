"""Day N."""

from copy import deepcopy
from collections import namedtuple
from functools import partial
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day14')


# X -> column, Y -> row, measured from bottom left.
Position = namedtuple("Position", ['x', 'y'])


def part1(data: str) -> int:
    # LUT by column since moving north.
    width = data.find('\n')
    height = data.count('\n')
    sort_lut_lists_ = partial(sort_lut_lists, asc=True)

    cubes_cols = dict()
    mobile_rocks_cols = dict()
    for y, row in enumerate(reversed(data.splitlines())):
        for x, symbol in enumerate(row):
            if symbol == 'O':
                add_to_lut(x, y, mobile_rocks_cols)
            elif symbol == '#':
                add_to_lut(x, y, cubes_cols)
    sort_lut_lists_(cubes_cols)
    sort_lut_lists_(mobile_rocks_cols)

    # Add a barrier to the top.
    for col in range(width):
        add_to_lut(col, height, cubes_cols)

    # We've now found where they all are. To move them north, for each movable
    # rock, I need to move it up until it hits a stationary rock. Doesn't matter
    # if I do this in order (my rocks can 'jump' over others) since they don't
    # have varying masses.
    #
    # Still need to keep track of cubes to exclude them from the mass
    # calculation.
    moved_rocks_cols = evaluate_tilt(cubes_cols, mobile_rocks_cols, 1)

    moved_rocks_rows = transpose_lut(moved_rocks_cols)
    # print_rows_lut(moved_rocks_rows, transpose_lut(cubes_cols), width)

    total = 0
    for row_idx, row in moved_rocks_rows.items():
        total += len(row)*(row_idx+1)

    return total


def part2(data: str) -> int:
    # LUT by column since moving north.
    width = data.find('\n')
    height = data.count('\n')
    sort_lut_lists_ = partial(sort_lut_lists, asc=True)

    cubes_cols = dict()
    mobile_rocks_cols = dict()
    for y, row in enumerate(reversed(data.splitlines())):
        for x, symbol in enumerate(row):
            if symbol == 'O':
                add_to_lut(x, y, mobile_rocks_cols)
            elif symbol == '#':
                add_to_lut(x, y, cubes_cols)
    sort_lut_lists_(cubes_cols)
    sort_lut_lists_(mobile_rocks_cols)

    # Add a barrier to the borders.
    for col in range(width):
        # To the top and bottom.
        add_to_lut(col, height, cubes_cols)
        add_to_lut(col, -1, cubes_cols)
    sort_lut_lists_(cubes_cols)
    # To the sides.
    cubes_cols[-1] = list(range(height))
    cubes_cols[width] = list(range(height))

    # We've now found where they all are. To move them north, for each movable
    # rock, I need to move it up until it hits a stationary rock. Doesn't matter
    # if I do this in order (my rocks can 'jump' over others) since they don't
    # have varying masses.
    #
    # Still need to keep track of cubes to exclude them from the mass
    # calculation.
    previous_loads = []
    N_CYCLES = 1000000000
    for i in range(500):
        next_mobile_cols = run_one_spin_cycle(cubes_cols, mobile_rocks_cols)
        load = compute_load(next_mobile_cols)
        if load in previous_loads:
            offset = previous_loads.index(load)
            # Zero out the previously measured one so I can allow the cycles to
            # settle out.
            previous_loads[offset] = -1
            # Check if (assuming it cycles) this will land on N_CYCLES.
            freq = i - offset
            print(f"Found a repeat ({load}) with offset {offset} with frequency {freq}.")
            if i > 7 and (N_CYCLES - offset - 1) % freq == 0:
                print(f"Expecting {load} to be the load at {N_CYCLES}")
                # return load
        previous_loads.append(load)
        mobile_rocks_cols = next_mobile_cols

    print(f"Measured loads: {previous_loads}")
    # print("Final:")
    # print_rows_lut(transpose_lut(next_mobile_cols), transpose_lut(cubes_cols), width)

    return load

# 93730 is too low.


def move_rock_along_file_until_stopped(
    rock_pos: int,
    stationary_rocks: list[int],
    mobile_rocks: list[int],
    direction: int,
) -> Position:
    rocks = stationary_rocks.copy()
    if rock_pos in rocks:
        raise NotImplementedError()
    rocks.append(rock_pos)
    rocks.sort()
    idx = rocks.index(rock_pos)
    lands_against = rocks[idx+direction]

    potential_pos = lands_against - direction

    while potential_pos in mobile_rocks:
        potential_pos -= direction

    return potential_pos


def compute_load(mobile_rocks_rows: dict[int, list]) -> int:
    """Slick way to hash these big dictionaries."""
    mobile_rocks_rows = transpose_lut(mobile_rocks_rows)
    total = 0
    for row_idx, row in mobile_rocks_rows.items():
        total += len(row)*(row_idx+1)
    return total


def run_one_spin_cycle(
    cubes_cols: dict[int, list],
    mobile_rocks_cols: dict[int, list],
) -> dict[int, list]:
    cubes_rows = transpose_lut(cubes_cols)
    width = max(cubes_cols.keys())
    # print("Start cycle:")
    # print_rows_lut(transpose_lut(mobile_rocks_cols), cubes_rows, width)

    tilted_north = evaluate_tilt(cubes_cols, mobile_rocks_cols, 1)
    # print("Tilted North:")
    # print_rows_lut(transpose_lut(tilted_north), cubes_rows, width)

    tilted_west = evaluate_tilt(cubes_rows, transpose_lut(tilted_north), -1)
    # print("Tilted West:")
    # print_rows_lut(tilted_west, cubes_rows, width)

    tilted_south = evaluate_tilt(cubes_cols, transpose_lut(tilted_west), -1)
    # print("Tilted South:")
    # print_rows_lut(transpose_lut(tilted_south), cubes_rows, width)

    tilted_east = evaluate_tilt(cubes_rows, transpose_lut(tilted_south), 1)
    # print("Tilted East:")
    # print_rows_lut(tilted_east, cubes_rows, width)

    spun = transpose_lut(tilted_east)
    return spun


def evaluate_tilt(
    cubes_cols: dict[int, list],
    mobile_rocks_cols: dict[int, list],
    direction: int,
) -> dict[int, list]:
    stationary_rocks_cols = deepcopy(cubes_cols)
    new_mobile_rocks = dict()
    for idx, col in mobile_rocks_cols.items():
        while col:
            # Get the rock closest to the top of the map.
            next_rock = col.pop()
            new_pos = move_rock_along_file_until_stopped(
                next_rock,
                stationary_rocks_cols.get(idx, []),
                col,
                direction,
            )
            stationary_rocks_cols[idx].append(new_pos)
            stationary_rocks_cols[idx].sort()
            add_to_lut(idx, new_pos, new_mobile_rocks)
    return new_mobile_rocks


def transpose_lut(rocks: dict[int, list]) -> dict[int, list]:
    """Switch from lut[x] = [y1, y2, ...] to lux[y] = [x1, x2, ...]"""
    new_lut = dict()
    for x, list_y in rocks.items():
        for y in list_y:
            add_to_lut(y, x, new_lut)
    return new_lut


def sort_lut_lists(lut: dict[int, list], asc: bool) -> None:
    """(Side effect) Sort ascending."""
    for list_ in lut.values():
        list_.sort(reverse=not asc)


def add_to_lut(key: int, value: int, lut: dict[int, list]) -> None:
    """(Side effect) Specifically for adding to lists in the luts."""
    try:
        lut[key].append(value)
    except KeyError:
        lut[key] = [value]


def print_rows_lut(mobile: dict[int, list], stuck: dict[int, list], width: int) -> None:
    for i in reversed(range(max(stuck.keys()))):
        for j in range(width):
            if j in mobile.get(i, []):
                print("O", end="")
            elif j in stuck.get(i, []):
                print("#", end="")
            else:
                print(".", end="")
        print()


if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
