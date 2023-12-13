import argparse
from pathlib import Path
from typing import Optional, Sequence

from icecream import ic


def check_mirror(area: list[str]) -> int:
    # First find any rows beside eachother that are the same
    pairs: list[tuple[int, int]] = []

    for idx in range(a_len := len(area)):
        if idx + 1 == a_len:
            break

        if area[idx] == area[idx + 1]:
            pairs.append((idx, idx + 1))

    ic(pairs)

    offsets: list[int] = []
    for r1, r2 in pairs:
        offset = 0

        while True:
            offset += 1
            r1o = r1 - offset
            r2o = r2 + offset

            if r1o < 0:
                r1o += 1
                break

            if r2o == a_len:
                r2o -= 1
                break

            if area[r1o] != area[r2o]:
                r1o += 1
                r2o -= 1
                break

        ic(r1o, r2o, a_len)

        if r1o == 0 or r2o == a_len - 1:
            ic(r1, r2, offset)

            offsets.append(r1 + 1)

    ic(offsets)

    return max(offsets or [0])


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    # Parse All Areas
    areas: list[list[str]] = []
    with input_path.open() as f:
        area: list[str] = []
        for line in map(str.strip, f.readlines()):
            if not line:
                areas.append(area)
                area = []
                continue
            area.append(line)
        areas.append(area)

    # Generate the transpose of all areas
    t_areas: list[list[str]] = []
    for area in areas:
        t_areas.append(["".join(x) for x in zip(*area)])
    ic(t_areas)

    result = 0
    for idx in range(len(areas)):
        ic(areas[idx])
        print("Rows")
        row_max = check_mirror(areas[idx])
        print("Cols")
        col_max = check_mirror(t_areas[idx])
        print()

        if col_max > row_max:
            result += col_max
        else:
            result += row_max * 100

        print("Results")
        ic(idx, row_max, col_max)
        print()
    ic(result)


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 6: Solution 1")

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
