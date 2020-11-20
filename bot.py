from PIL import ImageGrab
from autocorrect import Speller
from PIL import Image
import pytesseract
import requests
import re
import cv2
import time
import numpy as np
import pyautogui
import random
from colorthief import ColorThief
'''
Path is where the hint hints file is located.
Hint positions indicate where the program takes screenshots
'''

path = "hints.txt"
hintPosOnScreen = [(), (64, 279, 320, 305), (64, 307, 320, 333), (64, 335, 320, 361), (64, 363, 320, 389), (64, 391, 320, 417), (64, 419, 320, 445)]
dirPosOnScreen = [(), (45, 280, 65, 300), (45, 308, 65, 328), (45, 336, 65, 356), (45, 364, 65, 384), (45, 392, 65, 412), (45, 420, 65, 440)]
flagsPosOnScreen = [(), (300, 282, 325, 308), (300, 310, 325, 336), (300, 338, 325, 364), (300, 366, 325, 392), (300, 394, 325, 420), (300, 422, 325, 448)]

# Initialise spellchecker

spell = Speller('fr')


def pil_to_cv2(pil_img):
    numpy_image = np.array(pil_img)
    opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
    return opencv_image


def cv2_to_pil(opencv_image):
    color_coverted = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(color_coverted)
    return pil_image


def get_hints(path):
    hints = dict()
    try:
        hints = open(path, "r").read()
    except Exception:
        print("Failed to read hint list file")
        exit()
    return hints


def preprocess_hints(text):
    for x in text:
        text[x] = text[x].replace(" ", "")
        text[x] = text[x].replace("\"", "")
        text[x] = text[x].replace("\'", "")
    return text


def click(t):
    currentMouseX, currentMouseY = pyautogui.position()
    (a, b, c, d) = t
    x = (a + c) // 2
    y = (b + d) // 2
    pyautogui.click(x, y)
    pyautogui.moveTo(currentMouseX, currentMouseY)
    return


def match_phor(img_rgb):

    color = ColorThief(img_rgb)
    palette = color.get_palette(color_count=3)
    img_rgb = pil_to_cv2(img_rgb)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = []
    for i in range(3):
        for t in range(4):
            try:
                if t == 0:
                    template = read_transparent_png("temp1.png", palette[i])
                    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                elif t == 1:
                    template = read_transparent_png("temp2.png", palette[i])
                    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                elif t == 2:
                    template = read_transparent_png("temp3.png", palette[i])
                    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                elif t == 3:
                    template = read_transparent_png("temp4.png", palette[i])
                    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            except Exception:
                print("Template images failed to load")
                exit()
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.7
            loc = np.where(res >= threshold)
            a = len(list(zip(*loc[::-1])))
            if a > 0:
                print("phorreur found")
                return True
            if a == 0:
                print("testing diffrent orientation")
    print("could not find phorreur")
    return False


def read_transparent_png(filename, colour):
    image_4channel = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    alpha_channel = image_4channel[:, :, 3]
    rgb_channels = image_4channel[:, :, :3]

    # colour Background Image
    background_image = np.ones_like(rgb_channels, dtype=np.uint8)
    background_image[..., 2] = background_image[..., 0] * colour[0]
    background_image[..., 1] = background_image[..., 0] * colour[1]
    background_image[..., 0] = background_image[..., 0] * colour[2]

    # Alpha factor
    alpha_factor = alpha_channel[:, :, np.newaxis].astype(np.float32) / 255.0
    alpha_factor = np.concatenate((alpha_factor, alpha_factor, alpha_factor), axis=2)

    # Transparent Image Rendered on colored Background
    base = rgb_channels.astype(np.float32) * alpha_factor
    white = background_image.astype(np.float32) * (1 - alpha_factor)
    final_image = base + white
    # cv2.imwrite("test.png", final_image)
    return final_image.astype(np.uint8)


def preprocess(img, flag):
    # Otsu thresholding
    # img = cv2.imread(filename, 0)
    img = cv2.GaussianBlur(img, (1, 1), 0)
    # img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
    #         cv2.THRESH_BINARY,11,2)
    ret2, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if flag == 1:
        img = cv2.bitwise_not(img)
    # cv2.imwrite("thresh.png", img)
    return img.astype(np.uint8)


def getDirection(i):
    im = ImageGrab.grab(bbox=dirPosOnScreen[i])
    # im.save("dir.png", "PNG")
    image = preprocess(pil_to_cv2(im), 0)
    template = cv2.imread("dir_template.png")
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    (a, b) = np.unravel_index(result.argmax(), result.shape)

    if b > 208:
        dir = "top"
    elif b > 136:
        dir = "right"
    elif b > 67:
        dir = "left"
    elif b > 30:
        dir = "bottom"
    else:
        dir = "checkbox"

    print("direction aquired : ", dir)
    return dir


def screenGrab(i):
    im = ImageGrab.grab(bbox=hintPosOnScreen[i])
    im = im.resize((450, 50), Image.BICUBIC)
    im = im.convert('L')
    # im.save("hint.png", "PNG")
    return preprocess(pil_to_cv2(im), 0)


def myPos():
    im = ImageGrab.grab(bbox=(28, 44, 145, 74))
    im = im.resize((500, 100))
    im = pil_to_cv2(im)
    # im.save("myPos.png", "PNG", optimize=True)
    cv2.imwrite("position_proccessed.png", preprocess(im, 1))
    custom_config = r'-c tessedit_char_whitelist=-,0123456789 --psm 6'
    txt = pytesseract.image_to_string("position_proccessed.png", lang='digits_comma', config=custom_config)
    # txt = txt.replace("~","-")
    # txt = txt.replace("\"", "-")
    # txt = txt.replace("+", "")
    # txt = txt.replace(" ", "")
    # txt = txt.replace("O", "0")
    # txt = txt.replace("A", "4")
    try:
        pos = re.findall("[-\\d]+", txt)
        x = pos[0]
        y = pos[1]
    except Exception:
        print("couldnt get position , try changing function parameters")
        return
    return int(x), int(y)


def isChecked(i):
    im = ImageGrab.grab(bbox=flagsPosOnScreen[i])
    # im.save("f.png", "PNG")
    width, height = im.size
    for x in range(width):
        y = height // 2 - 3
        r, g, b = im.getpixel((x, y))
        if g > 200:
            return True

    return False


def phorreur(i, dir):
    d = 1
    x, y = myPos()
    print("Phorreur at", dir)
    im = ImageGrab.grab(bbox=(351, 0, 1570, 865))
    # im.save("phorreur_check.png", "PNG")
    numap = 0
    boucle = 0
    while match_phor(im) is False:

        if numap == 10:
            boucle = 1
        elif numap == 0:
            boucle = 0

        if boucle == 1:
            print("returning")
            if dir == "left":
                navigate("right", d, x + 1, y)
            elif dir == "right":
                navigate("left", d, x - 1, y)
            elif dir == "top":
                navigate("bottom", d, x, y + 1)
            elif dir == "bottom":
                navigate("top", d, x, y - 1)
            im = ImageGrab.grab(bbox=(351, 0, 1570, 865))
            im.save("phorreur_check.png", "PNG")
            x, y = myPos()
            numap = numap - 1

        elif boucle == 0:
            print("searching")
            if dir == "left":
                navigate(dir, d, x - 1, y)
            elif dir == "right":
                navigate(dir, d, x + 1, y)
            elif dir == "top":
                navigate(dir, d, x, y - 1)
            elif dir == "bottom":
                navigate(dir, d, x, y + 1)
            im = ImageGrab.grab(bbox=(351, 0, 1570, 865))
            im.save("phorreur_check.png", "PNG")
            x, y = myPos()
            numap = numap + 1

    click(flagsPosOnScreen[i])
    while isChecked(i) is False:
        time.sleep(0.3)
    return


def fixSpelling(string):
    for x in string:
        if (x.isalpha() is False):
            # if (x.isalpha() is False) and (x!="\'") and (x!=" "):
            string = string.replace(x, "")
    string = string.strip(' ')
    string = spell(string)
    print("spelling fixed : ", string)
    return string


def getHint(i):
    im = cv2_to_pil(screenGrab(i))
    hint = pytesseract.image_to_string(im, lang='fra')
    hint = hint.strip(' ')
    print("hint aquired : ", hint)
    return hint


def request(x, y, dir, n):
    _url = "https://dofus-map.com:443/huntTool/getData.php?x=" + str(x) + "&y=" + str(y) + "&direction=" + dir + "&world=0&language=fr"
    _cookies = {"language": "fr", "_ga": "GA1.2.248099094.1590810638", "_gid": "GA1.2.1175252966.1590810638", "__gads": "ID=ffe46b184016c260:T=1590814251:S=ALNI_MYkkuOrsAhRdweCF2D9sQjoLTM6KQ"}
    _headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0", "Accept": "*/*", "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3", "Accept-Encoding": "gzip, deflate", "Connection": "close", "Referer": "https://dofus-map.com/hunt"}
    r = requests.get(_url, headers=_headers, cookies=_cookies)
    rq = r.json()
    hints = rq.get("hints")
    try:
        distance = None
        for k in hints:
            if k["n"] == int(n):
                distance = k["d"]
                print("distance is ", str(distance))
                break
        if dir == "right":
            x += int(distance)
        elif dir == "left":
            x -= int(distance)
        elif dir == "top":
            y -= int(distance)
        elif dir == "bottom":
            y += int(distance)
    except Exception:
        print("could not process request properly , check if input data is correct")
        return
    return x, y, distance


def navigate(dir, d, x, y):
    if dir == 'left':
        print('left')
        while True:
            (a, b) = myPos()
            if (a, b) == (x, y):
                return
            yy = random.choice([120, 400, 670])
            currentMouseX, currentMouseY = pyautogui.position()
            pyautogui.click(352, yy)
            pyautogui.moveTo(currentMouseX, currentMouseY)
            time.sleep(0.1)
            while myPos() == (a, b):
                True

    elif dir == 'right':
        print('right')
        while True:
            (a, b) = myPos()
            if (a, b) == (x, y):
                return
            yy = random.choice([120, 400, 670])
            currentMouseX, currentMouseY = pyautogui.position()
            pyautogui.click(1570, yy)
            pyautogui.moveTo(currentMouseX, currentMouseY)
            time.sleep(0.1)
            while myPos() == (a, b):
                True

    elif dir == 'top':
        print("top")
        while True:
            (a, b) = myPos()
            if (a, b) == (x, y):
                return
            xx = random.choice([550, 950, 1315])
            currentMouseX, currentMouseY = pyautogui.position()
            pyautogui.click(xx, 1)
            pyautogui.moveTo(currentMouseX, currentMouseY)
            time.sleep(0.1)
            while myPos() == (a, b):
                True

    elif dir == 'bottom':
        print("down")
        while True:
            (a, b) = myPos()
            if (a, b) == (x, y):
                return
            xx = random.choice([550, 950, 1315])
            currentMouseX, currentMouseY = pyautogui.position()
            pyautogui.click(xx, 853)
            pyautogui.moveTo(currentMouseX, currentMouseY)
            time.sleep(0.1)
            while myPos() == (a, b):
                True


def Ready(i):
    box = list(flagsPosOnScreen[i])
    box[1] = box[1] + 28
    box[3] = box[3] + 28
    box[0] = box[0] - 25
    box[2] = box[2] - 25
    im = ImageGrab.grab(bbox=box)
    # im.save("ready.png", "PNG")
    width, height = im.size
    f = False
    for x in range(width):
        y = height // 2
        # r, g, b = im.getpixel((x, y))
        g = im.getpixel((x, y))[2]
        # print((r, g, b))
        if g > 200:
            f = True
            break
    if f:
        print("fin étape")
        currentMouseX, currentMouseY = pyautogui.position()
        pyautogui.click((box[0] + box[2]) // 2, (box[1] + box[3]) // 2)
        pyautogui.moveTo(currentMouseX, currentMouseY)
        time.sleep(1)
        main()
    return False


def main():
    hints = get_hints(path)
    try:
        for i in range(1, 7):
            if isChecked(i) is True:
                if i != 6:
                    print("indice " + str(i) + " checked")
                    Ready(i)
                    continue
                else:
                    print("indice " + str(i) + " checked")
                    Ready(i)
                    main()

            print("indice num " + str(i))
            x, y = myPos()
            print("myPos = " + str((x, y)))
            dir = getDirection(i)
            hint = getHint(i)
            if "Phorreur" in hint:
                phorreur(i, dir)
            else:
                lenTxt = len(hint)
                try:
                    n = None
                    if lenTxt < 21:
                        for key, value in hints.items():
                            if hint.lower() == value.lower():
                                n = key
                        # n = list(hints.keys())[list(hints.values()).index(hint)]
                    else:
                        for key, value in hints.items():
                            if hint[:-1] in value:
                                n = key
                    if n is None:
                        raise Exception
                except Exception:
                    try:
                        n = None
                        print("ERROR reading hint , attempting spelling fix")
                        hints = preprocess_hints(hints)
                        hint = fixSpelling(hint)
                        if "Phorreur" in hint:
                            phorreur(i)
                        if lenTxt < 22:
                            for key, value in hints.items():
                                if hint.lower() == value.lower():
                                    n = key
                            # n = list(hints.keys())[list(hints.values()).index(hint)]
                        else:
                            for key, value in hints.items():
                                if hint[:-1] in value:
                                    n = key
                        if n is None:
                            raise Exception
                    except Exception:
                        print("ERROR getting hint id, check main boucle , retrying")
                        main()
                        return
                        # popup.alert_popup("End?","RERUN?","")
                print(dir)
                x, y, dist = request(x, y, dir, n)
                print("go to " + str((x, y)))
                # popup.alert_popup("indice num " + str(i), dir + " " + str(d) + "\ngo to " + str((x, y)), "")
                navigate(dir, dist, x, y)
                # while (x, y) != myPos():
                #    time.sleep(0.5)
                print("clicking")
                click(flagsPosOnScreen[i])

            while isChecked(i) is False:
                time.sleep(0.2)
        main()
    except Exception:
        print("Error occured check above messages for information")
        main()
        # popup.alert_popup("End?", "RERUN?", "")


if __name__ == '__main__':
    main()
