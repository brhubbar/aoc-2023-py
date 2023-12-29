"""Day N."""

import itertools
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day22')


def part1(data: str) -> int:
    Brick.id_counter = itertools.count()
    bricks = [Brick.from_str(brick) for brick in data.splitlines()]
    bricks.sort(key=lambda x: x.min_z)

    dim_x, dim_y, dim_z = get_tower_dimensions(bricks)
    tower = Tower(dim_x, dim_y, dim_z)

    settle_bricks(bricks, tower)

    return len(find_removable_bricks(bricks, tower))


def part2(data: str) -> int:
    Brick.id_counter = itertools.count()
    bricks = [Brick.from_str(brick) for brick in data.splitlines()]
    bricks.sort(key=lambda x: x.min_z)

    dim_x, dim_y, dim_z = get_tower_dimensions(bricks)
    tower = Tower(dim_x, dim_y, dim_z)

    settle_bricks(bricks, tower)

    # Now sort by id.
    bricks.sort(key=lambda x: x.id)

    supporting_bricks = []
    for brick in bricks:
        supporting_bricks.append(tower.get_supporting_bricks(brick))

    def process_removal(supporting_bricks: list[set], brick_id: int) -> None:
        """
        Recursively remove brick from all other bricks' list of supporters.

        Returns the number of bricks caused to fall.

        Assumes that a brick's location in supporting_bricks = its id. (hence
        the sort above))
        """
        # print(f"Removing {brick_id}")
        fallen_bricks = 0
        for idx in range(len(supporting_bricks)):
            brick_set = supporting_bricks[idx]
            if brick_id in brick_set:
                brick_set.remove(brick_id)
                if not brick_set:
                    fallen_bricks += 1
                    fallen_bricks += process_removal(supporting_bricks, idx)
        return fallen_bricks

    total = 0
    for brick in bricks:
        sb = deepcopy(supporting_bricks)
        n_removed = process_removal(sb, brick.id)
        # print(f"{n_removed} fell when removing {brick}")
        total += n_removed

    return total
# 945 is too low
# 19013 is too low

def find_removable_bricks(bricks: list["Brick"], tower: "Tower") -> set[int]:
    """
    Return a list of brick ids which could be safely removed from the tower.

    "Safely" means that there is at least one other brick supporting the bricks
    which it supports.

    To determine this, we find the bricks supporting each brick. If there are
    multiple, we do nothing (these are optional bricks). If there is only one,
    we add it to the set of 'required' bricks. The return value is the set of
    all bricks absent from the 'required' set.

    """
    optional_bricks = set(range(Brick.max_id+1))
    required_bricks = set()

    for brick in bricks:
        supporting_bricks = tower.get_supporting_bricks(brick)
        if len(supporting_bricks) == 1:
            required_bricks.update(supporting_bricks)

    return optional_bricks.difference(required_bricks)


def settle_bricks(bricks: list["Brick"], tower: "Tower") -> None:
    """Modifies the brick positions and updates that position in the tower."""
    for brick_idx in range(len(bricks)):
        brick = bricks[brick_idx]
        # print(f"Brick fell from {brick}", end=" ")
        brick.fall(tower)
        # print(f"to {brick}")


def get_tower_dimensions(bricks: list["Brick"]) -> tuple[int]:
    """Compute the width, length, and height of the brick fall space."""
    # X and Y have minimum values of 0. Z minimum value is 1, so the bottom
    # layer is set to True (occupied.)
    dim_x = 0
    dim_y = 0
    dim_z = 0
    for brick in bricks:
        # Add 1 because we index from 0.
        dim_x = max(brick.max_x+1, dim_x)
        dim_y = max(brick.max_y+1, dim_y)
        dim_z = max(brick.max_z+1, dim_z)
    return dim_x, dim_y, dim_z


class Tower(defaultdict):
    """
    Keeps track of the stack of bricks.

    tower[z] = {
        'x_axis': [
            [x=0, x=1, x=2, ...],  # y = 0
            [x=0, x=1, x=2, ...],  # y = 1
        ],
        'y_axis': [
            [y=0, y=1, y=2, ...],  # x = 0
            [y=0, y=1, y=2, ...],  # x = 1
        ],
    }

    For a given z plane, stores vectors parallel to the x axis and to the y
    axis indicating if the space is occupied. The value in the space indicates
    what brick is occupying that space. -1 is the ground, None is unoccupied.

    """

    dim_x: int
    dim_y: int
    dim_z: int

    def __init__(self, dim_x, dim_y, dim_z) -> None:
        super().__init__(self.create_empty_layer)
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.dim_z = dim_z
        self[0] = {
            'x_axis': [[-1]*dim_y]*dim_x,
            'y_axis': [[-1]*dim_x]*dim_y,
        }

    def create_empty_layer(self) -> dict[str, list[list[bool]]]:
        return {
            # Each vector is y long. x many vectors. Use a generator to create
            # unique lists.
            'x_axis': [[None]*self.dim_y for _ in range(self.dim_x)],
            'y_axis': [[None]*self.dim_x for _ in range(self.dim_y)],
        }

    @staticmethod
    def get_brick_vector_args(brick: "Brick") -> dict:
        """
        Return the arguments used to define a brick in the Tower space.

        Returns
        -------
        z_plane : int
            The minimum z value of the brick. Used to fetch the z plane.
        axis : ['x_axis', 'y_axis']
            The axis that the brick runs parallel to.
        vector_idx : int
            The value of the xy coordinate perpendicular to the axis of
            orientation.
        min_pos : int
            The value of the minimum xy coordinate parallel to the axis of
            orientation.
        max_pos : int
            The value of the maximum xy coordinate parallel to the axis of
            orientation.

        """
        if brick.orientation == 1:
            # Oriented along x. Look down from current z position for the
            # nearest z plane with the occupied vector at all blocked.
            return {
                'axis': 'x_axis',
                'z_plane': brick.min_z,
                'vector_idx': brick.min_y,
                'min_pos': brick.min_x,
                'max_pos': brick.max_x,
            }
        elif brick.orientation in (0, 2, 3):
            # Oriented in y or z. z is treated like y with a width of 1.
            return {
                'axis': 'y_axis',
                'z_plane': brick.min_z,
                'vector_idx': brick.min_x,
                'min_pos': brick.min_y,
                'max_pos': brick.max_y,
            }
        raise RuntimeError("Invalid Orientation!")

    def get_supporting_bricks(self, brick) -> set[int]:
        bva = self.get_brick_vector_args(brick)
        z_plane = bva['z_plane'] - 1
        if z_plane == 0:
            # On the ground - nothing to see here!
            return set()
        check_plane = self[z_plane][bva['axis']][bva['vector_idx']]
        check_vector = check_plane[bva['min_pos']:bva['max_pos']+1]
        supporting_bricks = set([brick_id for brick_id in check_vector if brick_id is not None])
        # print(f"{supporting_bricks=} found in {check_vector=}")
        if not supporting_bricks:
            raise RuntimeError("The brick hasn't fallen!?")
        return supporting_bricks

    def add_brick(self, brick: "Brick") -> None:
        """Mark the space occupied by the brick in the z planes."""
        for z in range(brick.min_z, brick.max_z+1):
            for y in range(brick.min_y, brick.max_y+1):
                for x in range(brick.min_x, brick.max_x+1):
                    self.set_position(brick.id, x, y, z)

    def remove_brick(self, brick: "Brick") -> None:
        """Mark the space no longer occupied by the brick in the z planes."""
        for z in range(brick.min_z, brick.max_z+1):
            for y in range(brick.min_y, brick.max_y+1):
                for x in range(brick.min_x, brick.max_x+1):
                    self.set_position(None, x, y, z)

    def set_position(self, val, x, y, z) -> None:
        """
        Set the value for a given position.

        Modifies both slices of the tower.

        """
        # print(f"Setting {x}, {y}, {z} to {val}")
        self[z]['x_axis'][y][x] = val
        self[z]['y_axis'][x][y] = val
        # print(self[z])


class Brick:
    """Defines the behaviors of a brick."""
    id_counter = itertools.count()
    def __init__(self) -> None:
        self._ends = tuple([[0, 0, 0], [0, 0, 0]])
        self.id = next(Brick.id_counter)

    def __repr__(self) -> str:
        return f"{self.id}: {self.ends}"

    @classmethod
    def from_str(cls, string: str) -> "Brick":
        """Create a brick from its defining string."""
        ends = string.split("~")
        ends = [
            [int(x) for x in end.split(",")]
            for end in ends
        ]
        if len(ends) != 2:
            raise ValueError("Expected two ends of the brick!")
        # Only one dimension changes, so this will align the ends to point in
        # the positive direction of x, y, or z.
        ends.sort()

        b = Brick()
        b.ends = ends
        return b

    @classmethod
    @property
    def max_id(cls) -> int:
        """Return the highest id of a brick out there."""
        # Peek a la stack overflow. https://stackoverflow.com/a/2425347
        next_id = next(cls.id_counter)
        cls.id_counter = itertools.chain([next_id], cls.id_counter)
        return next_id - 1

    def fall(self, tower: Tower) -> None:
        """Move the brick as far down in the z dimension as possible."""
        def get_min_z_not_occupied(axis, z_plane, vector_idx, min_pos, max_pos) -> bool:
            check_z = z_plane - 1
            while check_z > 0:
                check_plane = tower[check_z][axis][vector_idx]
                check_vector = check_plane[min_pos:max_pos+1]
                # print(f"Checking {check_plane=}, {check_vector=}")
                if any([p is not None for p in check_vector]):
                    # This one is occupied.
                    return check_z + 1
                check_z -= 1
            # None found, fall all the way.
            return 1

        fall_to_z = get_min_z_not_occupied(**tower.get_brick_vector_args(self))

        # Move the brick.
        tower.remove_brick(self)
        delta_z = self.min_z - fall_to_z
        self.ends = (
            (self.min_x, self.min_y, self.min_z-delta_z),
            (self.max_x, self.max_y, self.max_z-delta_z),
        )
        tower.add_brick(self)

    @property
    def ends(self) -> tuple[tuple[int]]:
        """Two ends of the brick, oriented along the + orientation axis."""
        return self._ends

    @ends.setter
    def ends(self, ends: tuple[tuple[int]]) -> None:
        """Sorts the list before saving."""
        ends_list = list(ends)
        ends_list.sort()
        self._ends = tuple(ends_list)

    @property
    def orientation(self) -> str:
        """
        Indicate the standard vector (x=1, y=2, or z=3) that the brick lies on.

        Returns 0 if a cube.

        """
        for axis in range(3):
            if self.ends[0][axis] == self.ends[1][axis]:
                continue
            # These values are different.
            return axis + 1
        # It's a cube.
        return 0


    @property
    def min_x(self) -> int:
        """The minimum x value of the brick."""
        return self.ends[0][0]

    @property
    def max_x(self) -> int:
        """The maximum x value of the brick. Used for finding x_dim."""
        return self.ends[1][0]

    @property
    def min_y(self) -> int:
        """The minimum y value of the brick."""
        return self.ends[0][1]

    @property
    def max_y(self) -> int:
        """The maximum y value of the brick. Used for finding y_dim."""
        return self.ends[1][1]

    @property
    def min_z(self) -> int:
        """The minimum z value of the brick. Used to sort before falling."""
        return self.ends[0][2]

    @property
    def max_z(self) -> int:
        """The maximum z value of the brick. Used for finding z_dim."""
        return self.ends[1][2]

if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
