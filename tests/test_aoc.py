"""Run each day against its test input."""

from pathlib import Path

from pytest import mark
import aoc2023


HERE = Path(__file__).parent


@mark.parametrize(
    argnames=['p1f', 'p2f', 'mod', 'part1', 'part2'],
    argvalues=[
        ('day1p1', 'day1p2', aoc2023.day1, 142, 281+83+79),
    ]
)
def test_part_1(p1f, p2f, mod, part1, part2):
    with open(Path(HERE, 'inputs', p1f)) as f:
        data = f.read()
    assert mod.part1(data) == part1

    with open(Path(HERE, 'inputs', p2f)) as f:
        data = f.read()
    assert mod.part2(data) == part2
