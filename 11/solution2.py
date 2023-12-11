import argparse
from itertools import combinations
from pathlib import Path
from typing import Optional, Sequence

from icecream import ic


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    space: list[list[int]] = []
    expanded_rows: list[int] = []
    expanded_cols: list[int] = []
    with input_path.open() as f:
        for row, line in enumerate(map(str.strip, f.readlines())):
            # If the row is devoid of galaxies it will be expanded later.
            if line.count("#") == 0:
                expanded_rows.append(row)

            space.append(list(map(int, line.replace("#", "1").replace(".", "0"))))

    # Transpose space
    space = [list(x) for x in zip(*space)]

    # A row (col) devoid of galaxies will be expanded later
    for col, t_row in enumerate(space):
        if t_row.count(0) == len(t_row):
            expanded_cols.append(col)

    # Transpose it back
    space = [list(x) for x in zip(*space)]

    # Find coordinates for all galaxies
    galaxy_locations: dict[int, tuple[int, int]] = {}

    galaxy = 1
    for r, v in enumerate(space):
        for c, value in enumerate(v):
            if value == 1:
                galaxy_locations[galaxy] = (r, c)
                galaxy += 1

    # Generate all galaxy pairs
    galaxy_pairs = list(combinations(list(range(1, galaxy)), 2))

    # Any expanded row or columns will be expanded to this amount
    expansion_rate = 1_000_000

    # Find distance between all galaxy pairs, and the sum of all distances
    distance_sum = 0
    for a, b in galaxy_pairs:
        # Grab Row/Col coordinates for both galaxies
        a_r, a_c = galaxy_locations[a]
        b_r, b_c = galaxy_locations[b]

        # Find which rows and columns the distance between the pairs crosses
        row_range = list(range(min(a_r, b_r) + 1, max(a_r, b_r)))
        col_range = list(range(min(a_c, b_c) + 1, max(a_c, b_c)))

        # Determine if any rows or columns are expanded and what their expanded values
        # would be
        row_mult = sum(x in row_range for x in expanded_rows) * (expansion_rate - 1)
        col_mult = sum(x in col_range for x in expanded_cols) * (expansion_rate - 1)

        # Add all distances together
        distance_sum += abs(a_c - b_c) + abs(a_r - b_r) + row_mult + col_mult
    ic(distance_sum)


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 6: Solution 1")

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
