import argparse
from pathlib import Path
from typing import Optional, Sequence

from icecream import ic


def hash_algo(instruction: str) -> int:
    value = 0
    for char in map(ord, instruction):
        value += char
        value *= 17
        value %= 256

    return value


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    if pargs.quiet:
        ic.disable()

    seq: list[str] = []
    with input_path.open() as f:
        line = f.read().strip()
        for instruction in map(str.strip, line.split(",")):
            seq.append(instruction)

    hashes: list[int] = []
    for instruction in seq:
        res = hash_algo(instruction)
        ic(instruction, res)
        hashes.append(res)

    _sum = sum(hashes)
    ic(_sum)
    print(_sum)


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 6: Solution 1")

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    parser.add_argument("-q", "--quiet", action="store_true")

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
