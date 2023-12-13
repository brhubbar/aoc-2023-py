"""Day N."""

from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day13')


def part1(data: str) -> int:
    total = 0
    for pattern in data.split("\n\n"):
        # Prepare to convert to binary numbers.
        pattern = pattern.replace('.', '0').replace('#', '1')
        rows = []
        cols = []
        for row in pattern.splitlines():
            rows.append(''.join(row))
            for idx, c in enumerate(row):
                try:
                    cols[idx] += c
                except IndexError:
                    cols.append(c)

        rows = [int(row, base=2) for row in rows]
        cols = [int(col, base=2) for col in cols]
        horz_refl = find_pattern_line(rows)
        vert_refl = find_pattern_line(cols)
        if horz_refl and vert_refl:
            print(f"Found a reflection in both directions for\n{pattern}")
        if not horz_refl and not vert_refl:
            print(f"Found neither for {pattern}!")
        total += vert_refl + 100*horz_refl
    return total


def part2(data: str) -> int:
    total = 0
    for pattern in data.split("\n\n"):
        # Prepare to convert to binary numbers.
        pattern = pattern.replace('.', '0').replace('#', '1')
        rows = []
        cols = []
        for row in pattern.splitlines():
            rows.append(''.join(row))
            for idx, c in enumerate(row):
                try:
                    cols[idx] += c
                except IndexError:
                    cols.append(c)

        rows = [int(row, base=2) for row in rows]
        cols = [int(col, base=2) for col in cols]
        horz_refl = find_smudge(rows)
        vert_refl = find_smudge(cols)
        if horz_refl and vert_refl:
            print(f"Found vert @ {vert_refl} and horz @ {horz_refl} for\n{pattern}")
        total += vert_refl + 100*horz_refl
    return total


def find_smudge(lines: list[int]) -> int:
    """Check for integers that are different by a single bit."""
    # First check for a smudge on the mirror line.
    # print(f"Comparing {lines}")
    for idx in range(len(lines)-1):
        if check_for_smudge(lines[idx], lines[idx+1]):
            # Not out of the woods yet - make the swap and ensure everything
            # else is a clean image.
            if check_for_reflection_after_idx_with_one_smudge(lines, idx):
                return idx+1
    # print(f"No smudges on the line of reflection.")
    # Okay, no dice. In that case, I can just find the mirror line, but require
    # a single smudge elsewhere.
    for idx in range(len(lines)-1):
        if lines[idx] == lines[idx+1] and check_for_reflection_after_idx_with_one_smudge(lines, idx):
            return idx+1
    # print(f"No smudges :/")

    return 0


def check_for_smudge(a: int, b: int) -> bool:
    """Return two if off by one position (bit)."""
    # Bitwise xor will yield a power of 2 IFF only different by one bit.
    # https://www.educative.io/answers/how-to-check-if-two-numbers-differ-at-one-bit-position-only
    xor = a ^ b
    return bin(xor).count("1") == 1



def find_pattern_line(lines: list[int]) -> int:
    """Return number of rows/cols before the line of reflection. 0 if none."""
    for idx in range(len(lines)-1):
        if lines[idx] == lines[idx+1] and check_for_reflection_after_idx(lines, idx):
            return idx+1
    return 0


def check_for_reflection_after_idx(list_: list[int], idx: int) -> bool:
    front = list_[:idx+1]
    back = list_[idx+1:]
    # Set the mirrored part up front.
    front.reverse()

    for f, b in zip(front, back):
        # Zip cuts off the excess for free.
        if f != b:
            return False
    return True


def check_for_reflection_after_idx_with_one_smudge(list_: list[int], idx: int) -> bool:
    front = list_[:idx+1]
    back = list_[idx+1:]
    # Set the mirrored part up front.
    front.reverse()

    n_smudges = 0
    for f, b in zip(front, back):
        # Zip cuts off the excess for free.
        if f == b:
            continue
        if check_for_smudge(f, b):
            # There's a smudge!
            n_smudges += 1
            continue
        # Don't match, not a smudge.
        return False
    # Okay - we made it to here, so nothing blatantly doesn't match. Now assert
    # that there's one and only one smudge.
    return n_smudges == 1




if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
