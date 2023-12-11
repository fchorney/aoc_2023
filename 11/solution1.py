import argparse
from itertools import combinations
from pathlib import Path
from typing import Optional, Sequence

from icecream import ic


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    space: list[list[int]] = []
    with input_path.open() as f:
        for line in map(str.strip, f.readlines()):
            # Count number values
            galaxy_count = line.count("#")

            for _ in range(0, galaxy_count):
                line = line.replace("#", "1", 1)
            line = line.replace(".", "0")

            new_row = list(map(int, line))
            space.append(new_row)

            # If the row is devoid of galaxies, its twice as high, so append it again
            if galaxy_count == 0:
                space.append(new_row.copy())

    # We were able to expand rows in reading the data, but now we must expand empty
    # columns

    # Transpose space
    old_space = [list(x) for x in zip(*space)]
    space = []

    # Find empty rows and double them
    for row in old_space:
        space.append(row)
        if row.count(0) == len(row):
            space.append(row.copy())

    # Transpose it back
    space = [list(x) for x in zip(*space)]

    # Find all coordinates for galaxies
    galaxy_locations: dict[int, tuple[int, int]] = {}

    galaxy = 1
    for r, v in enumerate(space):
        for c, value in enumerate(v):
            if value == 1:
                galaxy_locations[galaxy] = (r, c)
                galaxy += 1

    # Find all pairs we need to determine
    galaxy_pairs = list(combinations(list(range(1, galaxy)), 2))

    distance_sum = 0
    for a, b in galaxy_pairs:
        a_r, a_c = galaxy_locations[a]
        b_r, b_c = galaxy_locations[b]

        distance = abs(a_c - b_c) + abs(a_r - b_r)
        # ic(a, b, distance)
        distance_sum += distance
    ic(distance_sum)


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 6: Solution 1")

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
