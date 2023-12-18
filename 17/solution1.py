import argparse
import sys
from collections import defaultdict
from enum import Enum
from pathlib import Path
from queue import PriorityQueue
from typing import Optional, Sequence

from icecream import ic


class Dir(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


def dir_op(d: Dir) -> Dir:
    if d == Dir.UP:
        return Dir.DOWN
    if d == Dir.RIGHT:
        return Dir.LEFT
    if d == Dir.DOWN:
        return Dir.UP
    if d == Dir.LEFT:
        return Dir.RIGHT


class Node:
    def __init__(self, value: int, row: int, col: int):
        self.value = value
        self.row = row
        self.col = col
        self._score = sys.maxsize
        self.right: Node | None = None
        self.left: Node | None = None
        self.up: Node | None = None
        self.down: Node | None = None

    def neighbours(self) -> "list[tuple[Node, Dir]]":
        neighbours: "list[tuple[Node, Dir]]" = []
        if self.up:
            neighbours.append((self.up, Dir.UP))
        if self.right:
            neighbours.append((self.right, Dir.RIGHT))
        if self.down:
            neighbours.append((self.down, Dir.DOWN))
        if self.left:
            neighbours.append((self.left, Dir.LEFT))

        return neighbours

    def score(self, goal: "Node", prev_dir: Dir | None = None) -> int:
        # Use Manhatten distance with a D of smallest value of adjacent nodes
        d = sys.maxsize
        for node, node_dir in self.neighbours():
            if prev_dir and node_dir == dir_op(prev_dir):
                # Don't calculate weight of direction we just came from
                continue
            if node.value < d:
                d = node.value
        dx = abs(self.row - goal.row)
        dy = abs(self.col - goal.col)
        self._score = d * (dx + dy)
        return self._score

    def __key(self) -> tuple[int, int, int]:
        return (self.value, self.row, self.col)

    def __hash__(self) -> int:
        return hash(self.__key())

    def __lt__(self, other) -> bool:
        if isinstance(other, Node):
            return self.value < other.value
        return NotImplemented

    def __eq__(self, other) -> bool:
        if isinstance(other, Node):
            return self.__key() == other.__key()
        return NotImplemented

    def __repr__(self) -> str:
        u = self.up.value if self.up else None
        r = self.right.value if self.right else None
        d = self.down.value if self.down else None
        _l = self.left.value if self.left else None

        return (
            f"Node<value={self.value}, loc=[{self.row}, {self.col}] up={u}, right={r}, "
            f"down={d}, left={_l}>"
        )


class LossGraph:
    def __init__(self, data: list[list[Node]]):
        self.start = data[0][0]
        self.goal = data[len(data) - 1][len(data[0]) - 1]

        for row, row_data in enumerate(data):
            for col, node in enumerate(row_data):
                if not node.up and row - 1 >= 0:
                    node.up = data[row - 1][col]
                if not node.right and col + 1 < len(data[0]):
                    node.right = data[row][col + 1]
                if not node.down and row + 1 < len(data):
                    node.down = data[row + 1][col]
                if not node.left and col - 1 >= 0:
                    node.left = data[row][col - 1]

    def reconstruct_path(
        self, came_from: dict[Node, tuple[Node, Dir]], current: Node
    ) -> list[tuple[Node, Dir]]:
        ic("We found the end?!")
        total_path: list[tuple[Node, Dir]] = [(current, Dir.LEFT)]
        while current in came_from:
            current, curr_dir = came_from[current]
            total_path.insert(0, (current, curr_dir))
        total_weight = sum(x[0].value for x in total_path)
        ic(total_path, total_weight)
        return total_path

    def a_star(self):
        start = self.start
        goal = self.goal

        # Set of discovered nodes that may need to be re-expanded
        open_set: PriorityQueue = PriorityQueue()

        # For Node n, came_from[n] is the node immediately preceding it on the cheapest
        # path from the start to currently known.
        came_from: dict[Node, tuple[Node, Dir]] = {}

        # For Node n, g_score[n] is the cost of the cheapest path from start to n
        # currently known.
        g_score: dict[Node, int] = defaultdict(lambda: sys.maxsize)
        g_score[start] = start.value

        # For Node n, f_score[n] = g_score[n] + h(n). f_score[n] represents our current
        # best guess a to how cheap a path could be from the start to finish if it goes
        # through n.
        f_score: dict[Node, int] = defaultdict(lambda: sys.maxsize)
        f_score[start] = start.score(goal)

        # Initially only the start node is known in the open_set
        open_set.put_nowait((f_score[start], start))

        while not open_set.empty():
            # This operation can occur in O(Log(N)) time
            _, current = open_set.get_nowait()

            if current == goal:
                return self.reconstruct_path(came_from, current)

            for neighbour, direction in current.neighbours():
                # d(current, neighbour) is the weight of the edge from current to
                # neighbour.
                # tentative_g_score is the distance from start to the neighbor through
                # current

                # We can't move in the same direction more than 3 times, so if we
                # try to do that, we want to add a huge value to discourage it

                tentative_g_score = g_score[current] + neighbour.value
                if tentative_g_score < g_score[neighbour]:
                    # This path to neighbour is better than any previous one. Record it!
                    came_from[neighbour] = (current, direction)
                    g_score[neighbour] = tentative_g_score
                    f_score[neighbour] = tentative_g_score + neighbour.score(
                        goal, direction
                    )

                    if neighbour not in (obj for p, obj in open_set.queue):
                        open_set.put_nowait((f_score[neighbour], neighbour))

        ic("Open set is empty but goal was never reached")


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    if pargs.quiet:
        ic.disable()

    loss_map: list[list[Node]] = []
    with input_path.open() as f:
        for row, line in enumerate(map(str.strip, f.readlines())):
            loss_row: list[Node] = []
            for col, loss in enumerate(map(int, line)):
                loss_row.append(Node(loss, row, col))
            loss_map.append(loss_row)

    loss_graph = LossGraph(loss_map)
    loss_graph.a_star()


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    parser.add_argument("-q", "--quiet", action="store_true")

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
