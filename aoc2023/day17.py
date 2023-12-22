"""Day N."""

import heapq
from enum import IntEnum
import itertools
from functools import partial
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day17')


# +1 = turn right. %4 wraps.
directions = {
    0: (-1, 0),  # Left
    1: (0, 1),  # Up
    2: (1, 0),  # Right
    3: (0, -1),  # Down.
}

# Build a 4-d graph of x, y, direction, steps_in_direction.
def part1(data: str) -> int:
    # This is a mapping of all possible locations in 4-d space to the object
    # tracking the state of that location. The object is probably overkill, but
    # this is Python so who cares.
    graph = dict()
    width = data.find('\n')
    height = data.count('\n')
    for y, row in enumerate(data.splitlines()):
        for x, char in enumerate(row):
            for dir_ in range(4):
                # Can't arrive at a node going in a direction with 0 previous
                # steps in that direction, so start from 1.
                for n in range(1, 4):
                    graph[(x, y, dir_, n)] = Node(x, y, dir_, n, int(char))
    # Add the starting point. This has zero steps taken so far.
    start_key = (0, 0, 2, 0)
    start = Node(*start_key, 0)
    start.distance_from_start = 0
    graph[start_key] = start

    # Djikstra's with a priority queue can be implemented by adding 'tasks'
    # (nodes to evaluate) to the queue only after they have been given a
    # non-initial weight. This keeps the queue small which should help
    # accelerate the sorting algorithm.
    # https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm#Using_a_priority_queue.
    # Using a priority queue is orders of magnitude faster than iterating
    # through the whole list of nodes, looking for the next optimal node to
    # visit. This is because that min-finding is done optimally by a heap sort,
    # rather than brute force.
    priority_queue = PriorityQueue()
    priority_queue.add_task(start_key, 0)

    print(f"Evaluating {len(graph)} nodes.")

    return djikstra(
        end=(width-1, height-1),
        graph=graph,
        priority_queue=priority_queue,
    )


def part2(data: str) -> int:
    # This is a mapping of all possible locations in 4-d space to the object
    # tracking the state of that location. The object is probably overkill, but
    # this is Python so who cares.
    graph = dict()
    width = data.find('\n')
    height = data.count('\n')

    # Preload with the minimum/maximum allowed steps.
    UltraNode = partial(Node, min_consecutive=4, max_consecutive=10)

    for y, row in enumerate(data.splitlines()):
        for x, char in enumerate(row):
            for dir_ in range(4):
                # Can't arrive at a node going in a direction with 0 previous
                # steps in that direction, so start from 1.
                for n in range(1, 11):
                    graph[(x, y, dir_, n)] = UltraNode(x, y, dir_, n, int(char))
    # Add the starting point. This has zero steps taken so far.
    start_key = (0, 0, 2, 0)
    start = UltraNode(*start_key, 0)
    start.distance_from_start = 0
    graph[start_key] = start

    # Djikstra's with a priority queue can be implemented by adding 'tasks'
    # (nodes to evaluate) to the queue only after they have been given a
    # non-initial weight. This keeps the queue small which should help
    # accelerate the sorting algorithm.
    # https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm#Using_a_priority_queue.
    # Using a priority queue is orders of magnitude faster than iterating
    # through the whole list of nodes, looking for the next optimal node to
    # visit. This is because that min-finding is done optimally by a heap sort,
    # rather than brute force.
    priority_queue = PriorityQueue()
    priority_queue.add_task(start_key, 0)

    print(f"Evaluating {len(graph)} nodes.")

    return djikstra(
        end=(width-1, height-1),
        graph=graph,
        priority_queue=priority_queue,
    )


def djikstra(
    end: tuple[int],
    graph: dict[tuple[int], "Node"],
    priority_queue: "PriorityQueue",
) -> int:
    # Just counter so I can visualize how quickly I'm moving through things.
    counter = 0
    while True:
        try:
            current_node = graph[priority_queue.pop_task()]
        except KeyError:
            # Empty queue or invalid node address.
            break

        counter += 1
        if counter % 1000 == 0:
            print(f"Evaluating {counter}th node.")

        # print(f"Evaluating {current_node}")
        # Mark the node as visited so it can be skipped in future evaluations of
        # this node as a neigbor.
        current_node.is_visited = True
        if (
            current_node.position == end
            and current_node.n_consecutive >= current_node.min_consecutive
        ):
            # We've found the minimum distance to this node aloong an allowed
            # path. Direction/n_steps are irrelevant because djikstra evaluates
            # the optimal path first.
            return current_node.distance_from_start

        for neighbor_coords in current_node.neighbor_tuples:
            neighbor_node = graph.get(neighbor_coords, None)
            if neighbor_node is None:
                # Off the map!
                continue

            if neighbor_node.is_visited:
                # Optimal path to this node has already been found!
                continue

            new_distance = current_node.distance_from_start + neighbor_node.weight
            if new_distance < neighbor_node.distance_from_start:
                # Visiting this neighbor from the current node is less expensive
                # than what it had previously been evaluated with.
                neighbor_node.distance_from_start = new_distance
                # Now that we've set a non-initial value for this neighbor node,
                # add it to the priority queue. add_task has a built-in
                # capability to override a previous entry of neighbor_coords, in
                # the case that this node just got re-evaluated with a better
                # cost.
                priority_queue.add_task(neighbor_coords, new_distance)

    return graph[end].distance_from_start


class Node:
    x: int
    y: int
    direction: int
    n_consecutive: int
    min_consecutive: int
    max_consecutive: int
    weight: int
    distance_from_start: int
    is_visited: bool

    def __init__(
        self,
        x: int,
        y: int,
        direction: int,
        consecutive: int,
        weight: int,
        min_consecutive: int = 0,
        max_consecutive: int = 3,
    ) -> None:
        self.x = x
        self.y = y
        self.direction = direction
        self.n_consecutive = consecutive
        self.min_consecutive = min_consecutive
        self.max_consecutive = max_consecutive
        self.weight = weight

        self.distance_from_start = float('inf')
        self.is_visited = False

    def __repr__(self) -> str:
        return f"{self.node} w{self.weight}, d{self.distance_from_start}"

    @property
    def position(self) -> tuple[int]:
        return self.x, self.y

    @property
    def node(self) -> tuple[int]:
        return self.x, self.y, self.direction, self.n_consecutive

    @property
    def neighbor_tuples(self) -> list[tuple[int]]:
        # Don't move backward, don't move too far.
        moves_to_neighbors = []
        if self.n_consecutive >= self.min_consecutive:
            moves_to_neighbors.extend([
                # Turn right
                ((self.direction + 1) % 4, 1),
                # Turn left
                ((self.direction - 1) % 4, 1),
            ])
        if self.n_consecutive < self.max_consecutive:
            # Go straight
            moves_to_neighbors.append((self.direction, self.n_consecutive + 1))

        neighbors = []
        for direction, n in moves_to_neighbors:
            x, y = directions[direction]
            neighbors.append((self.x+x, self.y+y, direction, n))
        return neighbors


class PriorityQueue:
    # Effectively copied from
    # https://docs.python.org/3/library/heapq.html#priority-queue-implementation-notes
    REMOVED = '<removed-task>'

    def __init__(self) -> None:
        self.pq = []
        self.entry_finder = {}
        self.counter = itertools.count()

    def add_task(self, task, priority=0) -> None:
        'Add a new task or update the priority of an existing task'
        if task in self.entry_finder:
            self.remove_task(task)
        count = next(self.counter)
        entry = [priority, count, task]
        self.entry_finder[task] = entry
        heapq.heappush(self.pq, entry)

    def remove_task(self, task) -> None:
        'Mark an existing task as REMOVED.  Raise KeyError if not found.'
        entry = self.entry_finder.pop(task)
        entry[-1] = self.REMOVED

    def pop_task(self):
        'Remove and return the lowest priority task. Raise KeyError if empty.'
        while self.pq:
            _, _, task = heapq.heappop(self.pq)
            if task is not self.REMOVED:
                del self.entry_finder[task]
                return task
        raise ValueError('pop from an empty priority queue')


if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
