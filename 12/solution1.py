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
        r: int,
    ) -> int:
        # ic(r)
        permutation_str = "".join(self.data_to_str(data))
        # ic(permutation_str)
        # ic(groups)
        # ic(data_idx)
        # ic(group_idx)

        if data_idx == len(data):
            # ic(permutation_str)
            return 1 if self.is_valid(data) else 0

        # ic(data[data_idx])
        # ic(groups[group_idx])

        x = 0

        if groups[group_idx] == 0:
            if group_idx + 1 == len(groups):
                # Replace any remaining unknowns with operational
                for idx in range(data_idx, len(data)):
                    if data[idx] == Status.UNKNOWN:
                        data[idx] = Status.OPERATIONAL

                return self.permutate(
                    data.copy(), data_idx + 1, groups.copy(), group_idx, r + 1
                )
            else:
                return self.permutate(
                    data.copy(), data_idx, groups.copy(), group_idx + 1, r + 1
                )

        if data[data_idx] == Status.UNKNOWN:
            # Try OPERATIONAL
            data[data_idx] = Status.OPERATIONAL
            x += self.permutate(
                data.copy(), data_idx + 1, groups.copy(), group_idx, r + 1
            )

            # Try DAMAGED
            data[data_idx] = Status.DAMAGED
            groups[group_idx] -= 1
            x += self.permutate(
                data.copy(), data_idx + 1, groups.copy(), group_idx, r + 1
            )
        elif data[data_idx] == Status.DAMAGED:
            groups[group_idx] -= 1
            x += self.permutate(
                data.copy(), data_idx + 1, groups.copy(), group_idx, r + 1
            )
        else:
            # Operational
            x += self.permutate(
                data.copy(), data_idx + 1, groups.copy(), group_idx, r + 1
            )

        return x

    def find_permutations(self) -> int:
        return self.permutate(self.data.copy(), 0, self.groups.copy(), 0, 0)

    def is_valid(self, data: list[Status]):
        # This checks if the data is in a valid state.
        # This also assumes we have removed all Unknowns
        if Status.UNKNOWN in data:
            return False

        groupings = []
        run = 0

        for item in data:
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
            valid_permutation = "".join(self.data_to_str(data))
            # ic(valid_permutation)
        else:
            invalid_permutation = "".join(self.data_to_str(data))
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

    def data_to_str(self, data: list[Status]) -> list[str]:
        result: list[str] = []

        for item in data:
            match item:
                case Status.OPERATIONAL:
                    result.append(".")
                case Status.DAMAGED:
                    result.append("#")
                case Status.UNKNOWN:
                    result.append("?")

        return result

    def __str__(self) -> str:
        return f"Nonogram<data='{''.join(self.data_to_str(self.data))}', groups={self.groups}>"

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

    ic(nonograms)

    all_permutation_counts = [x.find_permutations() for x in nonograms]
    ic(all_permutation_counts)
    ic(sum(all_permutation_counts))

    # ic(list(x.find_permutations() for x in nonograms))
    # ic(nonograms[5].find_permutations())


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 6: Solution 1")

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
