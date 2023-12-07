"""Day N."""

from functools import partial
from pprint import pprint
from pathlib import Path

HERE = Path(__file__).parent
INPUTS_DIR = Path(HERE.parent, 'inputs')
INPUT_FILE = Path(INPUTS_DIR, 'day7')


TYPES = {
    0: "High card",
    1: "One pair",
    2: "Two pair",
    3: "Three of a kind",
    4: "Full house",
    5: "Four of a kind",
    6: "Five of a kind"
}

# For translating to base 14.
CARD_RANK = {
    "A": "d",
    "K": "c",
    "Q": "b",
    "J": "a",
    "T": "9",
    "9": "8",
    "8": "7",
    "7": "6",
    "6": "5",
    "5": "4",
    "4": "3",
    "3": "2",
    "2": "1",
    "1": "0",
}

CARD_RANK_JOKERS = {
    "A": "d",
    "K": "c",
    "Q": "b",
    "T": "a",
    "9": "9",
    "8": "8",
    "7": "7",
    "6": "6",
    "5": "5",
    "4": "4",
    "3": "3",
    "2": "2",
    "1": "1",
    "J": "0",
}


def part1(data: str) -> int:
    hands = data.splitlines()
    # List of lists, one list for each type, in order.
    hand_types = [[], [], [], [], [], [], []]
    for hand in hands:
        cards_in_hand = hand.split()[0]
        hand_type = check_type(cards_in_hand)
        hand_types[hand_type].append(hand)
    # pprint(hand_types)
    # [weakest...strongest]
    ranked_hands = []
    for hand_type in hand_types:
        ranked_hands.extend(rank_of_same_type(hand_type))
    # pprint(ranked_hands)
    total = 0
    for rank, hand in enumerate(ranked_hands):
        bid = int(hand.split()[1])
        total += bid * (rank+1)

    return total


def part2(data: str) -> int:
    # 253483637 is too low
    hands = data.splitlines()
    # List of lists, one list for each type, in order.
    hand_types = [[], [], [], [], [], [], []]
    for hand in hands:
        cards_in_hand = hand.split()[0]
        hand_type = check_type(cards_in_hand, is_jokers=True)
        hand_types[hand_type].append(hand)
    # pprint(hand_types)
    # [weakest...strongest]
    ranked_hands = []
    for hand_type in hand_types:
        ranked_hands.extend(rank_of_same_type(hand_type, is_jokers=True))
    pprint(ranked_hands)
    total = 0
    for rank, hand in enumerate(ranked_hands):
        bid = int(hand.split()[1])
        total += bid * (rank+1)

    return total


def rank_of_same_type(hands: list[str], is_jokers: bool = False) -> list[str]:
    """Return list sorted [weakest...strongest]"""
    if is_jokers:
        key = partial(convert_hand_to_number_for_comparison, is_jokers=True)
        return sorted(hands, key=key)
    return sorted(hands, key=convert_hand_to_number_for_comparison)


def convert_hand_to_number_for_comparison(hand: str, is_jokers: bool = False) -> int:
    """Convert XXXXX bid --> a base 14 number for comparison."""
    rank_order = CARD_RANK
    if is_jokers:
        rank_order = CARD_RANK_JOKERS
    # Ignore the bid for sorting.
    hand = hand.split()[0]
    digital_hand = ''
    for card in hand:
        digital_hand += rank_order[card]
    return int(digital_hand, base=14)


def compare_forward_hands_of_same_type(hand_1: str, hand_2: str) -> bool:
    """Return True if first hand ranks higher on first different card."""
    for card_1, card_2 in zip(hand_1, hand_2):
        if card_1 == card_2:
            continue
        return CARD_RANK.index(card_1) > CARD_RANK.index(card_2)


def check_type(hand: str, is_jokers: bool = False) -> int:
    """High card = 0, Five of a kind = 6"""
    cards = dict()
    for card in hand:
        n_already = cards.get(card, 0)
        n_already += 1
        cards[card] = n_already
    qties = list(cards.values())
    if is_jokers:
        qties = adjust_qties_with_jokers(qties, cards.get('J', 0))
    if 5 in qties:
        # Five of a kind.
        return 6
    elif 4 in qties:
        # Four of a kind.
        return 5
    elif 3 in qties:
        if 2 in qties:
            # Full house.
            return 4
        else:
            # Three of a kind.
            return 3
    elif 2 in qties:
        if len(qties) == 3:
            # Two pair.
            return 2
        else:
            # One pair.
            return 1
    else:
        # High card.
        return 0


def adjust_qties_with_jokers(qties: list[int], n_jokers: int) -> list[int]:
    """High card = 0, Five of a kind = 6"""
    if not n_jokers:
        # No jokers.
        return qties
    # Pull the jokers.
    qties.remove(n_jokers)
    if n_jokers == 1:
        if 4 in qties:
            # Create a 5 of a kind.
            return [5]
        elif 3 in qties:
            # Create a 4 of a kind.
            return [4, 1]
        elif 2 in qties:
            if len(qties) == 2:
                # Create a full house.
                return [3, 2]
            else:
                # Create a three of a kind.
                return [3, 1, 1]
        else:
            # Create a pair.
            return [2, 1, 1, 1]
    elif n_jokers == 2:
        if 3 in qties:
            # Create a 5 of a kind.
            return [5]
        elif 2 in qties:
            # Create a 4 of a kind.
            return [4, 1]
        else:
            # Create a 3 of a kind.
            return [3, 1, 1]
    elif n_jokers == 3:
        if 2 in qties:
            # Create a 5 of a kind.
            return [5]
        else:
            # Create a 4 of a kind.
            return [4, 1]
    else:
        # 4 or 5 jokers result in 5 of a kind.
        return [5]



if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        data = f.read()
    print('Part 1: ', part1(data))
    print('Part 2: ', part2(data))
