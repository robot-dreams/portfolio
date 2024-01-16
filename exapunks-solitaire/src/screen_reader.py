from collections import Counter
from itertools import chain
from PIL import Image

import pyautogui
import time

S_X0 = 557
S_Y0 = 765
S_DX = 201
S_DY = 45
S_W = 18
S_H = 18

class ScreenReader:
    def __init__(self):
        self.reference = {}
        for card in chain(range(1, 5), range(12, 22)):
            f = '{}.png'.format(card)
            self.reference[card] = Image.open(f)

    def limit(self, card):
        if 1 <= card <= 4:
            return 4
        else:
            return 2

    def get_diff(self, im1, im2, threshold=10000):
        result = 0
        for i in range(S_W):
            for j in range(S_H):
                p1 = im1.getpixel((i, j))
                p2 = im2.getpixel((i, j))
                for k in range(4):
                    result += (p2[k] - p1[k])**2
                if result > threshold:
                    return threshold
        return result

    def read(self):
        screen = pyautogui.screenshot()
        seen = Counter()
        piles = []
        for p in range(9):
            pile = []
            for h in range(4):
                x1 = S_X0 + p * S_DX
                y1 = S_Y0 + h * S_DY
                im = screen.crop((x1, y1, x1 + S_W, y1 + S_H))
                best_card = None
                best_diff = float('inf')
                for card in self.reference:
                    if seen[card] == self.limit(card):
                        continue
                    diff = self.get_diff(im, self.reference[card])
                    if diff < best_diff:
                        best_card = card
                        best_diff = diff
                    if diff == 0:
                        break
                seen[best_card] += 1
                pile.append(best_card)
            piles.append(pile)
        return piles
