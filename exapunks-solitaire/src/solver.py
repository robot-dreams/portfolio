from random import shuffle

class GaveUp(Exception):
    pass

"""
Face cards are represented depending on suit:
1 - clubs
2 - diamonds
3 - hearts
4 - spades

Number cards are represented as 2 * value + color
- value ranges from 6-10
- color is either 0 (black) or 1 (red)

A board consists of:
- free_cell (None or a card)
- 9 lists of cards
"""

MAX_FACE_PILE = 4
MAX_NUMBER_PILE = 5
MAX_MOVABLE = max(MAX_FACE_PILE, MAX_NUMBER_PILE)
NUM_PILES = 9

def is_face(card):
    return 1 <= card <= 4

def value(card):
    """
    Precondition: not is_face(card)
    """
    return card >> 1

def color(card):
    """
    Precondition: not is_face(card)
    """
    return card & 1

def is_valid_face(pile, d):
    """
    Preconditions:
    - len(pile) >= d
    - is_face(pile[-d])
    """
    # All cards in pile must match top
    for i in range(1, d):
        if pile[-i] != pile[-d]:
            return False
    return True

def is_movable_face(pile, d):
    """
    Preconditions:
    - len(pile) >= d
    - is_face(pile[-d])
    """
    if not is_valid_face(pile, d):
        return False
    if len(pile) == MAX_FACE_PILE and is_valid_face(pile, MAX_FACE_PILE):
        return False
    return True

def is_stackable_number(lo, hi):
    """
    Preconditions:
    - not is_face(lo)
    - not is_face(hi)
    """
    # values must be ascending
    if value(lo) + 1 != value(hi):
        return False
    # colors must be alternating
    if color(lo) ^ 1 != color(hi):
        return False
    return True

def is_movable_number(pile, d):
    """
    Preconditions:
    - len(pile) >= d
    - not is_face(pile[-d])
    """
    for i in range(1, d):
        lo = pile[-i]
        hi = pile[-i-1]
        if is_face(lo):
            return False
        if not is_stackable_number(lo, hi):
            return False
    return True

def is_good_pile(pile):
    if not pile:
        return False
    elif is_face(pile[0]):
        return False
    else:
        return value(pile[0]) == 10 and is_movable_number(pile, len(pile))

def is_solved_pile(pile):
    if not pile:
        return True
    if len(pile) == MAX_FACE_PILE and is_face(pile[0]):
        return is_valid_face(pile, MAX_FACE_PILE)
    if len(pile) == MAX_NUMBER_PILE and not is_face(pile[0]):
        return is_movable_number(pile, MAX_NUMBER_PILE)
    return False

class Board:
    def __init__(self, piles):
        self.free_cell = None
        self.piles = piles

    def __str__(self):
        return str(self.free_cell) + '/' + str(self.piles)

    def solve(self, seen, moves):
        if self.is_solved():
            return True

        if len(seen) > 10**4:
            raise GaveUp

        key = str(self)
        if key in seen:
            return False
        seen.add(key)

        srcs = list(range(NUM_PILES))
        dsts = list(range(NUM_PILES))
        shuffle(srcs)
        shuffle(dsts)

        for dst in dsts:
            if self.can_unfree(dst):
                moves.append(('unfree', dst, len(self.piles[dst])))
                self.unfree(dst)
                if self.solve(seen, moves):
                    return True
                moves.pop()
                self.free(dst)

        for src in srcs:
            for dst in dsts:
                for d in range(MAX_MOVABLE, 0, -1):
                    if self.can_transfer(src, dst, d):
                        moves.append(('transfer', src, len(self.piles[src]) - d, dst, len(self.piles[dst])))
                        self.transfer(src, dst, d)
                        if self.solve(seen, moves):
                            return True
                        moves.pop()
                        self.transfer(dst, src, d)

        for src in srcs:
            if self.can_free(src):
                moves.append(('free', src, len(self.piles[src]) - 1))
                self.free(src)
                if self.solve(seen, moves):
                    return True
                moves.pop()
                self.unfree(src)

        return False

    def is_solved(self):
        if self.free_cell is not None:
            return False
        for pile in self.piles:
            if not is_solved_pile(pile):
                return False
        return True

    def can_transfer(self, src, dst, d):
        if src == dst:
            return False
        if is_good_pile(self.piles[src]):
            return False
        if len(self.piles[src]) < d:
            return False
        if len(self.piles[src]) > d:
            pile = self.piles[src]
            if is_face(pile[-d-1]) and is_movable_face(pile, d + 1):
                return False
            if not is_face(pile[-d-1]) and is_movable_number(pile, d + 1):
                return False

        src_top = self.piles[src][-d]
        dst_bot = None
        if self.piles[dst]:
            dst_bot = self.piles[dst][-1]

        if is_face(src_top):
            if not is_movable_face(self.piles[src], d):
                return False
            if dst_bot is not None and dst_bot != src_top:
                return False
        else:
            if not is_movable_number(self.piles[src], d):
                return False
            if dst_bot is not None:
                if is_face(dst_bot):
                    return False
                if not is_stackable_number(src_top, dst_bot):
                    return False
        return True

    def transfer(self, src, dst, d):
        self.piles[dst].extend(self.piles[src][-d:])
        self.piles[src] = self.piles[src][:-d]

    def can_free(self, src):
        if self.free_cell is not None:
            return False
        pile = self.piles[src]
        if not pile:
            return False
        if is_good_pile(self.piles[src]):
            return False
        if len(pile) > 1:
            if is_face(pile[-2]) and is_movable_face(pile, 2):
                return False
            if not is_face(pile[-2]) and is_movable_number(pile, 2):
                return False
        return not is_face(pile[-1]) or is_movable_face(pile, 1)

    def free(self, src):
        self.free_cell = self.piles[src][-1]
        self.piles[src].pop()

    def can_unfree(self, dst):
        if self.free_cell is None:
            return False
        pile = self.piles[dst]
        if not pile:
            return True
        elif is_face(self.free_cell):
            return pile[-1] == self.free_cell
        else:
            return is_stackable_number(self.free_cell, pile[-1])

    def unfree(self, dst):
        self.piles[dst].append(self.free_cell)
        self.free_cell = None

def solve(piles):
    board = Board(piles)
    seen = set()
    moves = []
    board.solve(seen, moves)
    return moves
