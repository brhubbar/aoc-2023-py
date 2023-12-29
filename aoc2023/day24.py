"""Day 24."""

from itertools import combinations
from pathlib import Path


import numpy as np
import z3
from scipy import linalg

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day24')


def part1(data: str) -> int:
    stones = []
    p_min = 200000000000000
    p_max = 400000000000000
    # p_min = 7
    # p_max = 27
    for hailstone_s in data.splitlines():
        stones.append(Hailstone.from_str(hailstone_s))

    total = 0
    for a, b in combinations(stones, 2):
        # print(f"\nHailstone A: {a}")
        # print(f"Hailstone B: {b}")
        try:
            ta, tb, x, y = a.intersection_xy(b)
        except NeverCross:
            continue
        if (
            ta > 0
            and tb > 0
            and p_min <= x <= p_max
            and p_min <= y <= p_max
        ):
            total += 1
        # except NeverCross:
        #     print("Hailstones' paths are parallel; they never intersect.")
        #     continue
        # if ta < 0:
        #     if tb < 0:
        #         print("Hailstones' paths crossed in the past for both hailstones.")
        #     else:
        #         print("Hailstones' paths crossed in the past for hailstone A.")
        # elif tb < 0:
        #     print("Hailstones' paths crossed in the past for hailstone B.")
        # elif p_min <= x <= p_max and p_min <= y <= p_max:
        #     print(f"Hailstones' paths will cross inside the test area (at {x=:.3f}, {y=:.3f}).")
        #     total += 1
        # else:
        #     print(f"Hailstones' paths will cross outside the test area (at {x=:.3f}, {y=:.3f}).")

    return total

# 18652 is too high

def part2(data: str) -> int:
    stones = []
    for hailstone_s in data.splitlines():
        stones.append(Hailstone.from_str(hailstone_s))

    x, y, z, dx, dy, dz = find_traj_hits_these_three(*stones[:3])
    return x + y + z

# 373286912225103 is too low!


def find_traj_hits_these_three(*hailstones: "Hailstone") -> float:
    """
    Return the start point + velocity of a rock which would intersect *on time*
    with three hailstones. I'm assuming that they all collide with one and only
    one trajectory.

    Returns
    -------
    x
    y
    z
    dx
    dy
    dz

    """
    # This can be solved linearly through a few assumptions and some slick math
    # tricks as described here:
    # https://www.reddit.com/r/adventofcode/comments/18pnycy/comment/kepu26z/
    #
    # You can also solve it by brute force by setting all positions and
    # velocities relative to that of the rock, then searching for a rock
    # velocity that causes all hailstones to collide with the rock (the origin).
    # Source:
    # https://www.reddit.com/r/adventofcode/comments/18pptor/comment/keps780/
    #
    # That said, most people used 'Z3' as a symbolic solver, and I haven't done
    # symbolic solving since I left matlab, so I want to try that out.
    #
    # Code copied from
    # https://www.reddit.com/r/adventofcode/comments/18pnycy/comment/kev3buh/
    #
    # Solving for pr_0 (3-vector), dpr (3-vector) and t (3-vector). Using more
    # than three hailstones would be over-constrained.

    t1, t2, t3, xr, yr, zr, dxr, dyr, dzr = z3.Reals("t1 t2 t3 xr yr zr dxr dyr dzr")
    h1, h2, h3 = hailstones[:3]
    constraints = [
        xr + dxr*t1 == h1.px + h1.dpx*t1,
        yr + dyr*t1 == h1.py + h1.dpy*t1,
        zr + dzr*t1 == h1.pz + h1.dpz*t1,
        xr + dxr*t2 == h2.px + h2.dpx*t2,
        yr + dyr*t2 == h2.py + h2.dpy*t2,
        zr + dzr*t2 == h2.pz + h2.dpz*t2,
        xr + dxr*t3 == h3.px + h3.dpx*t3,
        yr + dyr*t3 == h3.py + h3.dpy*t3,
        zr + dzr*t3 == h3.pz + h3.dpz*t3,
    ]
    # Set up the solver, assert that my constraints are valid, and then run it.
    solver = z3.Solver()
    solver.add(*constraints)
    solver.check()
    model = solver.model()
    # I only actually need the position, but I'm going to return the whole trajectory.
    return tuple([model[var].as_long() for var in [xr, yr, zr, dxr, dyr, dzr]])


class Hailstone:
    def __init__(
        self,
        p: tuple[int],
        dp: tuple[int],
    ) -> None:
        self.p = p
        self.dp = dp

    def __repr__(self) -> str:
        return f"{self.p} @ {self.dp}"

    @classmethod
    def from_str(cls, string) -> "Hailstone":
        p, dp = string.split(" @ ")
        p = [int(x) for x in p.split(', ')]
        dp = [int(dx) for dx in dp.split(', ')]
        return cls(p, dp)

    def intersection_xy(self, other: "Hailstone") -> float:
        """
        Return the time and location that the two trajectories cross.

        Returns
        -------
        t_self
        t_other
        x
        y

        """
        # This is vector math. pt = p0 + dp*t
        #
        # Set p1_t1 = p2_t2, so
        #
        # p1_0 = 2-vector
        # p2_0 = 2-vector
        # dp1 = 2-vector
        # dp2 = 2-vector
        # DP = 2x2 matrix [dp1, -dp2]
        # t = 2-vector [t1, t2]
        #
        # p1_0 + dp1*t1 = p2_0 + dp2*t2
        #
        # p2_0 - p1_0 = DP*t
        #
        # ... b = A*x
        #
        # Solve for t1, t2. Use them to compute the location of the intersection
        # and determine if it happens in the future for both.
        p1_0 = np.array(self.p[:2])
        p2_0 = np.array(other.p[:2])
        dp1 = np.array(self.dp[:2])
        dp2 = np.array(other.dp[:2])

        b = p2_0 - p1_0
        # column_stack makes dp1 the first column, -dp2 the second.
        A = np.column_stack((dp1, -dp2))

        try:
            t = linalg.solve(A, b)
        except linalg.LinAlgError:
            # Trajectories are parallel!
            raise NeverCross

        p1_t1 = p1_0 + (dp1 * t[0])
        p2_t2 = p2_0 + (dp2 * t[1])

        if not np.allclose(p1_t1, p2_t2):
            raise RuntimeError("Ben sucks at math!")

        return t[0], t[1], p1_t1[0], p1_t1[1]

    @property
    def px(self) -> float:
        return self.p[0]

    @property
    def py(self) -> float:
        return self.p[1]

    @property
    def pz(self) -> float:
        return self.p[2]

    @property
    def dpx(self) -> float:
        return self.dp[0]

    @property
    def dpy(self) -> float:
        return self.dp[1]

    @property
    def dpz(self) -> float:
        return self.dp[2]


class NeverCross(Exception):
    pass

if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
