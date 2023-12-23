"""Day N."""

import re
from collections import namedtuple
from functools import partial
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day19')

PART_ATTRS = re.compile(r"\d+")
MIN_VALUE = 1
MAX_VALUE = 4000

Step = namedtuple("Step", ["attr", "min", "max", "goto", "description"])

def part1(data: str) -> int:
    workflows_s, parts_s = data.split("\n\n")

    # For each step, store the attribute to check and the bounds it should fall
    # into, then the workflow to send it to if that passes.
    #
    # e.g.
    #
    #    qqz{ s>2770:qa,m<1801:hdj,R}
    #
    # Becomes
    # 'qqz' = [
    #     ('s', 2771, 4000, 'qa')
    #     ('m', 0, 1800, 'hdj')
    #     (None, None, None, 'R')
    # ]
    # If the attribute to check is None, then it'll pass.
    #
    # Bounds are *inclusive*.
    workflows = dict()
    for workflow in workflows_s.splitlines():
        name, steps_s = workflow.split("{")
        # print(f"Parsing workflow {name}")
        steps = []
        for step in steps_s.split(","):
            if step.endswith("}"):
                # Final step, this is a default.
                steps.append(Step(None, None, None, step[:-1], f"else --> {step[:-1]}"))
                break
            attr = step[0]
            comparator = step[1]
            compare_to, goto = step[2:].split(":")
            create_step = partial(
                Step,
                description=f"{attr} {comparator} {compare_to} --> {goto}",
            )
            if comparator == "<":
                step = create_step(attr, MIN_VALUE, int(compare_to)-1, goto)
            elif comparator == ">":
                step = create_step(attr, int(compare_to)+1, MAX_VALUE, goto)
            else:
                raise RuntimeError("AHHHH")

            steps.append(step)
        workflows[name] = steps
    # print(workflows)

    accepted = []
    rejected = []
    for part_s in parts_s.splitlines():
        # print(part_s)
        x, m, a, s = PART_ATTRS.findall(part_s)
        part = {
            'x': int(x),
            'm': int(m),
            'a': int(a),
            's': int(s),
        }
        workflow = workflows['in']
        # print("Running in")
        while True:
            goto = run_workflow_on_part(workflow, part)
            if goto == "A":
                accepted.append(part)
                break
            if goto == "R":
                rejected.append(part)
                break
            workflow = workflows[goto]
            # print(f"\nRunning {goto}")

    # print(accepted)
    # print(rejected)

    return sum([sum([value for value in part.values()]) for part in accepted])


def part2(data: str) -> int:
    # For each workflow, store a list of steps.
    #
    # Each step defines the bounds which x,m,a,s must fall into. A default step
    # has the bounds (0, 4000), (0, 4000), (0, 4000), (0, 4000).
    #
    # For each step, create two new Bounds: one which falls into the set
    # defined, and one which falls outside of the set defined.
    #
    # e.g.
    #
    #    qqz{ s>2770:qa,m<1801:hdj,R}
    #
    # Becomes
    # 'qqz' = [
    #     ('s', 2771, 4000, 'qa')
    #     ('m', 0, 1800, 'hdj')
    #     (None, None, None, 'R')
    # ]
    #
    # Then, to process, if Bounds entering qqz is
    #
    #     (0, 4000), (0, 4000), (0, 4000), (1351, 4000)
    #
    # Bounds will split into
    #
    #     (0, 4000), (0, 4000), (0, 4000), (2771, 4000) -> 'qa'  (First passes)
    #     (0, 4000), (0, 1800), (0, 4000), (1351, 2770) -> 'hdj'  (Second passes)
    #     (0, 4000), (1801, 4000), (0, 4000), (1351, 4000) -> 'R'  (Default)
    #
    # For first pass: checking 's'. To pass, take max of s[0], and min of s[1]
    #   To fail: if bound_s[0] == 0, take max(bound_s[1] + 1, s[0]), and s[1]
    #            if bound_s[1] == 4000, take s[0] and min(bound_s[0]-1, s[1])

    workflows_s, _ = data.split("\n\n")
    workflows = dict()
    for workflow in workflows_s.splitlines():
        name, steps_s = workflow.split("{")
        # print(f"Parsing workflow {name}")
        steps = []
        for step in steps_s.split(","):
            if step.endswith("}"):
                # Final step, this is a default.
                steps.append(Step(None, None, None, step[:-1], f"else --> {step[:-1]}"))
                break
            attr = step[0]
            comparator = step[1]
            compare_to, goto = step[2:].split(":")
            create_step = partial(
                Step,
                description=f"{attr} {comparator} {compare_to} --> {goto}",
            )
            if comparator == "<":
                step = create_step(attr, MIN_VALUE, int(compare_to)-1, goto)
            elif comparator == ">":
                step = create_step(attr, int(compare_to)+1, MAX_VALUE, goto)
            else:
                raise RuntimeError("AHHHH")

            steps.append(step)
        workflows[name] = steps
    # print(workflows)

    boundses = [{
        'goto': 'in',
        'x': (MIN_VALUE, MAX_VALUE),
        'm': (MIN_VALUE, MAX_VALUE),
        'a': (MIN_VALUE, MAX_VALUE),
        's': (MIN_VALUE, MAX_VALUE),
    }]

    accepted_bounds = []
    # while boundses:
    while boundses:
        bounds = boundses.pop()
        workflow = workflows[bounds['goto']]
        print(f"\nPopped {bounds}")
        for new_bounds in split_bounds_for_workflow(workflow, bounds):
            print(f"Got {new_bounds}.")
            if new_bounds['goto'] == "A":
                accepted_bounds.append(new_bounds)
                continue
            if new_bounds['goto'] == "R":
                # This one is done, but we don't need to count it.
                continue
            # This one has more workflows to traverse. Toss it onto the stack.
            boundses.append(new_bounds)

    # print(f"\n{accepted_bounds=}")

    total = 0
    # Calculate the total number of combinations of inputs for each bounds.
    for bounds in accepted_bounds:
        # Drop the goto.
        bounds.pop('goto')
        # Compute how many values are valid for each range.
        attr_ranges = [max_ - min_ + 1 if min_ <= max_ else 0 for min_, max_ in bounds.values()]
        this_total = 1
        for attr_range in attr_ranges:
            this_total *= attr_range
        print(f"{this_total} possible combinations for {bounds}")
        total += this_total
    return total
# 241818912886202 too high
# 143760172569135 correct..

def run_workflow_on_part(workflow: list[Step], part: dict[str, int]) -> str:
    """Return the workflow to goto."""
    for attr, min_, max_, goto, description in workflow:
        if attr is None:
            # This is the default case.
            return goto

        # print(f"Checking {description} on {part}...")
        if min_ <= part[attr] <= max_:
            # print("Yep!")
            return goto
        # print("Nope.")


def split_bounds_for_workflow(workflow: list[Step], bounds: dict) -> tuple:
    """For each step in the workflow, yield a reduced set of bounds for pass and
    for fail."""
    # 'qqz' = [
    #     ('s', 2771, 4000, 'qa')
    #     ('m', 0, 1800, 'hdj')
    #     (None, None, None, 'R')
    # ]
    #
    # Then, to process, if Bounds entering qqz is
    #
    #     (0, 4000), (0, 4000), (0, 4000), (1351, 4000)
    #
    # Bounds will split into
    #
    #     (0, 4000), (0, 4000), (0, 4000), (2771, 4000) -> 'qa'  (First passes)
    #     (0, 4000), (0, 1800), (0, 4000), (1351, 2770) -> 'hdj'  (Second passes)
    #     (0, 4000), (1801, 4000), (0, 4000), (1351, 4000) -> 'R'  (Default)
    #
    # For first: To pass: take max(test.min, s[0]), and min(test.max, s[1])
    #   To fail: if test.min == 0, take max(test.max + 1, s[0]), and s[1]
    #            if test.max == 4000, take s[0] and min(test.min-1, s[1])

    # This will be overwritten by failing bounds from the previous step. Copies
    # prevent mutability causing side effects.
    passing_bounds = bounds.copy()
    failing_bounds = bounds.copy()
    for attr, min_, max_, goto, description in workflow:
        print(f"Splitting bounds for {description}")
        # Create the passing case.
        passing_bounds['goto'] = goto
        if attr is None:
            # This is the default (final) case.
            yield passing_bounds
            break

        # These are the limits coming into this split.
        old_min = passing_bounds[attr][0]
        old_max = passing_bounds[attr][1]
        passing_bounds[attr] = (max(min_, old_min), min(max_, old_max))
        yield passing_bounds

        # Create the failing case.
        if min_ == MIN_VALUE:
            # This is a < case. To fail, we must be >= the upper bound. +1
            # because we subtracted 1 earlier to make an inclusive bound.
            failing_bounds[attr] = (max(max_+1, old_min), old_max)
        elif max_ == MAX_VALUE:
            # This is a > case. To fail, we must be <= the lower bound. -1
            # because we added 1 earlier to make an inclusive bound for passing.
            failing_bounds[attr] = (old_min, min(min_-1, old_max))
        # Create a copy of this so we can apply passing and failing criteria
        # from the next step to this new set of bounds.
        passing_bounds = failing_bounds.copy()


if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
