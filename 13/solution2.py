import argparse
from collections import defaultdict
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

    res = [x for x in offsets if x]
    return res[0] if res else 0


def find_smudge_candidates(area: list[str]) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []

    # I'm pretty sure areas are guaranteed to have an odd number of rows
    for anchor in range(a_len := (len(area))):
        for idx in range(anchor + 1, a_len):
            if sum(1 for a, b in zip(area[anchor], area[idx]) if a != b) == 1:
                pairs.append((anchor, idx))

    # This is so gross lol
    return list(map(tuple, set(map(tuple, map(sorted, pairs)))))


def fix_smudges(area: list[str], candidates: list[tuple[int, int]]) -> list[list[str]]:
    fixed_mirrors: list[list[str]] = []
    for r1, r2 in candidates:
        for idx in range(len(area[r1])):
            if (x1 := area[r1][idx]) != (x2 := area[r2][idx]):
                new_area = area.copy()
                new_area[r1] = (
                    area[r1][:idx] + ("." if x1 == "#" else "#") + area[r1][idx + 1 :]
                )
                fixed_mirrors.append(new_area)

                # new_area = area.copy()
                # new_area[r2] = (
                #    area[r2][:idx] + ("." if x2 == "#" else "#") + area[r2][idx + 1 :]
                # )
                # fixed_mirrors.append(new_area)

    return fixed_mirrors


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

    fixed_areas: dict[int, list[list[str]]] = defaultdict(list)
    for idx, area in enumerate(areas):
        ic(area)
        candidates = find_smudge_candidates(area)
        ic(candidates)
        fixed_areas[idx].extend(fix_smudges(area, candidates))

    ic(fixed_areas)

    # Generate the transpose of all areas
    t_areas: list[list[str]] = []
    for area in areas:
        t_areas.append(["".join(x) for x in zip(*area)])

    fixed_t_areas: dict[int, list[list[str]]] = defaultdict(list)
    for idx in fixed_areas.keys():
        for area in fixed_areas[idx]:
            fixed_t_areas[idx].append(["".join(x) for x in zip(*area)])

    # for idx, area in enumerate(t_areas):
    #    ic(area)
    #    candidates = find_smudge_candidates(area)
    #    ic(candidates)
    #    fixed_t_areas[idx].extend(fix_smudges(area, candidates))

    ic(fixed_t_areas)

    result = 0
    for idx in range(len(areas)):
        ic(areas[idx])
        print("Rows")
        # row_max = check_mirror(areas[idx])
        row_max = 0

        # Check all smudge fixed rows
        fixed_areas_max: list[int] = []
        for fixed_area in fixed_areas[idx]:
            ic(fixed_area)
            fixed_areas_max.append(check_mirror(fixed_area))

        ic(fixed_areas_max)
        rm = [x for x in fixed_areas_max if x]
        row_max = rm[0] if rm else 0

        print("Cols")
        # col_max = check_mirror(t_areas[idx])
        col_max = 0
        print()

        if row_max == 0:
            # Check all smudge fixed cols
            fixed_t_areas_max: list[int] = []
            for fixed_area in fixed_t_areas[idx]:
                ic(fixed_area)
                fixed_t_areas_max.append(check_mirror(fixed_area))

            ic(fixed_t_areas_max)
            cm = [x for x in fixed_t_areas_max if x]
            col_max = cm[0] if cm else 0

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
