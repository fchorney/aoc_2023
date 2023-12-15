import argparse
from pathlib import Path
from typing import Optional, Sequence

from icecream import ic


ROCK = 0
STONE = 1
SPACE = 7


def move_rock_north(platform: list[list[int]], row: int, col: int) -> None:
    while (row := row - 1) >= 0 and platform[row][col] == SPACE:
        platform[row][col] = ROCK
        platform[row + 1][col] = SPACE


def tilt_platform_north(platform: list[list[int]]) -> None:
    # Rocks [0] move with tilt direction
    # Stones [1] don't move, and stop Rocks
    # Empty Space [7] don't do anything

    # Go through the platform and move any rock that we find that can be moved
    for row, row_data in enumerate(platform):
        for col, value in enumerate(row_data):
            # If we're a rock
            if value == ROCK:
                # If we're at the edge of the map, or there's a stone above us, continue
                if row - 1 < 0 or platform[row - 1][col] == STONE:
                    continue
                move_rock_north(platform, row, col)


def get_platform_load(platform: list[list[int]]) -> int:
    load = 0
    platform_len = len(platform)
    for idx, row in enumerate(platform):
        load_value = platform_len - idx
        load += row_to_str(row).count("O") * load_value
    return load


def row_to_str(row: list[int]) -> str:
    return "".join(map(str, row)).replace("0", "O").replace("1", "#").replace("7", ".")


def print_platform(platform: list[list[int]]) -> str:
    output = ""
    for row in platform:
        output += row_to_str(row) + "\n"
    return output[:-1]


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    platform: list[list[int]] = []
    with input_path.open() as f:
        for line in map(str.strip, f.readlines()):
            line = line.replace("O", "0").replace("#", "1").replace(".", "7")
            platform.append(list(map(int, line)))

    print(print_platform(platform))

    tilt_platform_north(platform)

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
