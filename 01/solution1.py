import re
from pathlib import Path


input_file = Path("./input")


cal_value = 0
with input_file.open() as f:
    for line in map(str.strip, f.readlines()):
        results = list(map(int, re.findall(r"\d", line)))
        cal_value += results[0] * 10 + results[-1]

print(cal_value)
