"""Day N."""

from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day15')


def part1(data: str) -> int:
    data = data.strip()
    total = 0
    for step in data.split(","):
        hash_ = 0
        for c in step:
            hash_ += ord(c)
            hash_ *= 17
            hash_ = hash_ % 256
        total += hash_
    return total



def part2(data: str) -> int:
    data = data.strip()

    hashmap = dict()
    for step in data.split(","):
        try:
            label, focal_length = step.split("=")
            focal_length = int(focal_length)
            is_add = True
        except ValueError:
            # Too few values to unpack.
            label = step.removesuffix("-")
            is_add = False

        hash_ = 0
        for c in label:
            hash_ += ord(c)
            hash_ *= 17
            hash_ = hash_ % 256

        box_id = hash_
        # Front [label, focal, label, focal, ...] Back
        box_contents = hashmap.get(box_id, [])

        if is_add:
            try:
                # Find where the lens is and update its focal length.
                label_idx = box_contents.index(label)
                # print(f"Replacing {label} with new FL {focal_length}")
                box_contents[label_idx+1] = focal_length
            except ValueError:
                # Label isn't present. Add to the back of the box.
                box_contents.extend([label, focal_length])
        else:
            # Remove that ish.
            try:
                label_idx = box_contents.index(label)
                # Remove the label.
                box_contents.pop(label_idx)
                # Remove the focal length.
                box_contents.pop(label_idx)
            except ValueError:
                # Not present, nothing to remove.
                pass

        # Lists are mutable so this is probably done already, but if we found an
        # unset key, I need to ensure that it gets set.
        hashmap[box_id] = box_contents
        # print(hashmap)

    total = 0
    for box_id, lenses in hashmap.items():
        for idx, focal_length in enumerate(lenses):
            if idx % 2 == 0:
                # Skip the even indexes, which hold the labels.
                continue
            total += (box_id+1) * ((idx+1)/2) * focal_length

    return total


if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
