import argparse
import re
from functools import cache
from pathlib import Path
from typing import Optional, Pattern, Sequence

from icecream import ic


# This code is essentially taken from https://github.com/dgDSA/AdventOfCode2023/blob/main/12.py
# Big thanks. You can see my very bad half attempt at a solution in `solution2.py`.

operational_re = re.compile(r"\.+")


class Nonogram:
    def __init__(self, data: str, groups: tuple[int, ...]):
        self.data = data
        self.groups = groups

    def __str__(self) -> str:
        return f"Nonogram<data='{self.data}', groups={self.groups}>"

    def __repr__(self) -> str:
        return self.__str__()


@cache
def find_broken_re(count: int) -> Pattern[str]:
    """
    Returns a pattern which matches a group of one or more machines which has
    exactly the given length.
    """
    # "#" or "?" `count` times, and then "." or "?" or the end of the string
    return re.compile(rf"[\#\?]{{{count}}}(\.|\?|$)")


@cache
def find_permutations(data: str, groups: tuple[int, ...]) -> int:
    # If we have run out of data...
    if not data:
        if groups:
            # Fail: We have reached the end of the row with groups still available
            return 0
        # We reached the end of data successfully
        return 1

    # If we have run out of groups...
    if not groups:
        if "#" in data:
            # Fail: We have run out of groups, but still have Damaged parts
            # available
            return 0
        # We reached the end of the groups with no Damaged parts left. Success
        return 1

    # Find any contiguous Operational parts
    if operational_parts := operational_re.match(data):
        # Just skip the operational parts and continue on with the next subset
        return find_permutations(data[len(operational_parts.group()) :], groups)

    successes = 0
    # If we're on an unknown part
    if data[0] == "?":
        # Assume this machine works, and continue on
        successes += find_permutations(data[1:], groups)

    if possibly_broken := find_broken_re(groups[0]).match(data):
        # Assume all parts in this range are broken
        successes += find_permutations(data[len(possibly_broken.group()) :], groups[1:])

    return successes


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    nonograms: list[Nonogram] = []
    with input_path.open() as f:
        for line in map(str.strip, f.readlines()):
            data, groups = line.split(" ")
            nonograms.append(
                Nonogram(
                    "?".join(x for x in [data] for _ in range(5)),
                    tuple(map(int, groups.split(","))) * 5,
                )
            )

    ic(nonograms)
    all_permutations = [find_permutations(x.data, x.groups) for x in nonograms]
    ic(sum(all_permutations))


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 6: Solution 1")

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
