import argparse
from collections import defaultdict
from pathlib import Path
from typing import Optional, Sequence

from icecream import ic


CARD_RANK = {
    "2": 1,
    "3": 2,
    "4": 3,
    "5": 4,
    "6": 5,
    "7": 6,
    "8": 7,
    "9": 8,
    "T": 9,
    "J": 10,
    "Q": 11,
    "K": 12,
    "A": 13,
}


class Card:
    def __init__(self, card: str):
        self.value = card
        self.rank = CARD_RANK[card]

    def __str__(self) -> str:
        return f"Card<{self.value} : {self.rank}>"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        return self.rank == other.rank

    def __lt__(self, other) -> bool:
        return self.rank < other.rank


class Hand:
    def __init__(self, data: str):
        _cards, _bid = data.split(" ")
        self.cards: list[Card] = [Card(x) for x in _cards]
        self.bid: int = int(_bid)
        self.strength: int = self._determine_strength()

    def __str__(self) -> str:
        return (
            f"Hand<{''.join([x.value for x in self.cards])} : "
            f"{self.strength} : {self.bid}>"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def _determine_strength(self) -> int:
        counts: dict[str, int] = defaultdict(int)
        for card in self.cards:
            counts[card.value] += 1

        strength = -1
        values = sorted(counts.values())
        match len(counts):
            case 1:
                # 5 of a kind
                strength = 6
            case 2:
                if values == [1, 4]:
                    # 4 of a kind
                    strength = 5
                else:
                    # full house
                    strength = 4
            case 3:
                if values == [1, 1, 3]:
                    # 3 of a kind
                    strength = 3
                else:
                    # 2 pair
                    strength = 2
            case 4:
                # pair
                strength = 1
            case 5:
                # High card
                strength = 0
            case _:
                # Default case, we shouldn't hit this
                raise Exception("Why are you running?")

        return strength

    def __lt__(self, other) -> bool:
        if self.strength == other.strength:
            # Determine what is better if the strength is the same
            # Cycle through the cards, to determine which one has a higher rank
            for i in range(0, len(self.cards)):
                if self.cards[i] == other.cards[i]:
                    continue
                return self.cards[i] < other.cards[i]
        return self.strength < other.strength


def main(args: Optional[Sequence[str]] = None) -> None:
    pargs = parse_args(args)
    input_path = pargs.input_path

    hands: list[Hand] = []
    with input_path.open() as f:
        for line in map(str.strip, f.readlines()):
            hands.append(Hand(line))

    ranked_hands = sorted(hands)
    winnings = sum(i * x.bid for i, x in enumerate(ranked_hands, 1))

    print(winnings)


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Day 6: Solution 1")

    parser.add_argument("input_path", type=lambda p: Path(p).absolute())

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
