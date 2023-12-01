"""Day 1."""

import re
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day1')


first = re.compile(r'[^\d]*(\d).*$')
last = re.compile(r'.*(\d)[^\d]*$')
fixed_first = re.compile(r'(\d|one|two|three|four|five|six|seven|eight|nine)')
fixed_last = re.compile(r'.*(\d|one|two|three|four|five|six|seven|eight|nine)')


def part1(data: str) -> float:
    total = 0
    for line in data.splitlines():
        digit1 = first.search(line)
        digit2 = last.search(line)
        if not digit1 or not digit2:
            breakpoint()
        total += int(digit1.group(1) + digit2.group(1))

    return total


def part2(data: str) -> float:
    total = 0
    for line in data.splitlines():
        digit1 = word_to_digit(fixed_first.findall(line.lower())[0])
        digit2 = word_to_digit(fixed_last.findall(line.lower())[-1])

        val = int(digit1 + digit2)

        print(line, val)

        total += val

    return total


def word_to_digit(word: str) -> str:
    if len(word) == 1:
        return word
    elif word == 'one':
        return '1'
    elif word == 'two':
        return '2'
    elif word == 'three':
        return '3'
    elif word == 'four':
        return '4'
    elif word == 'five':
        return '5'
    elif word == 'six':
        return '6'
    elif word == 'seven':
        return '7'
    elif word == 'eight':
        return '8'
    elif word == 'nine':
        return '9'


if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
