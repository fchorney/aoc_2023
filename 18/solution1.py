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

    def __str__(self) -> str:
        color = self.color or "FFFFFF"
        txt = "#" if self._type in [HoleType.EDGE, HoleType.INNER] else "."
        result = f"\033[38;5;{rgb2short(color)[0]}m{txt}\033[0m"
        return result

@dataclass
class Coordinate:
    row: int
    col: int

    def __add__(self, other) -> "Coordinate":
        if isinstance(other, Coordinate):
            self.row += other.row
            self.col += other.col
            return self
        return NotImplemented

class Trench:
    def __init__(self):
        self.terrain: dict[int[dict[int, Hole]]] = defaultdict(lambda: defaultdict(int))
        self.coordinate: Coordinate = Coordinate(0, 0)
        self.grid: list[list[Hole]] = []
        self.dig_count: int = 0

    def dig(self, hole: Hole) -> None:
        self.terrain[self.coordinate.row][self.coordinate.col] = hole

    def process(self, instruction: Instruction) -> None:
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

        new_coord = Coordinate(r, c)
        for _ in range(instruction.count):
            self.coordinate += new_coord
            self.dig(Hole(HoleType.EDGE, instruction.color))

    def generate_grid(self) -> list[list[Hole]]:
        row_offset = min(self.terrain.keys())
        col_offset = min(min(x.keys()) for x in self.terrain.values())

        row_max = max(self.terrain.keys()) + abs(row_offset) + 1
        col_max = max(max(x.keys()) for x in self.terrain.values()) + abs(col_offset) + 1

        ic(row_offset, col_offset, row_max, col_max)

        # Create the grid
        dig_count = 0
        grid: list[list[Hole]] = []
        for row in range(row_max):
            grid.append([])
            for col in range(col_max):
                hole = self.terrain.get(row+row_offset, {}).get(col + col_offset, None)
                if hole:
                    grid[row].append(hole)
                    dig_count += 1
                else:
                    # Determine if it's an empty plot, or a filled plot
                    boundaries = 0
                    if row > 0 or row < len(grid):
                        look = True
                        for inner_col in range(col - 1, -1, -1):
                            if grid[row][inner_col]._type == HoleType.EDGE:
                                if look:
                                    if (
                                        inner_col - 1 >= 0 and
                                        grid[row][inner_col - 1]._type == HoleType.EDGE
                                    ):
                                        # We found a run and the above hole is an edge.
                                        # Ignore any more edges until we hit an empty spot
                                        look = False
                                    if look or row - 1 >= 0 and grid[row-1][inner_col]._type == HoleType.EDGE:
                                        boundaries += 1
                                else:
                                    if (
                                        inner_col == 0 and
                                        grid[row][inner_col]._type == HoleType.EDGE
                                        and row -1 >= 0
                                        and grid[row-1][inner_col]._type == HoleType.EDGE
                                    ):
                                        boundaries += 1
                                    if inner_col - 1 >= 0 and grid[row][inner_col - 1]._type != HoleType.EDGE:
                                        if row - 1 >= 0 and grid[row-1][inner_col]._type == HoleType.EDGE:
                                            boundaries += 1
                            else:
                                look = True

                    if boundaries % 2 == 0:
                        grid[row].append(Hole(HoleType.EMPTY, None))
                    else:
                        grid[row].append(Hole(HoleType.INNER, None))
                        dig_count += 1

        self.dig_count = dig_count
        return grid

    def to_console(self) -> str:
        output = ""
        for r in self.generate_grid():
            for c in r:
                output += str(c)
            output+="\n"
        return output

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

    o = trench.to_console()
    print(o)
    ic(trench.dig_count)
    print(trench.dig_count)

def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    parser.add_argument("-q", "--quiet", action="store_true")

    return parser.parse_args(args)


if __name__ == "__main__":
    main(['testinput1', '-q'])
