"""Day N."""

from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day6')


def part1(data: str) -> int:
    time_string, distance_string = data.splitlines()
    time_strings = time_string.split()
    distance_strings = distance_string.split()

    # Drop the label.
    time_strings.pop(0)
    distance_strings.pop(0)

    times_ms = [int(x) for x in time_strings]
    distances_mm = [int(x) for x in distance_strings]

    total = 1
    for time, record_distance in zip(times_ms, distances_mm):
        possible_hold_times = range(time)
        n_winning_options = 0
        for hold_time in possible_hold_times:
            # Hold for 6 seconds, travel for 1, total time is 7.
            travel_time = time - hold_time
            speed_mm_ms = hold_time
            travel_distance = speed_mm_ms * travel_time
            if travel_distance > record_distance:
                n_winning_options += 1
        total *= n_winning_options

    return total


def part2(data: str) -> int:
    time_string, distance_string = data.splitlines()
    time_strings = time_string.split()
    distance_strings = distance_string.split()

    # Drop the label.
    time_strings.pop(0)
    distance_strings.pop(0)

    time_ms = int(''.join(time_strings))
    distance_mm = int(''.join(distance_strings))

    possible_hold_times = range(time_ms)
    n_winning_options = 0
    for hold_time in possible_hold_times:
        # Find minimum hold time.
        # Hold for 6 seconds, travel for 1, total time is 7.
        travel_time = time_ms - hold_time
        speed_mm_ms = hold_time
        travel_distance = speed_mm_ms * travel_time
        if travel_distance > distance_mm:
            # This'll be subtracted from in the next loop.
            n_winning_options = hold_time
            break

    possible_hold_times_from_the_top = range(time_ms-1, -1, -1)
    for hold_time in possible_hold_times_from_the_top:
        travel_time = time_ms - hold_time
        speed_mm_ms = hold_time
        travel_distance = speed_mm_ms * travel_time
        if travel_distance > distance_mm:
            # This'll be subtracted from in the next loop.
            n_winning_options = hold_time - n_winning_options + 1
            break

    return n_winning_options


if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
