import argparse
import pprint
from copy import deepcopy
from enum import Enum
from pathlib import Path
from typing import Optional, Self, Sequence

from icecream import ic


# preferredWidth = 20
# pp = pprint.PrettyPrinter(width=preferredWidth)
# ic.configureOutput(argToStringFunction=pp.pformat)
# ic.lineWrapWidth = preferredWidth

# ic.disable()

UP = ["7", "F", "|"]
RIGHT = ["7", "J", "-"]
DOWN = ["J", "L", "|"]
LEFT = ["L", "F", "-"]


class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


ALL_DIRECTIONS = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]


class Coordinate:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def move(
        self, network: "Network", direction: Direction, ignore_test_dir: bool = False
    ) -> Self | None:
        test_dir = None
        check = None
        x = self.x
        y = self.y
        match direction:
            case Direction.UP:
                y = y - 1
                test_dir = UP
                check = y < 0
            case Direction.RIGHT:
                x = x + 1
                test_dir = RIGHT
                check = x >= len(network.data[y])
            case Direction.DOWN:
                y = y + 1
                test_dir = DOWN
                check = y >= len(network.data)
            case Direction.LEFT:
                x = x - 1
                test_dir = LEFT
                check = x < 0

        if check or (not ignore_test_dir and network.data[y][x] not in test_dir):
            return None

        return Coordinate(x, y)

    def __eq__(self, other) -> bool:
        if not other:
            return False
        return self.x == other.x and self.y == other.y

    def __repr__(self) -> str:
        return f"{self.x}:{self.y}"

    def __hash__(self) -> int:
        return hash((self.x, self.y))


class Network:
    def __init__(self, network_data: str):
        self.data: list[list[str]] = []
        for line in map(str.strip, network_data.split("\n")):
            if not line.strip():
                continue
            self.data.append(list(line.strip()))

        self.location: Coordinate | None = None
        self.start_location: Coordinate | None = None
        self.last_location: Coordinate | None = None
        for y, v in enumerate(self.data):
            for x, char in enumerate(v):
                if char == "S":
                    self.start_location = Coordinate(x, y)
                    break
            if self.location:
                break

        self.replace_start_with_pipe()

        self.pipe_locations: set[Coordinate] = set()

    def replace_start_with_pipe(self) -> None:
        if not self.start_location:
            return

        directions: set[Direction] = set()
        for direction in ALL_DIRECTIONS:
            if self.start_location.move(self, direction):
                directions.add(direction)

        pipe = "X"
        if directions == {Direction.RIGHT, Direction.DOWN}:
            pipe = "F"
        elif directions == {Direction.RIGHT, Direction.UP}:
            pipe = "L"
        elif directions == {Direction.RIGHT, Direction.LEFT}:
            pipe = "-"
        elif directions == {Direction.UP, Direction.DOWN}:
            pipe = "|"
        elif directions == {Direction.LEFT, Direction.DOWN}:
            pipe = "7"
        elif directions == {Direction.LEFT, Direction.UP}:
            pipe = "J"

        self.data[self.start_location.y][self.start_location.x] = pipe

    def valid_directions(self) -> list[Direction]:
        if not self.location:
            return []

        match self.data[self.location.y][self.location.x]:
            case "F":
                return [Direction.RIGHT, Direction.DOWN]
            case "L":
                return [Direction.UP, Direction.RIGHT]
            case "-":
                return [Direction.LEFT, Direction.RIGHT]
            case "|":
                return [Direction.UP, Direction.DOWN]
            case "7":
                return [Direction.LEFT, Direction.DOWN]
            case "J":
                return [Direction.UP, Direction.LEFT]
            case _:
                return []

    def find_inside(self) -> int:
        if not self.start_location:
            return -1

        # Pipe network is assumed to be a loop, and each pipe in the network has
        # 2 pipes joining it
        # First traverse the pipe
        while self.location != self.start_location:
            if not self.location:
                self.location = self.start_location
                self.last_location = self.location

            self.pipe_locations.add(self.location)

            # Move to the first location we can move to that isn't our previous location
            for direction in self.valid_directions():
                if self.location and not (
                    new_location := self.location.move(self, direction)
                ):
                    continue

                # We can move somewhere, make sure we havent just been there
                if self.last_location and new_location == self.last_location:
                    continue

                self.last_location = self.location
                self.location = new_location
                break

        # Now go through the whole dataset, if we are looking at a piece that's not on
        # the pipe then project it left towards x = 0. If it crosses "-", "J", or "L"
        # add 1 to its count. Odd = inside, Even = Outside
        inside = 0
        # ic(self.pipe_locations)
        for y, row in enumerate(self.data):
            for x, _ in enumerate(row):
                boundary_count = 0
                coordinate: Coordinate | None = Coordinate(x, y)

                # ic(coordinate)

                # Continue if were in the main pipe loop
                if coordinate and coordinate in self.pipe_locations:
                    continue

                while coordinate and (
                    coordinate := coordinate.move(
                        self, Direction.LEFT, ignore_test_dir=True
                    )
                ):
                    if coordinate not in self.pipe_locations:
                        continue

                    pipe = self.data[coordinate.y][coordinate.x]
                    # ic(pipe)
                    if pipe in ["L", "J", "|"]:
                        boundary_count += 1

                if boundary_count % 2 != 0:
                    inside += 1

        return inside

    def _replace_chars(self, char: str) -> str:
        match char:
            case "7":
                return "┓"
            case "J":
                return "┛"
            case "L":
                return "┗"
            case "F":
                return "┏"
            case "|":
                return "┃"
            case "-":
                return "━"
            case ".":
                return "▪"
            case "S":
                return "□"
            case "X":  # Current Location
                return "▽"
            case "M":  # Overlapping Current Location and Start Location
                return "◯"
            case _:
                return "X"

    def __str__(self) -> str:
        chunk = True

        output_data = deepcopy(self.data)

        if (
            self.start_location
            and self.location
            and self.start_location == self.location
        ):
            output_data[self.location.y][self.location.x] = "M"
        else:
            if self.start_location:
                output_data[self.start_location.y][self.start_location.x] = "S"
            if self.location:
                output_data[self.location.y][self.location.x] = "X"

        result = "\n"

        if chunk and (self.location or self.start_location):
            # reduce output to 5x5 grid around our current location
            location = self.location or self.start_location

            if location:
                width = 5
                low_x = max(0, location.x - width)
                high_x = min(len(output_data[0]) - 1, location.x + width)
                low_y = max(0, location.y - width)
                high_y = min(len(output_data) - 1, location.y + width)
                new_output: list[list[str]] = []
                for y in range(low_y, high_y + 1):
                    new_output.append(output_data[y][low_x : high_x + 1])
                output_data = new_output

        for row in output_data:
            result += f"{' '.join(map(self._replace_chars, row))}\n"

        return result


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    with input_path.open() as f:
        network = Network(f.read())

    # print(str(network))

    inside = network.find_inside()
    ic(inside)


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 6: Solution 1")

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
