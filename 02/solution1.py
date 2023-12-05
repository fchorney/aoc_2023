import re
from pathlib import Path


RED = 12
GREEN = 13
BLUE = 14

input_file = Path("input")

game_re = re.compile(r"Game (?P<game>\d*):(?P<data>.*)")
item_re = re.compile(r"(?P<count>\d*) (?P<color>blue|red|green)")

game_sum = 0

with input_file.open() as f:
    for line in map(str.strip, f.readlines()):
        if not (values := game_re.search(line)):
            print("can't parse game")
            continue
        if not (game_id := values.group("game")):
            print("no game id")
            continue
        if not (items := values.group("data")):
            print("no items")
            continue

        game_id = int(game_id)

        valid = True
        for idx, section in enumerate(items.split(";"), 1):
            if not valid:
                break

            green = red = blue = 0
            for item in map(str.strip, section.split(",")):
                if not (values := item_re.search(item)):
                    print("Can't parse item")
                    continue
                if not (count := values.group("count")):
                    print("No Count")
                    continue
                if not (color := values.group("color")):
                    print("No Color")
                    continue

                count = int(count)
                match color.lower():
                    case "red":
                        red += count
                    case "blue":
                        blue += count
                    case "green":
                        green += count

            if green > GREEN or blue > BLUE or red > RED:
                valid = False
                continue

        if valid:
            game_sum += game_id

print(game_sum)
