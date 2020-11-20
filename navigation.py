from PIL import ImageGrab
import pytesseract
import re
import cv2
import time
import pyautogui
import random
import os

hintPosOnScreen = [(52, 277, 292, 311), (52, 305, 292, 340), (52, 335, 292, 370), (52, 368, 292, 396), (52, 395, 292, 426), (52, 425, 292, 449), (52, 453, 292, 485)]
dirPosOnScreen = [(), (28, 314, 50, 329), (27, 344, 50, 357), (29, 370, 50, 391), (27, 399, 50, 421), (31, 428, 46, 449), (28, 461, 49, 473)]
flagsPosOnScreen = [(), (299, 311, 322, 336), (300, 341, 322, 365), (300, 370, 322, 394), (302, 400, 321, 423), (301, 430, 322, 452), (301, 458, 322, 480)]


def preprocess(filename):
    # Otsu thresholding
    img = cv2.imread(filename, 0)
    blur = cv2.GaussianBlur(img, (1, 1), 0)
    ret2, th2 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    th2 = cv2.bitwise_not(th2)
    cv2.imwrite("thresh.png", th2)


def myPos():
    im = ImageGrab.grab(bbox=(28, 44, 145, 74))
    im = im.resize((250, 50))
    # im.save("myPos.png", "PNG")
    im.save("myPos.png", "PNG", optimize=True)
    preprocess("myPos.png")
    custom_config = r'-c tessedit_char_whitelist=-,0123456789 --psm 6'
    txt = pytesseract.image_to_string("thresh.png", lang='digits_comma', config=custom_config)
    txt = txt.replace("~", "-")
    txt = txt.replace("\"", "-")
    txt = txt.replace("+", "")
    txt = txt.replace(" ", "")
    txt = txt.replace("O", "0")
    txt = txt.replace("A", "4")
    try:
        pos = re.findall("[-\\d]+", txt)
        x = pos[0]
        y = pos[1]
    except Exception:
        print("couldnt get position , try changing function parameters")
    return int(x), int(y)


def getDestDir(x, y, xx, yy):
    try:
        x, y = myPos()
        print("myPos = " + str((x, y)))
        i = yy - y
        j = xx - x
        if (j > 0):
            dirx = "right"
        elif (j == 0):
            dirx = "none"
        else:
            dirx = "left"
        if (i > 0):
            diry = "bottom"
        elif (i == 0):
            diry = "none"
        else:
            diry = "top"

    except Exception:
        print("error getting direction , maybe postition failed")
    return (dirx, diry, x, y)


def movex(dir, x):

    if dir == 'left':
        print('left')
        while True:
            (a, b) = myPos()
            if (a, b) == (x, b):
                return
            yy = random.choice([120, 400, 670])
            currentMouseX, currentMouseY = pyautogui.position()
            pyautogui.click(352, yy)
            pyautogui.moveTo(currentMouseX, currentMouseY)
            while myPos() == (a, b):
                time.sleep(0.2)

    elif dir == 'right':
        print('right')
        while True:
            (a, b) = myPos()
            if (a, b) == (x, b):
                return
            yy = random.choice([120, 400, 670])
            currentMouseX, currentMouseY = pyautogui.position()
            pyautogui.click(1570, yy)
            pyautogui.moveTo(currentMouseX, currentMouseY)
            while myPos() == (a, b):
                time.sleep(0.2)


def movey(dir, y):

    if dir == 'top':
        print("top")
        while True:
            (a, b) = myPos()
            if (a, b) == (a, y):
                return a, b
            xx = random.choice([550, 950, 1315])
            currentMouseX, currentMouseY = pyautogui.position()
            pyautogui.click(xx, 1)
            pyautogui.moveTo(currentMouseX, currentMouseY)
            while myPos() == (a, b):
                time.sleep(0.2)

    elif dir == 'bottom':
        print("down")
        while True:
            (a, b) = myPos()
            if (a, b) == (a, y):
                return a, b
            xx = random.choice([670, 1000, 1320])
            currentMouseX, currentMouseY = pyautogui.position()
            pyautogui.click(xx, 853)
            pyautogui.moveTo(currentMouseX, currentMouseY)
            while myPos() == (a, b):
                time.sleep(0.2)


def main():
    try:
        (x, y) = myPos()
        print("Destination x :")
        xx = int(input())
        print("Destination y :")
        yy = int(input())

        try:
            while (xx, yy) != (x, y):
                dirx, diry, x, y = getDestDir(x, y, xx, yy)
                movex(dirx, xx)
                movey(diry, yy)
                (x, y) = myPos()
            print("position reached")
            os.system("ezpz.py")
            return
        except Exception:
            print("error navigating")
            print("retry ? Y/N")
            test = input()
            if test == 'y':
                main()
            else:
                return
    except Exception:
        print("error reading pos")
        print("retry ? Y/N")
        test = input()
        if test == 'y':
            main()
        else:
            return


if __name__ == '__main__':
    main()
