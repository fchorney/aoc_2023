import argparse
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence

from icecream import ic


@dataclass
class Part:
    x: int
    m: int
    a: int
    s: int

    def total(self) -> int:
        return sum([self.x, self.m, self.a, self.s])

    def __getitem__(self, key: str) -> int:
        return {"x": self.x, "m": self.m, "a": self.a, "s": self.s}[key]

    def __str__(self) -> str:
        return f"Part<x={self.x}, m={self.m}, a={self.a}, s={self.s}>"

    def __repr__(self) -> str:
        return self.__str__()


class Rule(ABC):
    @abstractmethod
    def satisfied(self, part: Part) -> bool:
        return NotImplemented

    @property
    @abstractmethod
    def next(self) -> str:
        return NotImplemented


class EndRule(Rule):
    def __init__(self, _next: str):
        self._next = _next

    def satisfied(self, part: Part) -> bool:
        return True

    @property
    def next(self) -> str:
        return self._next

    def __str__(self) -> str:
        return f"Rule<{self.__repr__()}>"

    def __repr__(self) -> str:
        return self.next


class ConditionRule(Rule):
    def __init__(self, var: str, check: str, value: int, _next: str):
        self.var = var
        self.check = check
        self.value = value
        self._next = _next

    def satisfied(self, part: Part) -> bool:
        if self.check == "<":
            return part[self.var] < self.value
        else:
            return part[self.var] > self.value

    @property
    def next(self) -> str:
        return self._next

    def __str__(self) -> str:
        return f"Rule<{self.__repr__()}>"

    def __repr__(self) -> str:
        return f"{self.var}{self.check}{self.value} -> {self.next}"


@dataclass
class Workflow:
    name: str
    rules: list[Rule] = field(default_factory=list)

    def __str__(self) -> str:
        return f"<Workflow<{self.name} -> {self.rules}>"


@dataclass
class System:
    workflows: dict[str, Workflow] = field(default_factory=dict)
    parts: list[Part] = field(default_factory=list)
    accepted: list[Part] = field(default_factory=list)
    rejected: list[Part] = field(default_factory=list)

    def run(self):
        for part in self.parts:
            # Always start with the `in` workflow
            workflow = self["in"]

            while workflow.name not in ["A", "R"]:
                for rule in workflow.rules:
                    if rule.satisfied(part):
                        workflow = self[rule.next]
                        break

            if workflow.name == "A":
                self.accepted.append(part)
            else:
                self.rejected.append(part)

    def __getitem__(self, key) -> Workflow:
        return self.workflows[key]

    def __setitem__(self, key, new_value):
        if isinstance(new_value, Workflow):
            self.workflows[key] = new_value
        return NotImplemented

    def __str__(self) -> str:
        return f"System<workflows:{self.workflows}, parts:{self.parts}>"

    def __repr__(self) -> str:
        return self.__str__()


WORKFLOW_RE = re.compile(
    r"(?P<name>[a-z]+){(?P<rules>(?:[xmas][<>]\d+:[a-zAR]+,)+)(?P<next>[a-zAR]+)}"
)
RULE_RE = re.compile(r"(?P<var>[xmas])(?P<check>[<>])(?P<value>\d+):(?P<next>[a-zAR]+)")
PARTS_RE = re.compile(r"{x=(\d+),m=(\d+),a=(\d+),s=(\d+)}")


def main(args: Optional[Sequence[str]] = None) -> int:
    pargs = parse_args(args)
    input_path = pargs.input_path

    if pargs.quiet:
        ic.disable()

    # Initialize system with special accept and reject workflows
    system = System()
    system["A"] = Workflow("A")
    system["R"] = Workflow("R")

    with input_path.open() as f:
        for line in map(str.strip, f.readlines()):
            if not line:
                continue

            if not line.startswith("{"):
                # Parse workflows
                if not (matches := WORKFLOW_RE.match(line)):
                    print(f"Could Not Parse Line: `{line}`")
                    return -1

                workflow = Workflow(matches.group("name"))
                e_next = EndRule(matches.group("next"))

                for rule_str in map(str.strip, matches.group("rules").split(",")):
                    if not rule_str:
                        continue

                    if not (matches := RULE_RE.match(rule_str)):
                        print(f"Could not Parse Rule: `{rule_str}`")
                        return -1
                    var = matches.group("var")
                    check = matches.group("check")
                    value = int(matches.group("value"))
                    r_next = matches.group("next")

                    workflow.rules.append(ConditionRule(var, check, value, r_next))
                # End rule needs to come last
                workflow.rules.append(e_next)
                system[workflow.name] = workflow
            else:
                # Parse Parts
                if not (matches := PARTS_RE.match(line)):
                    print(f"Could not PArse Part Line: `{line}`")
                    return -1

                part = Part(*list(map(int, matches.groups())))
                system.parts.append(part)

    ic(system)
    system.run()

    ic(system.accepted)
    ic([x.total() for x in system.accepted])
    total = sum(x.total() for x in system.accepted)
    ic(total)
    print(total)

    return total


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    parser.add_argument("-q", "--quiet", action="store_true")

    return parser.parse_args(args)


if __name__ == "__main__":
    assert main(["testinput1", "-q"]) == 19114
    assert main(["input", "-q"]) == 472630
