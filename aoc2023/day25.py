"""
Day 25

https://www.reddit.com/r/adventofcode/comments/18qbsxs/comment/ketzp94/

Devised a simple ad-hoc algorithm. We're looking to split the graph into two
components, with exactly three edges crossing the component boundaries. We
define one component as the set of nodes S. The other component is G \ S.

We start with S = G, i.e. all nodes are in one component and the other one is
empty. For each node in S, we count how many of its neighbours are in the other
component. Nodes with many "external" neighbours clearly do not belong in our
component, so we iteratively remove them from S. (They are implicitly added to
the other component G \ S.) We repeat this until the nodes in our component have
exactly 3 external neighbours, and we're done!

"""

from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day25')


def part1(data: str) -> int:
    graph = defaultdict(set)

    for line in data.splitlines():
        component, *peripherals = line.replace(':', '').split()
        for peripheral in peripherals:
            graph[component].add(peripheral)
            graph[peripheral].add(component)

    nodes = set(graph)

    count_fn = lambda component: len(graph[component]-nodes)

    while sum(map(count_fn, nodes)) != 3:
        nodes.remove(max(nodes, key=count_fn))

    return len(nodes) * len(set(graph)-nodes)



def part2(data: str) -> int:
    return 0


if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
