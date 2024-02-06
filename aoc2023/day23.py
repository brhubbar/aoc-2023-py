"""Day 23."""

# I couldn't with part 2.
# https://gist.github.com/qwewqa/00d8272766c2945f4aa965ea36dba7f5

import itertools
from copy import deepcopy
from enum import IntEnum
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day23')


def part1(data: str) -> int:
    data = data.splitlines()
    edges = {}
    for r, row in enumerate(data):
        for c, v in enumerate(row):
            if v == ".":
                for dr, dc in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
                    ar, ac = r + dr, c + dc
                    if not (0 <= ar < len(data) and 0 <= ac < len(row)):
                        continue
                    if data[ar][ac] == ".":
                        edges.setdefault((r, c), set()).add((ar, ac))
                        edges.setdefault((ar, ac), set()).add((r, c))
            if v == ">":
                edges.setdefault((r, c), set()).add((r, c + 1))
                edges.setdefault((r, c - 1), set()).add((r, c))
            if v == "v":
                edges.setdefault((r, c), set()).add((r + 1, c))
                edges.setdefault((r - 1, c), set()).add((r, c))

    n, m = len(data), len(data[0])

    q = [(0, 1, 0)]
    visited = set()
    best = 0
    while q:
        r, c, d = q.pop()
        if d == -1:
            visited.remove((r, c))
            continue
        if (r, c) == (n - 1, m - 2):
            best = max(best, d)
            continue
        if (r, c) in visited:
            continue
        visited.add((r, c))
        q.append((r, c, -1))
        for ar, ac in edges[(r, c)]:
            q.append((ar, ac, d + 1))
    return best

def part2(data: str) -> int:
    data = data.splitlines()
    edges = {}  # (r, c) -> (ar, ac, length)
    for r, row in enumerate(data):
        for c, v in enumerate(row):
            if v in ".>v":
                for dr, dc in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
                    ar, ac = r + dr, c + dc
                    if not (0 <= ar < len(data) and 0 <= ac < len(row)):
                        continue
                    if data[ar][ac] in ".>v":
                        edges.setdefault((r, c), set()).add((ar, ac, 1))
                        edges.setdefault((ar, ac), set()).add((r, c, 1))

    # Remove nodes with degree 2 by merging the edges
    while True:
        for n, e in edges.items():
            if len(e) == 2:
                a, b = e
                edges[a[:2]].remove(n + (a[2],))
                edges[b[:2]].remove(n + (b[2],))
                edges[a[:2]].add((b[0], b[1], a[2] + b[2]))
                edges[b[:2]].add((a[0], a[1], a[2] + b[2]))
                del edges[n]
                break
        else:
            break

    n, m = len(data), len(data[0])

    q = [(0, 1, 0)]
    visited = set()
    best = 0
    while q:
        r, c, d = q.pop()
        if d == -1:
            visited.remove((r, c))
            continue
        if (r, c) == (n - 1, m - 2):
            best = max(best, d)
            continue
        if (r, c) in visited:
            continue
        visited.add((r, c))
        q.append((r, c, -1))
        for ar, ac, l in edges[(r, c)]:
            q.append((ar, ac, d + l))
    return best

# 3842 is too low

class Hiker:
    visited_pos: list[tuple[int]]
    n_steps: int
    # ((dx, dy), (x0, y0), (x-1, y-1))
    moved_from_fork: tuple[tuple[int]]
    # (x, y)
    starting_fork: tuple[int]

    id_counter = itertools.count()
    def __init__(self, x: int, y: int, n_steps: int) -> None:
        self.x = x
        self.y = y
        self.visited_pos = [self.position]
        self.n_steps = n_steps
        self.moved_from_fork = None
        self.id = next(Hiker.id_counter)

    def __repr__(self) -> str:
        return f"Hiker {self.id} at {self.position}, coming from {self.moved_from_fork} after {self.n_steps}"

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        result.id = next(Hiker.id_counter)
        return result

    @property
    def position(self) -> tuple[int]:
        return self.x, self.y

    def move(self, dx: int, dy: int) -> None:
        # Mark the current position as two-directional.
        self.x += dx
        self.y += dy
        self.visited_pos.append(self.position)
        self.n_steps += 1


class Forest:
    hikers: list[Hiker]
    former_hikers: list[Hiker]
    topography: dict[tuple[int], "TileType"]
    # ((dx, dy), (x0, y0), (x-1, y-1), (n_steps,))
    bad_moves: list[tuple[tuple[int]]]
    longest_path: int
    forks: list[tuple[int]]
    # (x, y): [(x_next, y_next, weight, distance_from_start)]
    dg: dict[tuple[int], list[tuple[int]]]

    def __init__(
        self,
        topography: dict[tuple[int], "TileType"],
        start: tuple[int],
        destination: tuple[int],
    ) -> None:
        self.topography = topography
        self.start = start
        self.destination = destination
        self.longest_path = 0
        self.hikers = []
        self.former_hikers = []
        self.bad_moves = []
        self.forks = dict()

    @classmethod
    def from_str(cls, string: str) -> "Forest":
        # Default to trees if a position is unknown.
        topography = dict()
        for y, row in enumerate(string.splitlines()):
            for x, c in enumerate(row):
                if c == "#":
                    topography[(x, y)] = TileType.TREE
                elif c == ".":
                    topography[(x, y)] = TileType.PATH
                elif c == "^":
                    topography[(x, y)] = TileType.UP
                elif c == "v":
                    topography[(x, y)] = TileType.DOWN
                elif c == "<":
                    topography[(x, y)] = TileType.LEFT
                elif c == ">":
                    topography[(x, y)] = TileType.RIGHT
                elif c == "S":
                    topography[(x, y)] = TileType.PATH
                    start = (x, y)
                elif c == "D":
                    topography[(x, y)] = TileType.PATH
                    destination = (x, y)
                else:
                    raise ValueError(f"Unexpected tile type {c}.")
        return cls(topography, start, destination)

    def compute_weighted_dg(self) -> None:
        other_hikers = self.hikers.copy()
        self.hikers = []
        forks = [self.start, self.destination]
        for tile, type_ in self.topography.items():
            if type_ < 0:
                continue

            # Drop a hiker here.
            hiker = Hiker(*tile, n_steps=0)

            if len(self.get_valid_steps_to_take(hiker)) < 3:
                # Just a point on a path (or a funnel), not a fork.
                continue

            # This hiker is on a fork and we want to see where he goes!
            hiker.starting_fork = tile
            forks.append(tile)
            self.hikers.append(hiker)
        self.forks = forks
        self.dg = {fork: [] for fork in forks}
        while not self.move_hikers_one_step_until_fork():
            pass

        self.hikers = other_hikers

    def move_hikers_one_step_until_fork(self) -> bool:
        """Returns true if all hikers are done."""
        if not self.hikers:
            return True
        done_hikers = []
        new_hikers = []
        for hiker in self.hikers:
            if hiker.position in self.forks and hiker.n_steps > 0:
                # Hiker has arrived.
                done_hikers.append(hiker)
                self.dg[hiker.starting_fork].append((*hiker.position, hiker.n_steps, float('inf')))
                continue

            valid_steps = self.get_valid_steps_to_take(hiker)

            hikers = [hiker]
            if len(valid_steps) > 1:
                # Need to multiply the hikers.
                for _ in range(len(valid_steps)-1):
                    new_hiker = deepcopy(hiker)
                    hikers.append(new_hiker)
                    new_hikers.append(new_hiker)

            for movement, hiker in zip(valid_steps, hikers):
                hiker.move(*movement)

        for hiker in done_hikers:
            self.hikers.remove(hiker)
            self.former_hikers.append(hiker)

        return False

    def move_hikers_one_step(self) -> bool:
        """Returns true if all hikers are done."""
        if not self.hikers:
            return True
        done_hikers = []
        invalid_hikers = []
        new_hikers = []
        n_bad_moves_pruned = 0
        unique_bad_moves_pruned = set()
        n_dead_ends_skipped = 0
        for hiker in self.hikers:
            if hiker.position == self.destination:
                # Hiker has arrived.
                done_hikers.append(hiker)
                self.longest_path = max(self.longest_path, hiker.n_steps)
                continue

            if hiker.moved_from_fork in self.bad_moves:
                # We've learned that this fork leads to nowhere.
                invalid_hikers.append(hiker)
                n_bad_moves_pruned += 1
                unique_bad_moves_pruned.add(hiker.moved_from_fork)
                continue

            valid_steps = self.get_valid_steps_to_take(hiker)
            # print(f"{valid_steps=}")
            if len(valid_steps) == 0:
                # This hiker shouldn't exist.
                invalid_hikers.append(hiker)
                # It must have come from a fork (otherwise we would never arrive
                # at the destination). Keep track of that to save computation
                # time later.
                self.bad_moves.append(hiker.moved_from_fork)
                # print(f"{hiker.moved_from_fork} is a bad move!")
                n_dead_ends_skipped += 1
                continue

            hikers = [hiker]
            if len(valid_steps) > 1:
                # Need to multiply the hikers.
                for _ in range(len(valid_steps)-1):
                    new_hiker = deepcopy(hiker)
                    hikers.append(new_hiker)
                    new_hikers.append(new_hiker)

            for movement, hiker in zip(valid_steps, hikers):
                if len(hikers) > 1:
                    # Moving from a fork - keep track of that so we know which
                    # forks are dead ends.
                    self.forks[hiker.moved_from_fork] = (

                    )

                    hiker.moved_from_fork = (
                        movement,
                        hiker.position,
                        hiker.visited_pos[-2],
                        hiker.n_steps
                    )
                hiker.move(*movement)

        # if n_bad_moves_pruned or n_dead_ends_skipped:
        #     print(f"About to kick from a pool of {len(self.hikers)} hikers.")
        for hiker in invalid_hikers:
            self.hikers.remove(hiker)
        for hiker in done_hikers:
            self.hikers.remove(hiker)
            self.former_hikers.append(hiker)
        self.hikers.extend(new_hikers)

        # if n_bad_moves_pruned:
        #     print(f"Kicked {n_bad_moves_pruned} dorks on {len(unique_bad_moves_pruned)} bad forks!")
        # if n_dead_ends_skipped:
        #     print(f"Kicked {n_dead_ends_skipped} hikers at dead ends!")
        # for hiker in invalid_hikers:
        #     print(hiker)
        # if n_bad_moves_pruned or n_dead_ends_skipped:
        #     print(f"Leaving {len(self.hikers)} hikers")
        return False

    def get_valid_steps_to_take(self, hiker: Hiker) -> list[tuple[int]]:
        """Returns a list of (dx, dy) pairs."""
        current_tile = self.topography[hiker.position]
        # Gather all possible moves by tile type, then remove any which have
        # been done before. This will catch attempts to walk uphill.
        possible_moves = []

        if current_tile < 0:
            raise RuntimeError("This hiker is in the woods!")
        elif current_tile > 0:
            # It's a slope.
            possible_moves.append(current_tile.as_tuple())
        else:
            # On the path, can go anywhere.
            for direction in [TileType.UP, TileType.DOWN, TileType.LEFT, TileType.RIGHT]:
                possible_moves.append(direction.as_tuple())

        # Now, validate the possible moves.
        current_x, current_y = hiker.position
        valid_moves = []
        n_bad_moves_skipped = 0
        for dx, dy in possible_moves:
            if ((dx, dy), hiker.position) in self.bad_moves:
                # We know this is a poor choice, don't go that way. Doing this
                # allows for us to learn that downstream forks only lead to dead
                # ends, thus pruning further back.
                n_bad_moves_skipped += 1
                continue
            neighbor_pos = (current_x+dx, current_y+dy)
            if neighbor_pos in hiker.visited_pos:
                # Already been here, no dice.
                continue
            neighbor = self.topography.get(neighbor_pos, TileType.TREE)
            # print(f"--> {neighbor}")
            if neighbor < 0:
                # Not a valid spot to visit.
                continue

            valid_moves.append((dx, dy))
        # if n_bad_moves_skipped:
        #     print(f"Skipped {n_bad_moves_skipped} bad moves!")
        return valid_moves


class TileType(IntEnum):
    TREE = -1
    PATH = 0
    # nxy where n is the sign bit and x/y are dx, dy and mutually exclusive.
    UP = 0b101
    DOWN = 0b001
    LEFT = 0b110
    RIGHT = 0b010

    def as_tuple(self) -> tuple[int]:
        if self <= 0:
            # No forced move.
            return 0, 0
        is_neg = (self & 0b100) >> 2
        sign = -1 * is_neg or 1
        x = (self & 0b010) >> 1
        y = self & 0b001
        # print(f"{x=}, {y=}, {sign=}")
        # print(f"Converted {self} to ({sign*x}, {sign*y})")
        return sign*x, sign*y



if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
