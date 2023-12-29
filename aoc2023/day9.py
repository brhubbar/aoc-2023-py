"""Day N."""

from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day9')


def part1(data: str) -> int:
    total = 0
    for variable in data.splitlines():
        history = [int(x) for x in variable.split()]
        total += find_next_point(history)

    return total


def part2(data: str) -> int:
    total = 0
    for variable in data.splitlines():
        history = [int(x) for x in variable.split()]
        history.reverse()
        total += find_next_point(history)

    return total


def find_next_point(history: list[int]) -> int:
    diff = history
    serieses = [history]
    while True:
        # Go down in the diffs.
        diff = calc_diff(diff)
        serieses.append(diff)
        if all([x == 0 for x in diff]):
            break
    # print(serieses)
    # Start from the last added point (a 0).
    serieses.reverse()
    for i in range(len(serieses)-1):
        diff = serieses[i]
        to_extrapolate = serieses[i+1]
        to_extrapolate.append(extrapolate(to_extrapolate, diff))
    return serieses[-1][-1]


def calc_diff(series: list[int]) -> list[int]:
    """Return the discrete derivative of series."""
    diff = [0] * (len(series)-1)
    for i in range(len(diff)):
        diff[i] = series[i+1] - series[i]
    return diff


def extrapolate(series: list[int], diff: list[int]) -> int:
    """Return the next point in series based on diff."""
    if not diff:
        breakpoint()
    return series[-1] + diff[-1]


if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
