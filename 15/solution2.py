import argparse
import re
from enum import Enum
from pathlib import Path
from typing import Optional, Sequence

from icecream import ic


SPLIT_RE = re.compile(r"(?P<inst>[A-Za-z]+)(?:=|-)(?P<focal>\d+)?")


class Mode(Enum):
    REMOVE = 0
    INSERT = 1


class Item:
    def __init__(self, instruction: str, focal_length: int):
        self.instruction = instruction
        self.focal_length = focal_length

    def __str__(self) -> str:
        return f"[{self.instruction} {self.focal_length}]"

    def __repr__(self) -> str:
        return self.__str__()


class HashMap:
    def __init__(self, length: int):
        self.store: dict[int, list[Item]] = {}
        self.length = length

        # Initialize boxes
        for idx in range(length):
            self.store[idx] = []

    def remove(self, instruction: str) -> None:
        key = hash_algo(instruction) % self.length
        box = self.store[key]

        if (exists := self.find_existing(box, instruction)) is not None:
            del box[exists]

    def find_existing(self, box: list[Item], instruction: str) -> int | None:
        for idx, item in enumerate(box):
            if item.instruction == instruction:
                return idx
        return None

    def insert(self, instruction: str, focal_length: int) -> None:
        item = Item(instruction, focal_length)
        key = hash_algo(instruction) % self.length
        box = self.store[key]

        # First check if a lense with the same focal length exists in the box
        if (exists := self.find_existing(box, instruction)) is not None:
            # Replace the existing item with the new one
            box[exists] = item
        else:
            box.append(item)

    def focusing_power(self) -> int:
        _sum = 0
        for key, box in self.store.items():
            for idx, item in enumerate(box):
                power = (1 + key) * (idx + 1) * item.focal_length
                _sum += power

                ic(key, idx, item.focal_length, power)

        return _sum

    def __str__(self) -> str:
        if len(self.store) == 0:
            return "HashMap<>"

        result = "HashMap<\n"
        for idx, row in self.store.items():
            if len(row) > 0:
                result += f"\tBox {idx}: "
                result += " ".join(map(str, row))
                result += "\n"
        return result + ">"

    def __repr__(self) -> str:
        return self.__str__()


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

    hashmap = HashMap(256)
    for full_instruction in seq:
        if not (matches := SPLIT_RE.match(full_instruction)):
            print(f"Could Not Parse '{full_instruction}'")
            return

        if not (instruction := matches.group("inst")):
            print(f"Could not find instruction '{full_instruction}'")
            return

        mode = Mode.REMOVE
        focal = 0
        if focal_str := matches.group("focal"):
            mode = Mode.INSERT
            focal = int(focal_str)

        ic(full_instruction)
        # ic(full_instruction, instruction, mode, focal)

        if mode == Mode.INSERT:
            hashmap.insert(instruction, focal)
        else:
            hashmap.remove(instruction)

    ic(hashmap)
    focusing_power = hashmap.focusing_power()
    ic(focusing_power)
    print(focusing_power)


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 6: Solution 1")

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    parser.add_argument("-q", "--quiet", action="store_true")

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
