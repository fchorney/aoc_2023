import argparse
from pathlib import Path
from typing import Optional, Sequence

from icecream import ic


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    with input_path.open() as f:
        for line in map(str.strip, f.readlines()):
            pass


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 6: Solution 1")

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
