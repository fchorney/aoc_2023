import argparse
import math
import re
import time
from copy import deepcopy
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from pathlib import Path
from typing import Optional, Sequence

from icecream import ic

INPUT_RE = re.compile(r"((?P<type>[%&]?)(?P<name>[a-z]+)) -> (?P<outputs>(?:[a-z]+(?:, )?)+)")

class Status(Enum):
    OFF = 1
    ON = 2

class Pulse(Enum):
    LOW = 1
    HIGH = 2

@dataclass
class Packet:
    sender: str
    pulse: Pulse
    recipient: str

class Module():
    def __init__(self, name: str, outputs: list[str]):
        self.name: str = name
        self.outputs: list[str] = outputs

    def pulse(self, packet: Packet) -> list[Packet]:
        return NotImplemented

    def __hash__(self) -> int:
        return NotImplemented

    def _make_pulses(self, pulse: Pulse) -> list[Packet]:
        return [Packet(self.name, pulse, name) for name in self.outputs]

class FlipFlop(Module):
    def __init__(self, name: str, outputs: list[str]):
        super(FlipFlop, self).__init__(name, outputs)

        # Default status to OFF
        self.status: Status = Status.OFF

    def pulse(self, packet: Packet) -> list[Packet]:
        # If a FlipFlop receives a HIGH pulse, it is ignored and nothing happens
        if packet.pulse == Pulse.HIGH:
            return []

        # Flip Status
        self.status = Status.OFF if self.status == Status.ON else Status.ON

        # Send pulse matching status
        return self._make_pulses(Pulse.HIGH if self.status == Status.ON else Pulse.LOW)

    def __hash__(self) -> int:
        return hash((self.name, tuple(self.outputs), self.status))

    def __repr__(self) -> str:
        return f"%{self.name} -> {', '.join(self.outputs)}"

class Conjunction(Module):
    def __init__(self, name: str, outputs: list[str]):
        super(Conjunction, self).__init__(name, outputs)

        # Keep a memory of last Pulse for all inputs
        # Remember: The default is a LOW pulse
        self.inputs: dict[str, Pulse] = {}

    def pulse(self, packet: Packet) -> list[Packet]:
        # Update input pulse
        self.inputs[packet.sender] = packet.pulse

        # Send a LOW pulse if all inputs are set to HIGH, else send a HIGH pulse
        return self._make_pulses(Pulse.LOW if all(x == Pulse.HIGH for x in self.inputs.values()) else Pulse.HIGH)

    def __hash__(self) -> int:
        return hash((self.name, tuple(self.outputs), tuple((x, y) for x, y in self.inputs.items())))

    def __repr__(self) -> str:
        return f"&{self.name} [{', '.join(self.inputs.keys())}] -> {', '.join(self.outputs)}"

class Broadcast(Module):
    def pulse(self, packet: Packet) -> list[Packet]:
        return self._make_pulses(packet.pulse)

    def __hash__(self) -> int:
        return hash((self.name, tuple(self.outputs)))

    def __repr__(self) -> str:
        return f"{self.name} -> {', '.join(self.outputs)}"

class Output(Module):
    def pulse(self, packet: Packet) -> list[Packet]:
        return []

    def __hash__(self) -> int:
        return hash((self.name, tuple(self.outputs)))

    def __repr__(self) -> str:
        return f"{self.name} -> None"

class Machine():
    def __init__(self, modules: dict[str, Module]):
        self.modules = modules
        self.stack: list[Packet] = []

        self.populate_conjunction_modules()
        self.populate_empty_outputs()

        rx_parent: Conjunction = [
            x for x in self.modules.values() if "rx" in x.outputs and isinstance(x, Conjunction)
        ][0]

        # {module_name: {"hash": original_hash, "count": current_count}}
        self.rx_inputs: dict[str, dict] = {}
        for input in rx_parent.inputs.keys():
            self.rx_inputs[input] = {"hash": hash(self.modules[input]), "count": 0, "cycled": False}

        self.module_hash = self.hash_modules()
        ic(self.module_hash)

    def hash_modules(self) -> int:
        return hash(tuple((x, y) for x, y in self.modules.items()))

    def populate_conjunction_modules(self) -> None:
        # First get the list of all Conjunction Modules
        for conj_module in filter(lambda x: isinstance(x, Conjunction), self.modules.values()):
            # For each conjunction module, find all other modules that output to it
            for input in list(filter(lambda x: conj_module.name in x.outputs, self.modules.values())):
                conj_module.inputs[input.name] = Pulse.LOW

    def populate_empty_outputs(self) -> None:
        # Grab a list of all inputs
        inputs = set(x for x in self.modules.keys() if x != "broadcaster")
        outputs = set(x for y in self.modules.values() for x in y.outputs)

        for output in outputs - inputs:
            self.modules[output] = Output(output, [])

    def run(self, count: int = 1) -> int:
        total_high_count: int = 0
        total_low_count: int = 0
        loops: int = 0
        for _ in range(count):
            high_count = low_count = 0
            self.stack = [Packet("button", Pulse.LOW, "broadcaster")]
            while self.stack:
                packet = self.stack.pop(0)

                if packet.sender in self.rx_inputs and not self.rx_inputs[packet.sender]["cycled"]:
                    if packet.pulse == Pulse.HIGH:
                        self.rx_inputs[packet.sender]["cycled"] = True
                        self.rx_inputs[packet.sender]['count'] = loops

                if all(x["cycled"] for x in self.rx_inputs.values()):
                    x = math.lcm(*list(x["count"] + 1 for x in self.rx_inputs.values()))
                    return x

                if packet.pulse == Pulse.HIGH:
                    high_count += 1
                else:
                    low_count += 1

                ic(packet)
                self.stack.extend(self.modules[packet.recipient].pulse(packet))
            ic(high_count, low_count)
            total_high_count += high_count
            total_low_count += low_count
            loops += 1
            ic(loops, total_high_count, total_low_count)

        print(self.rx_inputs)

        return total_high_count * total_low_count

    def __repr__(self) -> str:
        return f"Machine<modules=\n{self.modules}\nstack=\n{self.stack}>"

def main(args: Optional[Sequence[str]] = None) -> int:
    pargs = parse_args(args)
    input_path = pargs.input_path

    if pargs.quiet:
        ic.disable()

    modules: dict[str, Module] = {}
    with input_path.open() as f:
        for line in map(str.strip, f.readlines()):
            if not (match := INPUT_RE.match(line)):
                print(f"Could not parse line: `{line}`")
                return -1

            module_type = Broadcast
            if type := match.group("type"):
                if type == "%":
                    module_type = FlipFlop
                if type == "&":
                    module_type = Conjunction

            outputs = list(map(str.strip, match.group('outputs').split(",")))
            name = match.group("name")
            modules[name] = module_type(name, outputs)

    machine = Machine(modules)

    ic(machine)
    pulse_product = machine.run(100000)
    ic(pulse_product)
    print(pulse_product)
    return pulse_product

def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    parser.add_argument("-q", "--quiet", action="store_true")

    return parser.parse_args(args)


if __name__ == "__main__":
    start = time.monotonic()
    assert main(["input", "-q"]) == 243566897206981
    print(f"input: {timedelta(seconds=time.monotonic() - start)}")
