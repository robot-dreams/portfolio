"""
Automatically beats the Solitaire game in EXAPUNKS

Settings used:
- Default resolution for Retina display (15" MBP 2015)
- Windowed mode
- 2880x1620 resolution
- Low graphics quality (2K)
- Snap to top (using SizeUp)
"""

from player import play
from solver import solve, GaveUp
from screen_reader import ScreenReader

import pyautogui
import time

s = ScreenReader()

while True:
    print('Reading cards from screen...')
    piles = s.read()
    print('Done.\n')
    print(piles)

    print('Finding solution...')
    try:
        moves = solve(piles)
        print('Done.\n')

        print('Executing solution...')
        play(moves)
        print('Done.\n')

        time.sleep(3)
    except (GaveUp, RecursionError):
        print('Giving up and trying again with new game.')

    pyautogui.mouseDown(1050, 710)
    pyautogui.mouseUp(1050, 710)
    time.sleep(7)
