import pyautogui
import time

X0 = 290
Y0 = 390
DX = 100
DY = 23
XF = 1050
YF = 210

def transfer(p1, h1, p2, h2):
    x1 = X0 + DX * p1
    y1 = Y0 + DY * h1
    x2 = X0 + DX * p2
    y2 = Y0 + DY * h2
    pyautogui.mouseDown(x1, y1)
    pyautogui.mouseUp(x2, y2)

def free(p, h):
    x = X0 + DX * p
    y = Y0 + DY * h
    pyautogui.mouseDown(x, y)
    pyautogui.mouseUp(XF, YF)

def unfree(p, h):
    x = X0 + DX * p
    y = Y0 + DY * h
    pyautogui.mouseDown(XF, YF)
    pyautogui.mouseUp(x, y)

def play(moves):
    for move in moves:
        if move[0] == 'transfer':
            _, p1, h1, p2, h2 = move
            transfer(p1, h1, p2, h2)
        elif move[0] == 'free':
            _, p, h = move
            free(p, h)
        else:
            _, p, h = move
            unfree(p, h)
