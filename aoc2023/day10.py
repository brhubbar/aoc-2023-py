"""Day N."""

from collections import namedtuple
from functools import partial
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day10')

# Defined with CW first.
PIPE_TYPES = {
    '|': 'ns',
    '-': 'ew',
    'L': 'ne',
    'J': 'wn',
    '7': 'sw',
    'F': 'es',
}

CW_CHECK_ORDER = 'nesw'

Movement = namedtuple('Movement', ['end_pos', 'coming_from'])

def part1(data: str) -> int:
    # Find S.
    starting_point = data.find("S")
    starting_point_type = determine_starting_point_type(data, starting_point)
    print(f"Found start at {starting_point} of type {starting_point_type}")
    pipe_mask = get_pipe_mask(data, starting_point, starting_point_type)
    return len(pipe_mask) / 2


def part2(data: str) -> int:
    # Find S.
    starting_point = data.find("S")
    starting_point_type = determine_starting_point_type(data, starting_point)
    pipe_mask = get_pipe_mask(data, starting_point, starting_point_type)
    print_mask(data, pipe_mask)

    # Allow us to reach back to the starting point.
    pipe_mask.append(pipe_mask[0])

    try:
        interior_mask = get_interior_mask(data, pipe_mask)
    except ValueError:
        # Probably just need to reverse it. (Not sure if it matters that S
        # doesn't get evaluated. I can swap in the proper type if need be).
        pipe_mask.reverse()
        interior_mask = get_interior_mask(data, pipe_mask)
    except IndexError:
        # Seems like we went out of bounds. Probably just need to reverse it.
        # (Not sure if it matters that S doesn't get evaluated. I can swap in
        # the proper type if need be).
        pipe_mask.reverse()
        interior_mask = get_interior_mask(data, pipe_mask)

    print_mask(data, interior_mask)
    return len(interior_mask)


def get_interior_mask(data: str, pipe_mask: list[int]) -> int:
    """
    Compute the area within the boundary defined.

    Assumes that increasing index --> CW movement. Missing this assumption
    results in a value error (hinting that you should reverse the list...)

    """
    interior_mask = set()
    vertical_step_offset = data.find('\n') + 1
    for idx in range(len(pipe_mask)-1):
        this_pipe = pipe_mask[idx]
        next_pipe = pipe_mask[idx + 1]

        print(f"Evaluating {data[this_pipe]} at {this_pipe}.", end=" ")
        if next_pipe == this_pipe + 1:
            # East! Look south.
            walk_offset = vertical_step_offset
        elif next_pipe == this_pipe - 1:
            # West! Look north.
            walk_offset = -vertical_step_offset
        elif next_pipe < this_pipe:
            # North! Look east.
            walk_offset = 1
        elif next_pipe > this_pipe:
            # South! Look west.
            walk_offset = -1
        else:
            print(this_pipe, next_pipe)
            raise ValueError("Not sure where we are!")
        print(f", walking {walk_offset}")

        for eval_point in (this_pipe, next_pipe):
            # Check this pipe and the next one for this direction. Inefficient,
            # but hopefully sufficient.
            for _ in range(vertical_step_offset):
                # Prevent an infinite loop (the grid is square).
                eval_point += walk_offset
                if eval_point in pipe_mask:
                    # Hit another bound! Bail.
                    break
                print(f"Found an interior point ({data[eval_point]}) at {eval_point}")
                interior_mask.add(eval_point)
            else:
                raise ValueError("Didn't hit another pipe in the loop?!")
    return interior_mask


def get_pipe_mask(
    data: str,
    starting_point: int,
    starting_point_type: str,
) -> list[int]:
    """
    Return a list of indices in the data string where the pipe lies.

    Cannot guarantee CW vs CCW.

    """
    pipe_mask = [starting_point]
    last_pipe_type = starting_point_type
    coming_from = ''

    # number of characters to shift to step up or down.
    move_compass_ = partial(move_compass, vertical_step_offset=data.find('\n') + 1)
    while True:
        valid_directions = PIPE_TYPES[last_pipe_type]
        valid_directions = valid_directions.replace(coming_from, '')
        # print(f"Checking {last_pipe_type} at {pipe_mask[-1]}, moving {valid_directions} and not {coming_from}")
        for valid_direction in valid_directions:
            test_move = move_compass_(pipe_mask[-1], valid_direction)
            # print(f"Moved {valid_direction} to {test_move}")
            # Assuming here that we never fall out of bounds of the sketch.
            test_pipe_type = data[test_move.end_pos]
            test_pipe_directions = PIPE_TYPES.get(test_pipe_type, '')

            if test_move.coming_from in test_pipe_directions:
                # This is a valid meeting point.
                pipe_mask.append(test_move.end_pos)
                last_pipe_type = test_pipe_type
                coming_from = test_move.coming_from
                # print(f"Found a valid pipe, {test_pipe_type} at {pipe_mask[-1]}\n")
                break
        else:
            # No valid pipes found, so we either made it around, or found an
            # opening.
            if test_move.end_pos == starting_point:
                # Check for the end of the loop.
                return pipe_mask

            print(pipe_mask)
            raise RuntimeError("Not a continuous pipe!")


def move_compass(start_pos: int, direction: str, vertical_step_offset: int) -> Movement:
    """Move one step in the cardinal direction. North is up."""
    if direction == 'n':
        return Movement(start_pos - vertical_step_offset, 's')
    if direction == 's':
        return Movement(start_pos + vertical_step_offset, 'n')
    if direction == 'e':
        return Movement(start_pos + 1, 'w')
    if direction == 'w':
        return Movement(start_pos - 1, 'e')


def determine_starting_point_type(data: str, starting_point: int) -> str:
    """Check to the nsew for pipes which validly connect."""
    move_compass_ = partial(move_compass, vertical_step_offset=data.find('\n') + 1)

    valid_directions = ''
    for move in 'nsew':
        test_move = move_compass_(starting_point, move)
        test_pipe_type = PIPE_TYPES.get(data[test_move.end_pos], '')

        if test_move.coming_from in test_pipe_type:
            valid_directions = ''.join([valid_directions, move])

    if len(valid_directions) > 2:
        raise RuntimeError("It's a Tee?")

    for pipe, type_ in PIPE_TYPES.items():
        for character in type_:
            if character not in valid_directions:
                break
        else:
            # No break.
            return pipe
        # Break because not a valid pipe.
        continue


def print_mask(data: str, mask: list[int]) -> None:
    for i in range(len(data)):
        if i in mask or data[i] == '\n':
            print(data[i], end='')
            continue
        print(" ", end="")


if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
