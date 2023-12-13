"""Day N."""

import re
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day12')


BROKEN = "#"
OPERATIONAL = "."
UNSURE = "?"

def part1(data: str) -> int:
    total = 0
    for row in data.splitlines():
        springs, damaged = row.split()
        n_damageds = [int(x) for x in damaged.split(',')]
        is_damaged_list = []
        for n_damaged in n_damageds:
            for _ in range(n_damaged):
                is_damaged_list.append(True)
            is_damaged_list.append(False)
        # Drop that last False.
        is_damaged_list.pop()

        total += count_arrangements(springs, is_damaged_list)

    return total


def part2(data: str) -> int:
    total = 0
    for row in data.splitlines():
        springs, damaged = row.split()
        n_damageds = [int(x) for x in damaged.split(',')]
        is_damaged_list = []
        for n_damaged in n_damageds:
            for _ in range(n_damaged):
                is_damaged_list.append(True)
            is_damaged_list.append(False)

        # Apply the twist.
        springs = '?'.join([springs]*5)
        is_damaged_list = is_damaged_list*5

        # Drop that last False.
        is_damaged_list.pop()

        # print(springs)
        # print(is_damaged_list)

        total += count_arrangements(springs, is_damaged_list)

    return total


def count_arrangements(springs: str, is_damaged_list: list[bool]) -> int:
    """
    Full credit to Reddit.

    https://www.reddit.com/r/adventofcode/comments/18ge41g/comment/kd18cl9/

    Parameters
    ----------
    springs : str
        Each character indicates a spring type (. = operational, # = broken, ? =
        either)
    is_damaged_list : list of bool
        Each True indicates a damaged spring. Each False indicates 1 or more
        operational springs.

    """
    # Ensure start/stop are always the same.
    springs = f'.{springs}.'
    is_damaged_list = [False, *is_damaged_list, False]

    n_arrangements_from_idx_to_end = [[0]*(len(springs)+1) for _ in range(len(is_damaged_list)+1)]
    # This is used just to get things kicked off, and forces (allows?) indexing
    # from 1.
    n_arrangements_from_idx_to_end[0][0] = 1
    for last_spring_idx, spring in enumerate(springs):
        for last_expect_idx, expect_damaged in enumerate(is_damaged_list):
            is_damaged = is_operational = False

            if spring == "#":
                # There *is* a damaged spring here.
                is_damaged = True
            elif spring == ".":
                # There is *not* a damaged spring here.
                is_operational = True
            else:
                # There could be a damaged spring here.
                is_damaged = is_operational = True

            if is_damaged and expect_damaged:
                # We are expecting a damaged spring, and we have one. This is a
                # possible arrangement, and will be marked as such IFF there is
                # a history of valid arrangements along this line of thinking.
                n_arrangements = n_arrangements_from_idx_to_end[last_expect_idx][last_spring_idx]  # Previous expect, previous character.
            elif is_operational and not expect_damaged:
                # We are expecting an operational spring, and we found one. This
                # is a possible arrangement, and will be marked as such IFF there is
                # a history of valid arrangements along this line of thinking.
                n_arrangements = (
                    n_arrangements_from_idx_to_end[last_expect_idx][last_spring_idx]  # Previous expect, previous character.
                    + n_arrangements_from_idx_to_end[last_expect_idx+1][last_spring_idx]  # This expect, previous character.
                )
            else:
                # This is not a valid arrangement, chop this chain.
                n_arrangements = 0
            n_arrangements_from_idx_to_end[last_expect_idx+1][last_spring_idx+1] = n_arrangements
    # for list_ in n_arrangements_from_idx_to_end:
    print(n_arrangements_from_idx_to_end[-1][-1])
    return n_arrangements_from_idx_to_end[-1][-1]



if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
