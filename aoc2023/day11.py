"""Day N."""

from functools import partial
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day11')

def part1(data: str) -> int:
    space = []
    vertical_offset = data.find("\n") + 1
    rows_without_galaxies = []
    for row_idx, spatial_row in enumerate(data.splitlines()):
        this_row = []
        galaxy_idx = -1
        for _ in spatial_row:
            galaxy_idx = spatial_row.find("#", galaxy_idx+1)
            if galaxy_idx == -1:
                # No more found.
                break
            this_row.append(galaxy_idx)
        else:
            print(this_row)
            raise RuntimeError("Something didn't work in galaxy finding.")
        if not this_row:
            # No galaxies here, apply 'vertical' spatial expansion.
            rows_without_galaxies.append(row_idx)
        space.append(this_row)

    # We've found all of the galaxies, now evaluate horizontal spatial expansion.
    cols_with_galaxies = set()
    for row in space:
        cols_with_galaxies.update(row)

    cols_without_galaxies = list(cols_with_galaxies.symmetric_difference(range(vertical_offset)))
    # Since we're shifting leftward, start from the right.
    cols_without_galaxies.sort(reverse=True)
    print(rows_without_galaxies)
    print(cols_without_galaxies)
    print(space)
    # Now, with space expanded fully, go row by row and find the relationship
    # with those galaxies in the row and above (more efficient to pop from the
    # end of a list).
    distances = []
    get_dist = partial(
        calc_distance,
        spatial_expansion_factor=1,
        rows_without_galaxies=rows_without_galaxies,
        cols_without_galaxies=cols_without_galaxies,
    )
    while space:
        row = space.pop()
        while row:
            this_galaxy = row.pop()
            # Those in the row with it.
            distances.extend([get_dist((0, this_galaxy), (0, other_galaxy)) for other_galaxy in row])
            # Those above it.
            for other_idx, other_row in enumerate(space):
                distances.extend([get_dist((len(space), this_galaxy), (other_idx, other_galaxy)) for other_galaxy in other_row])
    print(distances)
    return sum(distances)



def part2(data: str) -> int:
    space = []
    vertical_offset = data.find("\n") + 1
    rows_without_galaxies = []
    for row_idx, spatial_row in enumerate(data.splitlines()):
        this_row = []
        galaxy_idx = -1
        for _ in spatial_row:
            galaxy_idx = spatial_row.find("#", galaxy_idx+1)
            if galaxy_idx == -1:
                # No more found.
                break
            this_row.append(galaxy_idx)
        else:
            print(this_row)
            raise RuntimeError("Something didn't work in galaxy finding.")
        if not this_row:
            # No galaxies here, apply 'vertical' spatial expansion.
            rows_without_galaxies.append(row_idx)
        space.append(this_row)

    # We've found all of the galaxies, now evaluate horizontal spatial expansion.
    cols_with_galaxies = set()
    for row in space:
        cols_with_galaxies.update(row)

    cols_without_galaxies = list(cols_with_galaxies.symmetric_difference(range(vertical_offset)))
    # Since we're shifting leftward, start from the right.
    cols_without_galaxies.sort(reverse=True)
    print(rows_without_galaxies)
    print(cols_without_galaxies)
    print(space)
    # Now, with space expanded fully, go row by row and find the relationship
    # with those galaxies in the row and above (more efficient to pop from the
    # end of a list).
    distances = []
    get_dist = partial(
        calc_distance,
        spatial_expansion_factor=1000000,
        rows_without_galaxies=rows_without_galaxies,
        cols_without_galaxies=cols_without_galaxies,
    )
    while space:
        row = space.pop()
        while row:
            this_galaxy = row.pop()
            # Those in the row with it.
            distances.extend([get_dist((0, this_galaxy), (0, other_galaxy)) for other_galaxy in row])
            # Those above it.
            for other_idx, other_row in enumerate(space):
                distances.extend([get_dist((len(space), this_galaxy), (other_idx, other_galaxy)) for other_galaxy in other_row])
    print(distances)
    return sum(distances)

def calc_distance(
    this_galaxy: tuple,  # row, col
    that_galaxy: tuple,  # row, col
    spatial_expansion_factor: int,
    rows_without_galaxies: list,
    cols_without_galaxies: list,
) -> int:
    row_range = [this_galaxy[0], that_galaxy[0]]
    row_range.sort()
    col_range = [this_galaxy[1], that_galaxy[1]]
    col_range.sort()
    expansion_offset = 0
    for row in rows_without_galaxies:
        if row_range[0] < row < row_range[1]:
            expansion_offset += spatial_expansion_factor - 1 or 1
    for col in cols_without_galaxies:
        if col_range[0] < col < col_range[1]:
            expansion_offset += spatial_expansion_factor - 1 or 1

    distance = expansion_offset + (row_range[1] - row_range[0]) + (col_range[1] - col_range[0])
    return distance

if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
