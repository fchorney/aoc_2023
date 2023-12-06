import argparse
import re
from pathlib import Path
from typing import Optional, Sequence


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    races: list[tuple[int, int]] = []

    with input_path.open() as f:
        times: list[int] = []
        distances: list[int] = []
        for line in f.readlines():
            if line.startswith("Time:"):
                times = list(map(int, re.findall(r"\d+", line)))

            if line.startswith("Distance:"):
                distances = list(map(int, re.findall(r"\d+", line)))

        races = list(zip(times, distances))

    win_prod = 1
    for time, record in races:
        win_list = []

        # Find First Winner
        for x in range(0, time + 1):
            distance = x * (time - x)
            if distance > record:
                win_list.append(x)
                break

        # Find Last Winner
        for x in range(time, 0 - 1, -1):
            distance = x * (time - x)
            if distance > record:
                win_list.append(x)
                break

        wins = win_list[1] - win_list[0] + 1

        print(f"{time} - {record} -> {wins} / {win_list}")
        win_prod *= wins

    print(win_prod)


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 6: Solution 1")

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
