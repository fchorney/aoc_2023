import argparse
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from math import prod
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

    def __setitem__(self, key, value):
        if isinstance(value, int):
            setattr(self, key, value)
        return NotImplemented

    def __sub__(self, other) -> "Part":
        if isinstance(other, Part):
            new_part = Part(0, 0, 0, 0)
            for attr in ["x", "m", "a", "s"]:
                a = self[attr]
                b = other[attr]

                if a == 0:
                    a = 1
                if b == 0:
                    b = 1

                new_part[attr] = b - a + 1

            return new_part
        return NotImplemented

    def distinct_combos(self) -> int:
        ic(self)
        return prod([self.x, self.m, self.a, self.s])

    def __str__(self) -> str:
        return f"Part<x={self.x}, m={self.m}, a={self.a}, s={self.s}>"

    def __repr__(self) -> str:
        return self.__str__()


class Rule(ABC):
    @abstractmethod
    def reverse(self) -> "Rule":
        return NotImplemented

    @abstractmethod
    def apply(self, part: Part):
        return NotImplemented

    @property
    @abstractmethod
    def next(self) -> str:
        return NotImplemented


class EndRule(Rule):
    def __init__(self, _next: str):
        self._next = _next

    def reverse(self) -> "EndRule":
        return self

    def apply(self, part: Part):
        pass

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

    def reverse(self) -> "ConditionRule":
        if self.check == "<":
            return ConditionRule(self.var, ">=", self.value, self._next)
        else:
            return ConditionRule(self.var, "<=", self.value, self._next)

    def apply(self, part: Part):
        value = part[self.var]

        if self.check == "<" and value >= self.value:
            part[self.var] = self.value - 1
        elif self.check == ">" and value <= self.value:
            part[self.var] = self.value + 1
        elif self.check == "<=" and value > self.value:
            part[self.var] = self.value
        elif self.check == ">=" and value < self.value:
            part[self.var] = self.value

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
        # First find any workflows that have an "A" condition
        rule_chains = [
            self.reverse_workflow_chains(x, "A")
            for x in self.get_workflows_for_endpoint("A")
        ]
        max_value = 4000

        # Flatten Rule Chains
        flat_chains = [x for y in rule_chains for x in y]

        combo_counts: list[int] = []
        for rule_chain in flat_chains:
            min_part = Part(max_value, max_value, max_value, max_value)
            max_part = Part(0, 0, 0, 0)
            ic(rule_chain)

            for rule in rule_chain:
                ic(rule)
                if hasattr(rule, "check"):
                    if "<" in rule.check:
                        rule.apply(min_part)
                    else:
                        rule.apply(max_part)
            ic(min_part, max_part)
            product = (max_part - min_part).distinct_combos()
            ic(product)
            combo_counts.append(product)
        return sum(combo_counts)

    def adapt_rules(self, workflow_str: str, endpoint: str) -> list[list[Rule]]:
        workflow = self[workflow_str]
        new_rule_chains: list[list[Rule]] = []
        new_rules: list[Rule] = []
        for idx, rule in enumerate(workflow.rules):
            if rule.next == endpoint:
                new_rules.append(rule)

                if idx < len(workflow.rules) - 1:
                    new_rule_chains.append(new_rules)
                    new_rules = new_rules.copy()[:-1] + [rule.reverse()]
                else:
                    break
            else:
                new_rules.append(rule.reverse())

        # If the last rule in the chain doesn't get us to accepted state, don't add it
        if new_rules[-1].next == endpoint:
            new_rule_chains.append(new_rules)
        return new_rule_chains

    def reverse_workflow_chains(
        self, endpoint: str, stoppoint: str
    ) -> list[list[Rule]]:
        if endpoint == "in":
            return self.adapt_rules(endpoint, stoppoint)

        new_rules = self.adapt_rules(endpoint, stoppoint)
        for a_workflow in self.get_workflows_for_endpoint(endpoint):
            new_chain = self.reverse_workflow_chains(a_workflow, endpoint)
            for idx, rule in enumerate(new_rules):
                chain_combo: list[Rule] = []
                for chain in new_chain:
                    chain_combo += chain
                new_rules[idx] = chain_combo + rule
        return new_rules

    def get_workflows_for_endpoint(self, endpoint: str) -> list[str]:
        workflow_names: list[str] = []
        for name, workflow in self.workflows.items():
            for rule in workflow.rules:
                if rule.next == endpoint:
                    workflow_names.append(name)
                    break
        return workflow_names

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
    total_combos = system.run()
    ic(total_combos)
    print(total_combos)

    return total_combos


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    parser.add_argument("-q", "--quiet", action="store_true")

    return parser.parse_args(args)


if __name__ == "__main__":
    assert main(["testinput1", "-q"]) == 167409079868000
    assert main(["input", "-q"]) == 116738260946855
