import os
import cv2
import random
import numpy as np
from PIL import Image
import logging
from pytesseract import image_to_string

# ADB related


def tap(crd: (int, int)):
    cmdTap = 'adb shell input tap {x} {y}'.format(
        x=crd[0],
        y=crd[1]
    )
    logging.info(cmdTap)
    os.system(cmdTap)


def swipe(org: (int, int), tar: (int, int), delay):
    cmdSwipe = 'adb shell input swipe {x1} {y1} {x2} {y2} {delay1}'.format(
        x1=org[0],
        y1=org[1],
        x2=tar[0],
        y2=tar[1],
        delay1=int(delay*1000)
    )
    logging.info(cmdSwipe)
    os.system(cmdSwipe)


def screenshot() -> str:
    os.system('adb shell screencap -p /sdcard/sh.png')
    os.system('adb pull /sdcard/sh.png .')
    return "sh.png"


# helper function
def shifter(ord: (int, int), i: int = 10, j: int = 10) -> (int, int):
    return (ord[0] + random.randint(-i, i), ord[1] + random.randint(-j, j))


def split(path: str, edge: (int, int)):
    img = Image.open(path)
    out = img.crop((edge[0], edge[1], edge[0]+1920, edge[1]+1080))
    out.save("tmp.png")


def get_sh(edge: (int, int)) -> str:
    screenshot()
    split("sh.png", edge)
    return "tmp.png"


# OpenCV related
def standby(sh: str, tmp: str, threshold: float = 0.85) -> bool:
    img = cv2.imread(sh, 0)
    template = cv2.imread(tmp, 0)
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    if (res >= threshold).any():
        return True
    return False


def check_color(sh: str, tmp: str, threshold: float = 0.8) -> bool:
    img = cv2.imread(sh, cv2.IMREAD_COLOR)
    template = cv2.imread(tmp, cv2.IMREAD_COLOR)
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    if (res >= threshold).any():
        return True
    return False


def get_crd(sh: str, tmp: str, threshold: float = 0.85) -> [(int, int)]:
    img = cv2.imread(sh, 0)
    template = cv2.imread(tmp, 0)
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    pos = []
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        pos.append(pt)
    return pos


def get_battle_id(img_path: str):
    img = Image.open(img_path)
    region = img.crop((1286, 15, 1378, 62))
    THRESHOLD = 200
    BINARY_TABLE = [0 if i < THRESHOLD else 1 for i in range(256)]
    text = image_to_string(
        region.convert('L').point(BINARY_TABLE, '1'), config='--psm 7 --oem 3 -c tessedit_char_whitelist=/1234')
    print(text)
    try:
        x = int(text[0])
    except IndexError:
        print("Failed to recognize battle id.")
        return 0
    except ValueError:
        print("Failed to recognize battle id.")
        return 0
    else:
        return x


def split_cards(img: str):
    im = Image.open(img)
    img_size = im.size
    x = img_size[0] // 5
    y = img_size[1] // 2 - 50
    for i in range(5):
        left = i*x
        up = y
        right = left + x
        low = up + y
        region = im.crop((left, up, right, low))
        region.save(f"./temp/{i}.png")


# prepare for servant reo
def split_servant(img: str, i: int):
    im = Image.open(img)
    size = (138, 144, 238, 226)
    region = im.crop(size)
    region.save(f"./temp/_s{i}.png")
