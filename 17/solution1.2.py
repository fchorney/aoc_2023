import argparse
from heapq import heappop, heappush
from math import inf
from pathlib import Path
from typing import Optional, Sequence

from icecream import ic


LEGAL_MOVES = {
    (0, 0): ((1, 0), (0, 1)),  # Start -> Right, Down
    (0, -1): ((1, 0), (-1, 0)),  # ??? -> Right, Left
    (1, 0): ((0, -1), (0, 1)),  # ??? -> Up, Down
    (0, 1): ((1, 0), (-1, 0)),  # ??? -> Right, Left
    (-1, 0): ((0, -1), (0, 1)),  # ??? -> Up, Down
}


def find_loss(grid: list[list[int]], mmax: int) -> int:
    destination_coord = (len(grid[0]) - 1, len(grid) - 1)
    # Heat Loss, Coordinate, Direction
    heap = [(0, (0, 0), (0, 0))]
    # TODO: Figure out what this means
    heat_map = {(0, 0): 0}
    visited = set()

    while heap:
        heat_loss, coord, direction = heappop(heap)

        if coord == destination_coord:
            break

        if (coord, direction) in visited:
            continue

        visited.add((coord, direction))

        for new_direction in LEGAL_MOVES[direction]:
            new_heat_loss = heat_loss
            for steps in range(1, mmax + 1):
                # Find new possible coordinate
                new_coord = (
                    coord[0] + steps * new_direction[0],
                    coord[1] + steps * new_direction[1],
                )

                # If we're out of bounds, continue
                if (
                    new_coord[0] < 0
                    or new_coord[1] < 0
                    or new_coord[0] > destination_coord[0]
                    or new_coord[1] > destination_coord[1]
                ):
                    continue

                new_heat_loss += grid[new_coord[1]][new_coord[0]]
                new_node = (new_coord, new_direction)

                if heat_map.get(new_node, inf) <= new_heat_loss:
                    continue

                heat_map[new_node] = new_heat_loss
                heappush(heap, (new_heat_loss, new_coord, new_direction))

    return heat_loss


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    if pargs.quiet:
        ic.disable()

    grid: list[list[int]] = []
    with input_path.open() as f:
        for line in map(str.strip, f.readlines()):
            grid.append(list(map(int, line)))

    ic(grid)

    heat_loss = find_loss(grid, 3)
    ic(heat_loss)
    print(heat_loss)


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    parser.add_argument("-q", "--quiet", action="store_true")

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
