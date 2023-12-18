import argparse
import heapq
import sys
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from math import inf
from pathlib import Path
from typing import Optional, Sequence

from icecream import ic


DATA_TYPE = list[list[int]]


class Dir(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    START = 4
    END = 5
    UNKNOWN = 6


def dir_op(d: Dir) -> Dir:
    if d == Dir.UP:
        return Dir.DOWN
    if d == Dir.RIGHT:
        return Dir.LEFT
    if d == Dir.DOWN:
        return Dir.UP
    if d == Dir.LEFT:
        return Dir.RIGHT
    return Dir.UNKNOWN


@dataclass
class Coordinate:
    row: int
    col: int

    def __repr__(self) -> str:
        return f"<{self.row}, {self.col}>"


@dataclass
class Node:
    value: int
    position: Coordinate

    def __repr__(self) -> str:
        return f"Node<{self.value}, {self.position}>"


@dataclass
class State:
    position: Coordinate
    direction: Dir
    heat_loss: int
    advances: dict[Dir, int] = field(default_factory=lambda: defaultdict(int))

    def __hash__(self) -> int:
        return hash((self.position.row, self.position.col, self.direction))

    def __lt__(self, other) -> bool:
        if isinstance(other, State):
            return self.heat_loss < other.heat_loss
        return NotImplemented

    def find_candidates(self, data: DATA_TYPE) -> "list[State]":
        candidates: "list[State]" = []
        for _dir in [Dir.UP, Dir.DOWN, Dir.RIGHT, Dir.LEFT]:
            # Dissalow candidates that would make us move in the same direction 3
            # times
            if _dir in self.advances and self.advances[_dir] == 3:
                continue

            # Can't go back the way we came
            if _dir == dir_op(self.direction):
                continue

            if new_position := self.move(_dir, data):
                state = deepcopy(self)
                state.direction = _dir
                state.heat_loss = (
                    self.heat_loss + data[new_position.row][new_position.col]
                )
                state.position = new_position

                # Delete any advances that aren't in the direction we're going
                for key in [x for x in state.advances.keys() if x != _dir]:
                    if key != _dir:
                        del state.advances[key]
                state.advances[_dir] += 1

                candidates.append(state)

        return candidates

    def move(self, direction: Dir, data: DATA_TYPE) -> Coordinate | None:
        if direction == Dir.UP and self.position.row - 1 >= 0:
            return Coordinate(self.position.row - 1, self.position.col)
        if direction == Dir.DOWN and self.position.row + 1 < len(data):
            return Coordinate(self.position.row + 1, self.position.col)
        if direction == Dir.LEFT and self.position.col - 1 >= 0:
            return Coordinate(self.position.row, self.position.col - 1)
        if direction == Dir.RIGHT and self.position.col + 1 < len(data[0]):
            return Coordinate(self.position.row, self.position.col + 1)
        return None


class LossGraph:
    def __init__(self, data: DATA_TYPE):
        self.data = data
        self.start_coord = Coordinate(0, 0)
        self.goal_coord = Coordinate(len(data) - 1, len(data[0]) - 1)

    def find_goal(self) -> None:
        heat_map: dict[State, int] = {}
        visited: set[State] = set()

        # Define Min Heap Queue
        queue: list[tuple[int, State]] = []

        # Push starting state
        start_state = State(self.start_coord, Dir.START, self.data[0][0])
        heat_map[start_state] = start_state.heat_loss
        heapq.heappush(queue, (start_state.heat_loss, start_state))

        while queue:
            ic(heat_map)
            ic(visited)
            curr_loss, state = heapq.heappop(queue)

            if state.position == self.goal_coord:
                ic("We found the end!")
                return

            if state in visited:
                continue

            visited.add(state)
            ic(curr_loss, state)

            for new_state in state.find_candidates(self.data):
                if heat_map.get(new_state, inf) <= new_state.heat_loss:
                    continue

                ic(new_state)

                heat_map[new_state] = new_state.heat_loss
                heapq.heappush(queue, (new_state.heat_loss, new_state))


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    if pargs.quiet:
        ic.disable()

    data: DATA_TYPE = []
    with input_path.open() as f:
        for line in map(str.strip, f.readlines()):
            data.append(list(map(int, line)))

    ic(data)
    loss_graph = LossGraph(data)

    loss_graph.find_goal()


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    parser.add_argument("-q", "--quiet", action="store_true")

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
