"""Day N."""

import math
import re
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day3')

PART_SYMBOL = re.compile(r'[^\w\d\s.\n]')
GEAR_SYMBOL = re.compile(r'[*]')
PART_NUMBER = re.compile(r'\d+')


def part1(data: str) -> int:
    # Identify index location of every part number.
    #
    # For each part number, search the surrounding 'adjacency space' for a
    # symbol.
    #
    # Adjacency space is the number's span +/- 1, offset +/- the width of a
    # column, totalling to three substrings.
    #
    # TODO: Need to be cautious of wrapping back to previous lines. Should be
    # handled for free by leaving the newlines in, since they shouldn't match.
    COLUMN_WIDTH = data.find('\n') + 1
    TOTAL_SIZE = len(data)
    total = 0

    part_numbers = PART_NUMBER.finditer(data)
    for part_number in part_numbers:
        span = part_number.span(0)
        part_id = int(part_number.group(0))
        search_spans = [
            (span[0]-1-COLUMN_WIDTH, span[1]+1-COLUMN_WIDTH),
            # Clip front/back to ensure we don't wrap backward/IndexError
            (max(0, span[0]-1), min(TOTAL_SIZE, span[1]+1)),
            (span[0]-1+COLUMN_WIDTH, span[1]+1+COLUMN_WIDTH),
        ]
        if search_spans[2][0] > TOTAL_SIZE:
            # Trying to look at a line after the last line. The inputs are s.t.
            # we don't have to worry about wrapping just beyond the end of the
            # line.
            search_spans.pop(2)

        if search_spans[0][1] < 0:
            # Trying to look at a line before the first line. The inputs are
            # s.t. we don't have to worry about wrapping just beyond the end of
            # the line.
            search_spans.pop(0)

        search_space = ''.join(
            [data[slice(*span)] for span in search_spans]
        )
        # print(f"{part_number=}\n{search_spans=}\n{search_space=}\n")

        if PART_SYMBOL.search(search_space):
            print(f"Found symbol in {part_id} space")
            total += part_id

        if len(PART_SYMBOL.findall(search_space)) > 1:
            # This is a quick verification that I won't have to worry about part
            # numbers touching multiple symbols.
            raise RuntimeError(f"{part_number.group(0)} touching two symbols: {search_space}")

    return total


def part2(data: str) -> int:
    # Identify index location of every part number.
    #
    # For each part number, search the surrounding 'adjacency space' for a
    # symbol.
    #
    # Adjacency space is the number's span +/- 1, offset +/- the width of a
    # column, totalling to three substrings.
    #
    # TODO: Need to be cautious of wrapping back to previous lines. Should be
    # handled for free by leaving the newlines in, since they shouldn't match.
    COLUMN_WIDTH = data.find('\n') + 1
    TOTAL_SIZE = len(data)
    total = 0

    part_numbers = PART_NUMBER.finditer(data)
    numbers_to_asterisks = dict()
    for part_number in part_numbers:
        span = part_number.span(0)
        part_id = int(part_number.group(0))
        search_spans = [
            (span[0]-1-COLUMN_WIDTH, span[1]+1-COLUMN_WIDTH),
            # Clip front/back to ensure we don't wrap backward/IndexError
            (max(0, span[0]-1), min(TOTAL_SIZE, span[1]+1)),
            (span[0]-1+COLUMN_WIDTH, span[1]+1+COLUMN_WIDTH),
        ]
        if search_spans[2][0] > TOTAL_SIZE:
            # Trying to look at a line after the last line. The inputs are s.t.
            # we don't have to worry about wrapping just beyond the end of the
            # line.
            search_spans.pop(2)

        if search_spans[0][1] < 0:
            # Trying to look at a line before the first line. The inputs are
            # s.t. we don't have to worry about wrapping just beyond the end of
            # the line.
            search_spans.pop(0)

        for span in search_spans:
            # Search just within the span. Doing this lets be gather the abs.
            # location of the symbol in data.
            match = GEAR_SYMBOL.search(data, *span)
            if match:
                loc = match.span(0)
                parts_touching_this_guy = numbers_to_asterisks.get(loc, [])
                parts_touching_this_guy.append(part_id)
                numbers_to_asterisks[loc] = parts_touching_this_guy
                # I've verified in part 1 that a number never contacts multiple
                # symbols.
                continue
    for parts_touching in numbers_to_asterisks.values():
        if len(parts_touching) > 1:
            total += math.prod(parts_touching)

    return total

if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
