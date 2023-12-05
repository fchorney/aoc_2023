import math
import re
from pathlib import Path


input_file = Path("input")

card_re = re.compile(r"Card\s+(?P<card>\d+):(?P<numbers>.*)")

all_points = 0
with input_file.open() as f:
    for line in f.readlines():
        if not (re_res := card_re.search(line)):
            print(f"Can't Parse Line: {line}")
            continue

        if not (card_id := re_res.group("card")):
            print(f"Can't parse card id: {line}")
            continue

        if not (numbers := re_res.group("numbers")):
            print(f"Can't parse numbers: {line}")
            continue

        card_id = int(card_id)

        winners, mine = numbers.split("|")
        winners = list(map(int, re.findall(r"\d+", winners)))

        win_numbers: set[int] = set()
        for number in map(int, re.findall(r"\d+", mine)):
            if number in winners:
                win_numbers.add(number)

        game_points = int(math.pow(2, len(win_numbers) - 1))

        print(f"{line.strip()} = {game_points} => {win_numbers}")

        all_points += game_points

print(all_points)
