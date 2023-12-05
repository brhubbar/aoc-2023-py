"""Day N."""

import re
from collections import namedtuple
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day5')

MAP_NAME = re.compile(r"\s*[\w \-]+:\s+")
Range = namedtuple("Range", ['start', 'end', 'offset'])

"seeds"
"seed-to-soil"
"soil-to-fertilizer"
"fertilizer-to-water"
"water-to-light"
"light-to-temperature"
"temperature-to-humidity"
"humidity-to-location"

def part1(data: str) -> int:
    map_strings = MAP_NAME.split(data)
    # Maps start with seed and end with location. In between, they go x-->y,
    # y-->z, z-->...
    while not map_strings[0]:
        # Drop the empty guy.
        map_strings.pop(0)

    # First real one is the seeds.
    seeds = map_strings.pop(0)
    seeds = [int(x) for x in seeds.split()]
    # Each map will stores the start and end of non-1:1 mappings from source to
    # destination. On a get, if the value is within one of those ranges, it'll
    # be offset accordingly, otherwise the value is just the key. So for a given
    # a, within a known range, the value will be offset by the difference
    # between src_start and dest_start. So, I need to store the start, the end,
    # and the offset for a given src number. Therefore, each map will be a list
    # of three-tuples.
    maps = []
    for map_string in map_strings:
        this_map = list()
        range_strings = map_string.splitlines()
        for range_string in range_strings:
            # These are always three-tuples.
            dest_start, src_start, length = [int(x) for x in range_string.split()]
            # Minus 1 because a length of two means start and 1 more. Offset is
            # added to the src number to set it to the right spot. E.g. if
            # source start is 98 and dest start is 50, 98 + -48 = 50.
            this_range = Range(src_start, src_start+length-1, dest_start-src_start)
            this_map.append(this_range)
        maps.append(this_map)

    # Now that we've built the maps, time to get the location of each seed.
    locations = []
    for seed in seeds:
        source = seed
        for map_ in maps:
            print(f"Source = {source}")
            for range_ in map_:
                if source < range_.start or source > range_.end:
                    # not in range.
                    continue
                # Apply the offset and continue to the next mapping. If this
                # never matches, then we stay 1:1
                source += range_.offset
                break
        # source now == location
        locations.append(source)
        print(f"Next location: {source}.\n")
    return min(locations)


def part2(data: str) -> int:
    map_strings = MAP_NAME.split(data)
    # Maps start with seed and end with location. In between, they go x-->y,
    # y-->z, z-->...
    while not map_strings[0]:
        # Drop the empty guy.
        map_strings.pop(0)

    # First real one is the seeds.
    seed_numbers = [int(x) for x in map_strings.pop(0).split()]
    # start, length, start, length --> [(start, stop), (start, stop),...]
    seed_ranges = [
        (seed_numbers[i], seed_numbers[i]+seed_numbers[i+1]-1)
        for i in range(0, len(seed_numbers), 2)
    ]
    # print(f"{seed_ranges=}")
    # Each map will stores the start and end of non-1:1 mappings from source to
    # destination. On a get, if the value is within one of those ranges, it'll
    # be offset accordingly, otherwise the value is just the key. So for a given
    # a, within a known range, the value will be offset by the difference
    # between src_start and dest_start. So, I need to store the start, the end,
    # and the offset for a given src number. Therefore, each map will be a list
    # of three-tuples.
    maps = []
    for map_string in map_strings:
        this_map = list()
        range_strings = map_string.splitlines()
        for range_string in range_strings:
            # These are always three-tuples.
            dest_start, src_start, length = [int(x) for x in range_string.split()]
            # Minus 1 because a length of two means start and 1 more. Offset is
            # added to the src number to set it to the right spot. E.g. if
            # source start is 98 and dest start is 50, 98 + -48 = 50.
            this_range = Range(src_start, src_start+length-1, dest_start-src_start)
            this_map.append(this_range)
        maps.append(this_map)

    # print(f"{maps[0]=}") For a given seed range, I need to check every seed
    # that lands on either side of a boundary for any level of map. So given the
    # possible seeds, I need to compute possible soils. Given those, the
    # possible fertilizers, and so on...
    #
    # So, for a range of seeds [a, b] and a map of seeds to soils, I can compute
    # a set of soil ranges, [(c, d), (e, f),...]. I can then repeat that for
    # each range of soils to ranges of fertilizer, and so on. From those, I can
    # just pick the smallest location.
    #
    # To do this, I need a recursive function that maps a range to a set of
    # ranges one resource down.
    # List of lists of tuples, one list of lists for each resource, and one
    # tuple for each range that's included.
    hit_ranges = [seed_ranges]
    for map_ in maps:
        hit_ranges.append(get_ranges_of_dest_for_range_of_sources(map_, *hit_ranges[-1]))

    # Iterate back up to determine seed ids for each location found.
    maps.reverse()
    seeds = []
    for range_ in hit_ranges[-1]:
        for dest in range_:
            for map_ in maps:
                # print(f"Dest = {dest}")
                for range_ in map_:
                    if dest-range_.offset < range_.start or dest-range_.offset > range_.end:
                        # not in range.
                        continue
                    # Apply the offset and continue to the next mapping. If this
                    # never matches, then we stay 1:1
                    dest -= range_.offset
                    break
            # dest now == seed
            seeds.append(dest)
            # print(f"Next seed: {dest}.\n")

    # Make sure seeds are within range.
    actual_seeds = set()
    for seed in seeds:
        for seed_range in seed_ranges:
            if min(seed_range) < seed < max(seed_range):
                actual_seeds.add(seed)
                break
    print(f"{actual_seeds=}")

    # Now that we've built the maps, time to get the location of each seed.
    locations = []
    maps.reverse()
    for seed in actual_seeds:
        source = seed
        for map_ in maps:
            # print(f"Source = {source}")
            for range_ in map_:
                if source < range_.start or source > range_.end:
                    # not in range.
                    continue
                # Apply the offset and continue to the next mapping. If this
                # never matches, then we stay 1:1
                source += range_.offset
                break
        # source now == location
        locations.append(source)
        # print(f"Next location: {source}.\n")
    return min(locations)

def get_ranges_of_dest_for_range_of_sources(
    dest_map: list[Range],
    *source_ranges: tuple[tuple],
) -> list[tuple]:
    dest_ranges_to_check = []
    for source_range in source_ranges:
        # The tuples aren't necessarily (min, max) after one iteration.
        min_ = min(source_range)
        max_ = max(source_range)
        dest_ranges_to_check_for_this_range = set()
        for range_ in dest_map:
            # print(f"Checking {source_range} against {range_}")
            if (min_ <= range_.start <= max_):
                # Starts outside the range,
                dest_ranges_to_check_for_this_range.add((min_, range_.start-1))
                # ends inside the range.
                dest_ranges_to_check_for_this_range.add((range_.start+range_.offset, max_+range_.offset))
            elif (min_ <= range_.end <= max_):
                # Starts inside the range,
                dest_ranges_to_check_for_this_range.add((min_+range_.offset, range_.end+range_.offset))
                # ends outside the range.
                dest_ranges_to_check_for_this_range.add((range_.end+1, max_))
            elif (range_.start <= min_ and range_.end >= max_):
                # Lies wholly within the range.
                dest_ranges_to_check_for_this_range.add((min_+range_.offset, max_+range_.offset))
            else:
                # Lies wholly outside the range. This is fine to do with
                # overlaps because I cut those out later.
                dest_ranges_to_check_for_this_range.add((min_, max_))

        dest_ranges_to_check.extend(dest_ranges_to_check_for_this_range)

    # print(f"Found {dest_ranges_to_check=}\n")
    if dest_ranges_to_check:
        return dest_ranges_to_check
    return list(source_ranges)


if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
