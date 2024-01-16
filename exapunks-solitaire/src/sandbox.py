import pyautogui
import time

S_X0 = 557
S_Y0 = 765
S_DX = 201
S_DY = 45
S_W = 18
S_H = 18

start = time.time()
im = pyautogui.screenshot()
for p in range(9):
    for h in range(4):
        start = time.time()
        x1 = S_X0 + p * S_DX
        y1 = S_Y0 + h * S_DY
        im2 = im.crop((x1, y1, x1 + S_W, y1 + S_H))
        print('Elapsed: {}', time.time() - start)
