import argparse
import re
from pathlib import Path
from typing import Optional, Sequence


class Node:
    def __init__(self, name: str):
        self.name: str = name
        self.left: "Node" | None = None
        self.right: "Node" | None = None

    def __str__(self) -> str:
        left = self.left.name if self.left else "None"
        right = self.right.name if self.right else "None"
        return f"Node<{self.name} : {left} : {right}>"

    def __repr__(self) -> str:
        return self.__str__()


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    instructions: list[str] = []
    endpoints: list[tuple[str, str, str]] = []
    with input_path.open() as f:
        for line in map(str.strip, f.readlines()):
            if not line:
                continue

            # First line is instructions
            if not instructions:
                instructions = list(line)
            else:
                endpoints.append(
                    re.match(r"([A-Z]{3}) = \(([A-Z]{3}), ([A-Z]{3})\)", line).groups()
                )

    # First make empty Nodes for each item
    nodes: dict[str, Node] = {x[0]: Node(x[0]) for x in endpoints}

    # Make the node tree
    for name, left, right in endpoints:
        node = nodes[name]
        node.left = nodes[left]
        node.right = nodes[right]

    idx = 0
    count = 0
    current_node = nodes["AAA"]
    inst_len = len(instructions)

    while current_node.name != "ZZZ":
        instruction = instructions[idx]
        idx = (idx + 1) % inst_len

        print(f"{idx}: {current_node.name} -> {instruction}")

        if instruction == "L":
            if current_node.left:
                current_node = current_node.left
        else:
            if current_node.right:
                current_node = current_node.right

        count += 1

    print(count)


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 6: Solution 1")

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
