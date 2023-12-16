"""Run each day against its test input."""

from pathlib import Path

from pytest import mark
import aoc2023


HERE = Path(__file__).parent


@mark.parametrize(
    argnames=['file', 'fn', 'expected'],
    argvalues=[
        # Put the most recent at the top to help speed things up.
        ('d16', aoc2023.day16.part2, 51),
        ('d16', aoc2023.day16.part1, 46),
        # ('d15_2', aoc2023.day15.part2, 145),
        # ('d15_2', aoc2023.day15.part1, 1320),
        # ('d15_1', aoc2023.day15.part1, 52),
        # ('d14', aoc2023.day14.part2, 64),
        # ('d14', aoc2023.day14.part1, 136),
        # ('d13', aoc2023.day13.part2, 400),
        # ('d13', aoc2023.day13.part1, 405),
        # ('d12', aoc2023.day12.part2, 525152),
        # ('d12', aoc2023.day12.part1, 21),
        # ('d11', aoc2023.day11.part2, 8410),
        # ('d11', aoc2023.day11.part2, 1030),
        # ('d11', aoc2023.day11.part1, 374),
        # ('d10_5', aoc2023.day10.part2, 10),
        # ('d10_4', aoc2023.day10.part2, 8),
        # ('d10_3', aoc2023.day10.part2, 4),
        # ('d10_2', aoc2023.day10.part1, 8),
        # ('d10_1', aoc2023.day10.part1, 4),
        # ('d9', aoc2023.day9.part2, 2),
        # ('d9', aoc2023.day9.part1, 114),
        # ('d8_3', aoc2023.day8.part2, 6),
        # ('d8_2', aoc2023.day8.part1, 6),
        # ('d8_1', aoc2023.day8.part1, 2),
        # ('d7', aoc2023.day7.part2, 5905),
        # ('d7', aoc2023.day7.part1, 6440),
        # ('d6', aoc2023.day6.part2, 71503),
        # ('d6', aoc2023.day6.part1, 288),
        # ('d5', aoc2023.day5.part2, 46),
        # ('d5', aoc2023.day5.part1, 35),
        # ('d4p2', aoc2023.day4.part2, 30),
        # ('d4p1', aoc2023.day4.part1, 13),
        # ('d3p2', aoc2023.day3.part2, 467835),
        # ('d3p1', aoc2023.day3.part1, 4361),
        # ('d2p2', aoc2023.day2.part2, 2286),
        # ('d2p1', aoc2023.day2.part1, 8),
        # ('d1p2', aoc2023.day1.part2, 281+83+79),
        # ('d1p1', aoc2023.day1.part2, 142),
    ]
)
def test_part(file: str, fn, expected: int) -> None:
    with open(Path(HERE, 'inputs', file)) as f:
        data = f.read()
    assert fn(data) == expected
