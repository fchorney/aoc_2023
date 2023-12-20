import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Sequence
from extra.convert_hex_xterm import rgb2short
from icecream import ic

INPUT_RE = re.compile(r"(?P<direction>[UDLR]) (?P<count>\d+) \(#(?P<color>[0-9a-z]+)\)")

class Direction(Enum):
    U = 0
    R = 1
    D = 2
    L = 3

@dataclass
class Instruction:
    direction: Direction
    count: int
    color: str

class HoleType(Enum):
    EDGE = 0
    EMPTY = 1
    INNER = 2
@dataclass
class Hole:
    _type: HoleType
    color: str | None

@dataclass
class Coordinate:
    row: int
    col: int

    def __add__(self, other) -> "Coordinate":
        if isinstance(other, Coordinate):
            row = self.row + other.row
            col = self.col + other.col
            return Coordinate(row, col)
        return NotImplemented

class Trench:
    def __init__(self):
        self.vertices: list[Coordinate] = [Coordinate(0, 0)]
        self.perimeter: int = 0

    def process(self, instruction: Instruction) -> None:
        count = instruction.count
        r = c = 0
        match instruction.direction:
            case Direction.U:
                r -= 1
            case Direction.D:
                r += 1
            case Direction.L:
                c -= 1
            case Direction.R:
                c += 1

        ic(self.vertices[-1])
        ic(Coordinate(r * count, c * count))
        self.vertices.append(self.vertices[-1] + Coordinate(r * count, c * count))
        self.perimeter += count

    def find_area(self) -> int:
        vertices = self.vertices
        n = len(vertices)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i].row * vertices[j].col
            area -= vertices[j].row * vertices[i].col
        area = abs(area) / 2
        return int(area) + self.perimeter // 2 + 1

def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    if pargs.quiet:
        ic.disable()

    instructions: list[Instruction] = []
    with input_path.open() as f:
        for line in map(str.strip, f.readlines()):
            if not (matches := INPUT_RE.match(line)):
                print(f"Error: Can't parse {line}")
            direction = Direction[matches.group("direction")]
            count = int(matches.group("count"))
            color = matches.group("color")
            instructions.append(Instruction(direction, count, color))

    trench = Trench()
    for instruction in instructions:
        ic(instruction)
        trench.process(instruction)

    area = trench.find_area()
    ic(area)
    print(area)


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    parser.add_argument("-q", "--quiet", action="store_true")

    return parser.parse_args(args)


if __name__ == "__main__":
    main(['input'])
