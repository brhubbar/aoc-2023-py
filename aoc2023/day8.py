"""Day N."""

import math
import re
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day8')

NODE = re.compile(r"\w\w\w")

def part1(data: str) -> int:
    directions, network = data.split('\n', maxsplit=1)
    directions = directions.replace("L", "0")
    directions = directions.replace("R", "1")
    network = network.strip()

    mapping = dict()
    for node in network.splitlines():
        here, left, right = NODE.findall(node)
        mapping[here] = [left, right]

    here = "AAA"
    end = "ZZZ"
    n_steps = 0
    while True:
        for step in directions:
            # 0 = left, 1 = right.
            here = mapping[here][int(step)]
            n_steps += 1
            if here == end:
                return n_steps


def part2(data: str) -> int:
    directions, network = data.split('\n', maxsplit=1)
    directions = directions.replace("L", "0")
    directions = directions.replace("R", "1")
    network = network.strip()

    mapping = dict()
    for node in network.splitlines():
        here, left, right = NODE.findall(node)
        mapping[here] = [left, right]
    heres = [key for key in mapping.keys() if key.endswith("A")]
    # These prints let you verify that each 'end' will return to the same point
    # as a 'start' will point to. The inputs must be well-crafted to
    # encode/enable that periodicity.
    #
    # ends = [key for key in mapping.keys() if key.endswith("Z")]
    # print(*[f"{here}: {mapping[here]}\n" for here in heres])
    # print(*[f"{end}: {mapping[end]}\n" for end in ends])
    # return 0
    steps_to_ends = [0]*len(heres)
    # These are probably designed to not overlap for a long time, so just figure
    # out the frequency of each path and find the least common multiple to
    # determine when they land. I boldly (and correctly) assumed that each path
    # was periodic, lol.
    for here_idx, here in enumerate(heres):
        n_steps = 0
        while True:
            for step in directions:
                # print(here)
                # 0 = left, 1 = right.
                here = mapping[here][int(step)]
                n_steps += 1
                if here.endswith("Z"):
                    print(n_steps)
                    steps_to_ends[here_idx] = n_steps
                    break
            else:
                # Break not called, try again.
                continue
            # Break called, exit this loop.
            break
    return math.lcm(*steps_to_ends)



if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
