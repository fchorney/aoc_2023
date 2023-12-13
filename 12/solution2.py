import argparse
from enum import Enum
from pathlib import Path
from typing import Optional, Sequence

from icecream import ic


class Status(Enum):
    OPERATIONAL = 0
    DAMAGED = 1
    UNKNOWN = 2


class Nonogram:
    def __init__(self, data: list[str], groups: list[int]):
        self.data = self.data_to_status(data)
        self.groups = groups

    def permutate(
        self,
        data: list[Status],
        data_idx: int,
        groups: list[int],
        group_idx: int,
    ) -> int:
        # ic(r)
        # permutation_str = self.data_to_str(data)
        # ic(permutation_str)
        # ic(groups)
        # ic(data_idx)
        # ic(group_idx)

        if data_idx == len(data) or group_idx == len(groups):
            # ic(permutation_str)
            return 1 if self.is_valid(data) else 0

        # ic(data[data_idx])
        # ic(groups[group_idx])

        x = 0

        if groups[group_idx] == 0:
            return self.permutate(data.copy(), data_idx, groups.copy(), group_idx + 1)

        if data[data_idx] == Status.UNKNOWN:
            # Try OPERATIONAL
            data[data_idx] = Status.OPERATIONAL
            x += self.permutate(data.copy(), data_idx + 1, groups.copy(), group_idx)

            # Try DAMAGED
            data[data_idx] = Status.DAMAGED
            groups[group_idx] -= 1
            x += self.permutate(data.copy(), data_idx + 1, groups.copy(), group_idx)
        elif data[data_idx] == Status.DAMAGED:
            groups[group_idx] -= 1
            x += self.permutate(data.copy(), data_idx + 1, groups.copy(), group_idx)
        else:
            # Operational
            x += self.permutate(data.copy(), data_idx + 1, groups.copy(), group_idx)

        return x

    def find_permutations(self) -> int:
        return self.permutate(self.data.copy(), 0, self.groups.copy(), 0)

    def iterative_find_permutations(self) -> int:
        # ic(self.data_to_str(self.data))
        all_data = [self.data.copy()]

        b = True
        while b:
            # ic([self.data_to_str(x) for x in all_data])
            data = all_data.pop(0)
            for idx, item in enumerate(data):
                if item in [Status.OPERATIONAL, Status.DAMAGED]:
                    continue

                op = data.copy()
                op[idx] = Status.OPERATIONAL
                all_data.append(op)
                dm = data.copy()
                dm[idx] = Status.DAMAGED
                all_data.append(dm)
                break
            else:
                all_data.append(data.copy())
                b = False

        x = 0
        for data in all_data:
            valid = self.is_valid_ex(data, self.groups)
            x += 1 if valid else 0

            # if valid:
            #    ic(self.data_to_str(data))

        return x

    def is_valid_ex(self, data: list[Status], groups: list[int]):
        idx = 0
        counting = False
        count = 0
        group_len = len(groups)

        # Add a '.' to the end so we don't need end checks
        data = data.copy()
        data.append(Status.OPERATIONAL)

        for item in data:
            if item == Status.DAMAGED:
                counting = True
                count += 1

                # Went through groups, but found more Damaged or count is too high
                if idx == group_len or count > groups[idx]:
                    return False
            else:
                if not counting:
                    continue

                # Count is wrong
                if count != groups[idx]:
                    return False

                counting = False
                count = 0
                idx += 1

        # Only valid if weve gone through all our groups
        return idx == group_len

    def is_valid(self, data: list[Status]):
        # This checks if the data is in a valid state.
        # This also assumes we have removed all Unknowns or any remaining unknowns would
        # be operational

        groupings = []
        run = 0

        for item in data:
            if item == Status.UNKNOWN:
                continue

            if item == Status.DAMAGED:
                run += 1

            if item == Status.OPERATIONAL:
                if run > 0:
                    groupings.append(run)
                run = 0

        # If a run ends at the end of the list it won't have been added to the
        # groupings yet
        if run > 0:
            groupings.append(run)

        result = groupings == self.groups
        if result:
            valid_permutation = self.data_to_str(data)
            # ic(valid_permutation)
        else:
            invalid_permutation = self.data_to_str(data)
            # ic(invalid_permutation)

        return result

    def data_to_status(self, data: list[str]) -> list[Status]:
        result: list[Status] = []

        for item in data:
            match item:
                case ".":
                    result.append(Status.OPERATIONAL)
                case "#":
                    result.append(Status.DAMAGED)
                case "?":
                    result.append(Status.UNKNOWN)

        return result

    def data_to_str(self, data: list[Status]) -> str:
        result: list[str] = []

        for item in data:
            match item:
                case Status.OPERATIONAL:
                    result.append(".")
                case Status.DAMAGED:
                    result.append("#")
                case Status.UNKNOWN:
                    result.append("?")

        return "".join(result)

    def __str__(self) -> str:
        return f"Nonogram<data='{self.data_to_str(self.data)}', groups={self.groups}>"

    def __repr__(self) -> str:
        return self.__str__()


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    nonograms: list[Nonogram] = []
    with input_path.open() as f:
        for line in map(str.strip, f.readlines()):
            data, groups = line.split(" ")
            nonograms.append(Nonogram(list(data), list(map(int, groups.split(",")))))

            # nonograms.append(
            #    Nonogram(
            #        "?".join(x for x in [data] for _ in range(5)),
            #        list(map(int, groups.split(","))) * 5,
            #    )
            # )

    ic(nonograms)

    result = sum(x.iterative_find_permutations() for x in nonograms)
    ic(result)


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 6: Solution 1")

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
