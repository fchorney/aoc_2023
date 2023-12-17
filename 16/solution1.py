import argparse
import sys
from abc import ABC, abstractmethod
from copy import deepcopy
from enum import Enum
from pathlib import Path
from typing import Optional, Sequence

from icecream import ic


class Dir(Enum):
    N = 0
    E = 1
    S = 2
    W = 3
    MT = 4


class Mirror(ABC):
    @abstractmethod
    def enter(self, heading: Dir) -> list[Dir]:
        return NotImplemented

    @abstractmethod
    def __str__(self) -> str:
        return NotImplemented

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def create(cls, symbol: str) -> "Mirror":
        match symbol:
            case ".":
                return Space()
            case "|":
                return VSplitter()
            case "-":
                return HSplitter()
            case "/":
                return RSplitter()
            case "\\":
                return LSplitter()

        return NotImplemented


class VSplitter(Mirror):
    """
    |
    """

    def enter(self, heading: Dir) -> list[Dir]:
        match heading:
            case Dir.N:
                return [Dir.N]
            case Dir.S:
                return [Dir.S]
            case _:
                return [Dir.S, Dir.N]

    def __str__(self) -> str:
        return "|"


class HSplitter(Mirror):
    """
    -
    """

    def enter(self, heading: Dir) -> list[Dir]:
        match heading:
            case Dir.W:
                return [Dir.W]
            case Dir.E:
                return [Dir.E]
            case _:
                return [Dir.E, Dir.W]

    def __str__(self) -> str:
        return "-"


class RSplitter(Mirror):
    """
    /
    """

    def enter(self, heading: Dir) -> list[Dir]:
        match heading:
            case Dir.N:
                return [Dir.E]
            case Dir.E:
                return [Dir.N]
            case Dir.S:
                return [Dir.W]
            case Dir.W:
                return [Dir.S]

    def __str__(self) -> str:
        return "/"


class LSplitter(Mirror):
    """
    \
    """

    def enter(self, heading: Dir) -> list[Dir]:
        match heading:
            case Dir.N:
                return [Dir.W]
            case Dir.E:
                return [Dir.S]
            case Dir.S:
                return [Dir.E]
            case Dir.W:
                return [Dir.N]

    def __str__(self) -> str:
        return "\\"


class Space(Mirror):
    """
    .
    """

    def enter(self, heading: Dir) -> list[Dir]:
        """
        Whatever direction we were headed into this space in, we keep going that way.
        """
        return [heading]

    def __str__(self) -> str:
        return "."


class DebugMirror(Mirror):
    def __init__(self, char: str):
        self.char = char

    def enter(self, heading: Dir) -> list[Dir]:
        return []

    def __str__(self) -> str:
        return self.char


class Instruction:
    def __init__(self, row: int, col: int, direction: Dir):
        self.row = row
        self.col = col
        self.direction = direction

    def apply(self, grid: "Grid") -> "list[Instruction] | None":
        # The instruction is off the grid
        if self.row < 0 or self.row >= len(grid.data):
            return None

        if self.col < 0 or self.col >= len(grid.data[0]):
            return None

        # If we have visited this mirror before going the same direction, stop
        if self.direction in grid.energized[self.row][self.col]:
            return None

        # Set the current direction on the mirror
        grid.energized[self.row][self.col].append(self.direction)
        if Dir.MT in grid.energized[self.row][self.col]:
            grid.ener_count += 1
            del grid.energized[self.row][self.col][0]

        # Grab the mirror
        directions = grid.data[self.row][self.col].enter(self.direction)

        output: list[Instruction] = []
        for direction in directions:
            match direction:
                case Dir.N:
                    instruction = Instruction(self.row - 1, self.col, Dir.N)
                case Dir.E:
                    instruction = Instruction(self.row, self.col + 1, Dir.E)
                case Dir.S:
                    instruction = Instruction(self.row + 1, self.col, Dir.S)
                case Dir.W:
                    instruction = Instruction(self.row, self.col - 1, Dir.W)
            output.append(instruction)
        return output

    def __str__(self) -> str:
        return f"<{self.row}, {self.col}, {self.direction.name}>"

    def __repr__(self) -> str:
        return self.__str__()


class Grid:
    def __init__(self, data: list[list[Mirror]]):
        self.data = data
        self.energized: list[list[list[Dir]]] = [
            [[Dir.MT] for _ in row] for row in self.data
        ]
        self.ener_count = 0

    def energize(self, inst: Instruction) -> None:
        instructions = inst.apply(self)

        if not instructions:
            return

        # print(inst)
        # print(self.location(inst))
        # print(self.ener_str())
        # print()

        for instruction in instructions:
            self.energize(instruction)

    def energized_count(self) -> int:
        return self.ener_count

    def location(self, inst: Instruction) -> str:
        """
        Given the current grid and instruction, show where we are
        """
        match inst.direction:
            case Dir.N:
                dir_str = "^"
            case Dir.E:
                dir_str = ">"
            case Dir.S:
                dir_str = "v"
            case Dir.W:
                dir_str = "<"

        data = deepcopy(self.data)
        data[inst.row][inst.col] = DebugMirror(dir_str)

        return self.data_str(data)

    def data_str(self, grid: list[list[Mirror]] | None = None) -> str:
        data = grid if grid is not None else self.data

        return "\n".join("".join(map(str, row)) for row in data)

    def ener_str(self) -> str:
        output = ""
        for row in self.energized:
            r_str = ""
            for col in row:
                if Dir.MT in col:
                    del col[0]
                r_str += f"{len(col)}"
            output += f"{r_str}\n"

        # output = ""
        # for row in self.energized:
        #    r_str = ""
        #    for col in row:
        #        r_str += f"[{','.join(x.name for x in col)}]"
        #    output += f"{r_str}\n"

        return output


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    if pargs.quiet:
        ic.disable()

    data: list[list[Mirror]] = []
    with input_path.open() as f:
        for line in map(str.strip, f.readlines()):
            row: list[Mirror] = []
            for symbol in list(line):
                row.append(Mirror.create(symbol))
            data.append(row)

    grid = Grid(data)
    # print(grid.ener_str())

    # Start at row 0, column 0, going East
    sys.setrecursionlimit(100000)
    grid.energize(Instruction(0, 0, Dir.E))
    print(grid.ener_str())
    ic(grid.energized_count())


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    parser.add_argument("-q", "--quiet", action="store_true")

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
