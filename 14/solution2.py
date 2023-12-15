import argparse
from functools import cache
from pathlib import Path
from typing import Optional, Sequence

from icecream import ic


ROCK = 0
STONE = 1
SPACE = 7


PLATFORM_TYPE = tuple[tuple[int, ...], ...]


def move_rock_north(platform: list[list[int]], row: int, col: int) -> None:
    # Convert to list of lists for this
    while (row := row - 1) >= 0 and platform[row][col] == SPACE:
        platform[row][col] = ROCK
        platform[row + 1][col] = SPACE


@cache
def tilt_platform_north(platform: PLATFORM_TYPE) -> PLATFORM_TYPE:
    # Rocks [0] move with tilt direction
    # Stones [1] don't move, and stop Rocks
    # Empty Space [7] don't do anything

    plat: list[list[int]] = list([list(x) for x in platform])

    # Go through the platform and move any rock that we find that can be moved
    for row, row_data in enumerate(plat):
        for col, value in enumerate(row_data):
            # If we're a rock
            if value == ROCK:
                # If we're at the edge of the map, or there's a stone above us, continue
                if row - 1 < 0 or plat[row - 1][col] == STONE:
                    continue
                move_rock_north(plat, row, col)

    return tuple(tuple(x) for x in plat)


def get_platform_load(platform: PLATFORM_TYPE) -> int:
    load = 0
    platform_len = len(platform)
    for idx, row in enumerate(platform):
        load_value = platform_len - idx
        load += row_to_str(row).count("O") * load_value
    return load


def row_to_str(row: tuple[int, ...]) -> str:
    return "".join(map(str, row)).replace("0", "O").replace("1", "#").replace("7", ".")


def print_platform(platform: PLATFORM_TYPE) -> str:
    output = ""
    for row in platform:
        output += row_to_str(row) + "\n"
    return output[:-1]


@cache
def rotate_platform_90_clockwise(platform: PLATFORM_TYPE) -> PLATFORM_TYPE:
    return tuple(tuple(x)[::-1] for x in zip(*platform))


def cycle_platform(
    platform: PLATFORM_TYPE, count: int, detect: bool = True
) -> PLATFORM_TYPE:
    # For each cycle, tilt north, rotate 90, tilt north (west), rotate 90,
    # tilt north (south), rotate 90, tilt north (east), rotate 90.
    # Now we're back to the original orientation
    previous_cycles: list[tuple] = [platform]

    for cycle in range(count * 4):
        platform = rotate_platform_90_clockwise(tilt_platform_north(platform))
        if detect and cycle % 4 == 0:
            if platform in previous_cycles:
                ic("We found a loop?")
                ic(cycle / 4)
                ic(previous_cycles.index(platform))
            previous_cycles.append(platform)

    return platform


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    platform_tmp: list[list[int]] = []
    with input_path.open() as f:
        for line in map(str.strip, f.readlines()):
            line = line.replace("O", "0").replace("#", "1").replace(".", "7")
            platform_tmp.append(list(map(int, line)))

    platform = tuple(tuple(x) for x in platform_tmp)

    print(print_platform(platform))

    platform = cycle_platform(platform, 1_000_000_000, detect=False)

    print("\n\n")
    print(print_platform(platform))

    load = get_platform_load(platform)
    ic(load)


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 6: Solution 1")

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
