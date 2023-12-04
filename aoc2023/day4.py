"""Day N."""

import re
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day4')

def part1(data: str) -> int:
    total = 0
    for card in data.splitlines():
        numbers = card.split(':', 1)[1]
        winning, yours = numbers.split('|')
        you_win = set(winning.split()).intersection(yours.split())
        if you_win:
            total += 2**(len(you_win)-1)
    return total

def part2(data: str) -> int:
    cards = data.splitlines()
    n_winning = [0]*len(cards)
    for card_idx, card in enumerate(cards):
        numbers = card.split(':', 1)[1]
        winning, yours = numbers.split('|')
        you_win = set(winning.split()).intersection(yours.split())
        n_winning[card_idx] = len(you_win)

    n_cards = [1]*len(cards)
    for card_idx, n_wins in enumerate(n_winning):
        for _ in range(n_cards[card_idx]):
            for idx in range(card_idx+1, card_idx+n_wins+1):
                n_cards[idx] += 1

    return sum(n_cards)


if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
