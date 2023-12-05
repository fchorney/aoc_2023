import re
from pathlib import Path


input_file = Path("input")

card_re = re.compile(r"Card\s+(?P<card>\d+):(?P<numbers>.*)")

scratchers: dict[int, list[list[int] | int]] = {}

all_scratchers = 0
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
        mine = list(map(int, re.findall(r"\d+", mine)))

        scratchers[card_id] = [winners, mine, 1]


def get_win_count(winners, mine) -> int:
    result: set[int] = set()
    for number in mine:
        if number in winners:
            result.add(number)
    return len(result)


for card, values in scratchers.items():
    winners, mine, count = values
    win_count = get_win_count(winners, mine)

    for extra_card in range(card + 1, card + win_count + 1):
        scratchers[extra_card][2] += count

print(sum([x[2] for x in scratchers.values()]))
