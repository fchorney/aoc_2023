import argparse
from pathlib import Path
from typing import Optional, Sequence

from icecream import ic


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    histories: list[list[int]] = []
    with input_path.open() as f:
        for line in map(str.strip, f.readlines()):
            histories.append(list(map(int, line.split(" "))))

    extrapolated_values: list[int] = []
    for history in histories:
        diff_lists: list[list[int]] = [history]
        idx = 0

        # Find all the diffs
        ic(history)
        while set(diff_lists[idx]) != {0}:
            new_list: list[int] = []
            for fidx in range(0, len(diff_lists[idx]) - 1):
                new_list.append(diff_lists[idx][fidx + 1] - diff_lists[idx][fidx])

            diff_lists.append(new_list)
            idx = idx + 1

        ic(diff_lists)

        # Bubble up the next number
        for idx in range(len(diff_lists) - 2, -1, -1):
            diff_lists[idx].insert(0, diff_lists[idx][0] - diff_lists[idx + 1][0])

        ic(diff_lists)

        extrapolated_values.append(diff_lists[0][0])

    ic(sum(extrapolated_values))


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 6: Solution 1")

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
