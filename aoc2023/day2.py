"""Day N."""

import re
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day2')

R = re.compile(r'(\d+) red')
G = re.compile(r'(\d+) green')
B = re.compile(r'(\d+) blue')

def part1(data: str) -> int:
    ALLOWED_R = 12
    ALLOWED_G = 13
    ALLOWED_B = 14

    result = 0

    for game in data.splitlines():
        name, pulls = game.split(':', 1)
        game_id = int(name.removeprefix('Game '))
        max_r = max_g = max_b = 0
        for pull in pulls.split(';'):
            # Measure by pull in case that matters somehow (it ended up not.)
            max_r = max(max_r, qty(R.findall(pull)))
            max_g = max(max_g, qty(G.findall(pull)))
            max_b = max(max_b, qty(B.findall(pull)))
        if (
            max_r <= ALLOWED_R
            and max_g <= ALLOWED_G
            and max_b <= ALLOWED_B
        ):
            result += game_id

    return result

def qty(search_result: list) -> int:
    """Return the number or 0 if none."""
    try:
        return int(search_result[0])
    except IndexError:
        return 0



def part2(data: str) -> int:
    result = 0

    for game in data.splitlines():
        _, pulls = game.split(':', 1)
        max_r = max_g = max_b = 0
        for pull in pulls.split(';'):
            max_r = max(max_r, qty(R.findall(pull)))
            max_g = max(max_g, qty(G.findall(pull)))
            max_b = max(max_b, qty(B.findall(pull)))
        power = max_r * max_g * max_b
        result += power
    return result


if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
