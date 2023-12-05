from pathlib import Path


input_file = Path("input")


data_grid: list[list] = []
part_numbers: dict[int, dict[int, int]] = {}


def find_number_and_idx(grid: list[list], row, col) -> int | None:
    # First lets find the first digit
    # Keep moving left until we can't see a digit
    curr_col = col
    while curr_col - 1 >= 0 and grid[row][curr_col - 1].isnumeric():
        curr_col -= 1

    # Let's make sure we don't currently have the number
    if row in part_numbers and curr_col in part_numbers[row]:
        # If we do, return it
        return None

    number_str = ""
    idx_c = curr_col

    while curr_col < len(grid[row]) and grid[row][curr_col].isnumeric():
        number_str += grid[row][curr_col]
        curr_col += 1

    if row not in part_numbers:
        part_numbers[row] = {}

    value = int(number_str)

    part_numbers[row][idx_c] = value
    print(value)
    return value


def get_part_number(grid: list[list], row, col) -> int | None:
    print(row, col)
    # First we need to check if the coordinates are legal
    if row < 0 or row >= len(grid):
        print("row too high")
        return None

    if col < 0 or col >= len(grid[row]):
        print("col too high")
        return None

    # Check if we are on a number
    value = grid[row][col]
    if not value or not value.isnumeric():
        return None

    return find_number_and_idx(grid, row, col)


# Read in the whole grid first
with input_file.open() as f:
    for line in map(str.strip, f.readlines()):
        data_grid.append([x.replace(".", "") for x in line])

g = data_grid
gear_sum = 0
for row, l in enumerate(data_grid):
    for col, value in enumerate(l):
        if not value:
            continue

        # We have a gear symbol
        if value == "*":
            print("-: ", row, col)
            gear_values: list[int] = []
            # Check each cardinal direction and return a value if we find one
            for d in [
                (row - 1, col),  # N
                (row - 1, col + 1),  # NE
                (row, col + 1),  # E
                (row + 1, col + 1),  # SE
                (row + 1, col),  # S
                (row + 1, col - 1),  # SW
                (row, col - 1),  # W
                (row - 1, col - 1),  # NW
            ]:
                if gear_value := get_part_number(g, *d):
                    gear_values.append(gear_value)

                print(gear_values)

            if len(gear_values) == 2:
                a = gear_values[0]
                b = gear_values[1]
                print(a, b)
                gear_sum += a * b

print(gear_sum)
