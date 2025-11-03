import numpy as np
import cv2
import os
import importlib.machinery
import importlib.util

# 通过路径加载模块，避免中文文件名导入问题
MODULE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '车牌识别.py'))
loader = importlib.machinery.SourceFileLoader('plate_module', MODULE_PATH)
spec = importlib.util.spec_from_loader(loader.name, loader)
plate_module = importlib.util.module_from_spec(spec)
loader.exec_module(plate_module)

get_plate_color = plate_module.get_plate_color


def make_solid_bgr(color_bgr, w=200, h=80):
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:, :] = color_bgr
    return img


def test_blue_plate():
    # BGR blue
    img = make_solid_bgr((255, 0, 0))
    # full image is plate
    res = get_plate_color(img, (0, 0, img.shape[1], img.shape[0]))
    assert res in ('蓝色', '未知') and res == '蓝色'


def test_green_plate():
    # approximate green
    img = make_solid_bgr((0, 255, 0))
    res = get_plate_color(img, (0, 0, img.shape[1], img.shape[0]))
    assert res in ('新能源绿色', '绿色', '未知') and res == '新能源绿色'


def test_yellow_plate():
    # yellow in BGR (0,255,255)
    img = make_solid_bgr((0, 255, 255))
    res = get_plate_color(img, (0, 0, img.shape[1], img.shape[0]))
    assert res in ('黄色', '未知') and res == '黄色'


def test_white_plate():
    img = make_solid_bgr((255, 255, 255))
    res = get_plate_color(img, (0, 0, img.shape[1], img.shape[0]))
    assert res == '白色'


def test_red_plate():
    img = make_solid_bgr((0, 0, 255))
    res = get_plate_color(img, (0, 0, img.shape[1], img.shape[0]))
    assert res == '红色' or res == '未知'
