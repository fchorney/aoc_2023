import re
from pathlib import Path


input_file = Path("./input")

mapping = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
}
match_re = re.compile(rf"(?=(\d|{'|'.join(mapping.keys())}))")


def str_to_num(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        pass

    return mapping[value]


cal_value = 0
with input_file.open() as f:
    for line in map(str.strip, f.readlines()):
        results = match_re.findall(line)
        cal_value += str_to_num(results[0]) * 10 + str_to_num(results[-1])

print(cal_value)
