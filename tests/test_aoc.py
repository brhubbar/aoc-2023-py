"""Run each day against its test input."""

from pathlib import Path

from pytest import mark
import aoc2023


HERE = Path(__file__).parent


@mark.parametrize(
    argnames=['file', 'fn', 'expected'],
    argvalues=[
        # Put the most recent at the top to help speed things up.
        ('d2p2', aoc2023.day2.part2, 2286),
        ('d2p1', aoc2023.day2.part1, 8),
        # ('d1p2', aoc2023.day1.part2, 281+83+79),
        # ('d1p1', aoc2023.day1.part2, 142),
    ]
)
def test_part_1(file: str, fn, expected: int) -> None:
    with open(Path(HERE, 'inputs', file)) as f:
        data = f.read()
    assert fn(data) == expected
