import os
import sys
import re
import numpy as np
import glob
import cv2
from hyperlpr import HyperLPR_plate_recognition

# 解决numpy兼容问题
if not hasattr(np, 'int'):
    np.int = np.int32

# 省份简称映射表（含港澳台）
PROVINCE_MAP = {
    '京': '北京市', '津': '天津市', '沪': '上海市', '渝': '重庆市',
    '冀': '河北省', '晋': '山西省', '蒙': '内蒙古自治区',
    '辽': '辽宁省', '吉': '吉林省', '黑': '黑龙江省',
    '苏': '江苏省', '浙': '浙江省', '皖': '安徽省',
    '闽': '福建省', '赣': '江西省', '鲁': '山东省',
    '豫': '河南省', '鄂': '湖北省', '湘': '湖南省',
    '粤': '广东省', '桂': '广西壮族自治区', '琼': '海南省',
    '川': '四川省', '贵': '贵州省', '云': '云南省',
    '藏': '西藏自治区', '陕': '陕西省', '甘': '甘肃省',
    '青': '青海省', '宁': '宁夏回族自治区', '新': '新疆维吾尔自治区',
    '港': '香港特别行政区', '澳': '澳门特别行政区', '台': '台湾地区'
}

SPECIAL_PLATE_TYPES = {
    "警": "警用车牌", "使": "使馆车牌", "领": "领事车牌",
    "学": "教练车牌", "港": "港澳入境车牌", "澳": "港澳入境车牌"
}


def postprocess_plate(plate_str):
    """修正常见的分隔符并过滤非法字符。
    只保留：中文省份简称（来自 PROVINCE_MAP 的键）、拉丁字母和数字，以及少量特殊中文字。
    """
    if not plate_str:
        return plate_str
    s = re.sub(r'[\s·-]', '', plate_str).upper()
    allowed_chinese = set(PROVINCE_MAP.keys()) | set(['警', '学', '领', '使', '港', '澳', '台'])
    out = []
    for i, ch in enumerate(s):
        # 首位若为中文且在省份表中，保留
        if i == 0 and ch in allowed_chinese:
            out.append(ch)
            continue
        # 保留 ASCII 字母和数字
        if '0' <= ch <= '9' or 'A' <= ch <= 'Z':
            out.append(ch)
            continue
        # 保留一些中文特殊字
        if ch in allowed_chinese:
            out.append(ch)
            continue
        # 其它字符丢弃
    return ''.join(out)


def correct_plate_string(plate_str):
    """对常见 OCR 误识别进行位置感知修正。
    - 在车牌尾部（最后5位）优先把易混字符替换为数字：O->0, I/L->1, Z->2, S->5, B->8, G->6
    - 如果替换后数字太少，会做一次更宽松的替换。
    保持首位中文省份字符不变。
    """
    if not plate_str:
        return plate_str
    if not plate_str:
        return plate_str
    s = plate_str.upper()
    chars = list(s)

    # 常见混淆字符到数字的映射（更合理）
    mapping = {
        'O': '0', 'I': '1', 'L': '1'
    }

    n = len(chars)
    # 从第二位开始对尾部做保守替换，避免改动省份简称
    start = max(1, n - 5)
    for i in range(start, n):
        c = chars[i]
        if c in mapping:
            chars[i] = mapping[c]

    # 若数字个数仍然不足，放宽替换范围（从第二位开始）
    digit_count = sum(ch.isdigit() for ch in chars)
    if digit_count < 2:
        for i in range(1, n):
            c = chars[i]
            if c in mapping:
                chars[i] = mapping[c]

    return ''.join(chars)

def get_plate_color(image, plate_region):
    """改进版颜色识别（支持警用白牌和新能源绿牌）。
    通过配置的 HSV 范围计算各颜色像素比例，并按优先级返回颜色标签。
    """
    if not plate_region or all(v == 0 for v in plate_region):
        return "未知"

    x1, y1, x2, y2 = map(int, plate_region)
    plate_img = image[y1:y2, x1:x2]
    if plate_img.size == 0:
        return "未知"

    hsv = cv2.cvtColor(plate_img, cv2.COLOR_BGR2HSV)
    pixel_count = plate_img.shape[0] * plate_img.shape[1]

    # 颜色范围配置（HSV），可根据需要调整
    PLATE_COLOR_RANGES = {
        'blue': [(90, 40, 40), (130, 255, 255)],
        'yellow': [(15, 60, 60), (40, 255, 255)],
        # 绿色范围放宽以覆盖新能源牌不同亮度
        'green': [(35, 30, 30), (95, 255, 255)],
        # 红色使用两个区间，处理 HSV 的周期性
        'red1': [(0, 60, 50), (10, 255, 255)],
        'red2': [(160, 60, 50), (180, 255, 255)],
    }

    def mask_ratio(hsv_img, low, up):
        low = np.array(low, dtype=np.uint8)
        up = np.array(up, dtype=np.uint8)
        mask = cv2.inRange(hsv_img, low, up)
        return cv2.countNonZero(mask) / float(pixel_count)

    ratios = {}
    ratios['blue'] = mask_ratio(hsv, *PLATE_COLOR_RANGES['blue'])
    ratios['yellow'] = mask_ratio(hsv, *PLATE_COLOR_RANGES['yellow'])
    ratios['green'] = mask_ratio(hsv, *PLATE_COLOR_RANGES['green'])
    red_ratio = mask_ratio(hsv, *PLATE_COLOR_RANGES['red1']) + mask_ratio(hsv, *PLATE_COLOR_RANGES['red2'])

    # 白色判断：S 低且 V 高
    _, s_channel, v_channel = cv2.split(hsv)
    mean_s = float(np.mean(s_channel))
    mean_v = float(np.mean(v_channel))
    is_white = (mean_s <= 60 and mean_v >= 180)

    # 判定优先级：新能源绿 -> 蓝 -> 黄 -> 白 -> 红 -> 兜底
    if ratios.get('green', 0.0) >= 0.18:
        return '新能源绿色'
    if ratios.get('blue', 0.0) >= 0.18:
        return '蓝色'
    if ratios.get('yellow', 0.0) >= 0.18:
        return '黄色'
    if is_white:
        return '白色'
    if red_ratio >= 0.12:
        return '红色'

    # 兜底：返回占比最大的颜色（若超过低阈值）
    candidates = {'blue': ratios.get('blue', 0.0), 'yellow': ratios.get('yellow', 0.0),
                  'green': ratios.get('green', 0.0), 'red': red_ratio}
    main = max(candidates, key=candidates.get)
    if candidates.get(main, 0.0) >= 0.12:
        mapping = {'blue': '蓝色', 'yellow': '黄色', 'green': '绿色', 'red': '红色'}
        return mapping.get(main, '未知')

    return '未知'

def enhance_image_for_plate(image):
    """图像增强：对可能的车牌颜色区域做小幅度增强，返回增强后的 BGR 图像。
    增强策略保守，避免破坏原始字符信息。
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    # 简化并参数化增强：对蓝/绿/红区域做轻微的 S/V 提升
    color_masks = {
        'blue': (np.array([90, 40, 40], dtype=np.uint8), np.array([130, 255, 255], dtype=np.uint8)),
        'green': (np.array([35, 40, 40], dtype=np.uint8), np.array([100, 255, 255], dtype=np.uint8)),
        'red': (np.array([0, 100, 100], dtype=np.uint8), np.array([10, 255, 255], dtype=np.uint8)),
    }

    # 提升参数
    s_increase = {'blue': 30, 'green': 0, 'red': 0}
    v_increase = {'blue': 0, 'green': 20, 'red': 30}

    for cname, (low, up) in color_masks.items():
        mask = cv2.inRange(hsv, low, up)
        if s_increase.get(cname, 0) > 0:
            s[mask > 0] = np.clip(s[mask > 0] + s_increase[cname], 0, 255)
        if v_increase.get(cname, 0) > 0:
            v[mask > 0] = np.clip(v[mask > 0] + v_increase[cname], 0, 255)

    enhanced_hsv = cv2.merge([h, s, v])
    return cv2.cvtColor(enhanced_hsv, cv2.COLOR_HSV2BGR)


def preprocess_for_recognition(image):
    """对整张图做轻量预处理以提升字符识别效果：
    - 对 V 通道做 CLAHE 提升局部对比度
    - 应用轻度锐化（Unsharp mask）以增强字符边缘
    """
    # 转 HSV，增强 V
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    # CLAHE 在 V 通道
    try:
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        v_clahe = clahe.apply(v)
    except Exception:
        v_clahe = v

    hsv_clahe = cv2.merge([h, s, v_clahe])
    img_clahe = cv2.cvtColor(hsv_clahe, cv2.COLOR_HSV2BGR)

    # 锐化：unsharp mask
    gaussian = cv2.GaussianBlur(img_clahe, (0, 0), sigmaX=3)
    sharpened = cv2.addWeighted(img_clahe, 1.5, gaussian, -0.5, 0)

    return sharpened


def check_plate_number_format(plate_str, plate_color):
    """根据车牌颜色/类型检查车牌号格式。
    规则：
      - 新能源（绿色）格式为 2+6，总长度 8（例如：粤B123456）
      - 普通蓝牌格式为 2+5，总长度 7（例如：粤B12345）
    返回 (is_valid, expected_format_str, note)
    """
    if not plate_str:
        return False, None, "空车牌字符串"
    s = plate_str.upper()
    length = len(s)
    if plate_color == "新能源绿色" or "新能源" in plate_str:
        return (length == 8), "2+6(总长8)", ("" if length == 8 else f"长度 {length} != 8")
    if plate_color == "蓝色":
        return (length == 7), "2+5(总长7)", ("" if length == 7 else f"长度 {length} != 7")
    return True, None, ""
def _detect_plates_hyperlpr(image, scales=(1.0, 0.8, 1.2)):
    """在不同 scale 下调用 HyperLPR，返回一组字典结果：
    [{'plate':..., 'conf':..., 'bbox':..., 'scale':...}, ...]
    bbox 保持为原始返回格式（可能是列表或 None），映射到原图在后续处理。
    """
    all_results = []
    for scale in scales:
        try:
            if scale != 1.0:
                resized = cv2.resize(image, (0, 0), fx=scale, fy=scale)
            else:
                resized = image
            res = HyperLPR_plate_recognition(resized) or []
        except Exception:
            res = []

        for r in res:
            plate = r[0] if len(r) > 0 else ''
            conf = r[1] if len(r) > 1 else 0.0
            bbox = r[2] if len(r) > 2 else None
            all_results.append({'plate': plate, 'conf': conf, 'bbox': bbox, 'scale': scale})
    return all_results


def _map_bbox_to_original(bbox, scale, img_shape):
    """将检测时的 bbox（相对于 scaled 图）映射回原始图像坐标并做边界裁剪。
    bbox 可能为 None 或 [x1,y1,x2,y2]（字符串/数字混合）。
    返回 (x1,y1,x2,y2) 或 None。
    """
    if not bbox:
        return None
    try:
        bx = list(map(float, bbox))
        x1, y1, x2, y2 = map(int, bx)
        if scale and scale != 1.0:
            x1 = int(round(x1 / scale))
            y1 = int(round(y1 / scale))
            x2 = int(round(x2 / scale))
            y2 = int(round(y2 / scale))
        h, w = img_shape[:2]
        x1 = max(0, min(x1, w - 1))
        x2 = max(0, min(x2, w - 1))
        y1 = max(0, min(y1, h - 1))
        y2 = max(0, min(y2, h - 1))
        if x2 > x1 and y2 > y1:
            return (x1, y1, x2, y2)
    except Exception:
        return None


def recognize_plate(image_path):
    """核心识别函数（重构版）
    保持与原接口兼容：返回 (plate_str or None, status_msg, plate_color or None, plate_type or None)
    """
    if not os.path.exists(image_path):
        return None, "文件不存在", None, None

    image = cv2.imread(image_path)
    if image is None:
        return None, "无法读取图片", None, None

    enhanced_img = enhance_image_for_plate(image)

    try:
        # 检测
        candidates = _detect_plates_hyperlpr(enhanced_img, scales=(1.0, 0.8, 1.2))
        if not candidates:
            return None, "未识别到车牌", None, None

        # 取置信度最高
        best = max(candidates, key=lambda x: float(x.get('conf', 0.0)))

        plate_str = postprocess_plate(best.get('plate', '') or '')
        plate_str = correct_plate_string(plate_str)

        mapped_bbox = _map_bbox_to_original(best.get('bbox'), best.get('scale', 1.0), enhanced_img.shape)

        plate_color = get_plate_color(enhanced_img, mapped_bbox)

        # 特殊车牌类型判断
        plate_type = "普通车牌"
        if re.match(r'^[A-Z]+\d+$', plate_str):
            plate_type = "军用白牌"
        else:
            for char, type_name in SPECIAL_PLATE_TYPES.items():
                if char in plate_str:
                    plate_type = type_name
                    break

        if plate_type == "军用白牌" or (isinstance(plate_type, str) and "警" in plate_type):
            plate_color = "白色"

        valid_format, expected_fmt, fmt_note = check_plate_number_format(plate_str, plate_color)
        if not valid_format:
            return None, "识别失败(异常车牌)", None, None

        return plate_str, "识别成功", plate_color, plate_type
    except Exception as e:
        return None, f"识别错误：{str(e)}", None, None

def batch_process(folder_path):
    """批量处理文件夹中的图片"""
    image_paths = []
    for ext in ('*.jpg', '*.jpeg', '*.png', '*.bmp'):
        image_paths.extend(glob.glob(os.path.join(folder_path, ext)))
    
    if not image_paths:
        print("未找到图片文件！")
        return []

    results = []
    for img_path in image_paths:
        img_name = os.path.basename(img_path)
        plate, status, color, plate_type = recognize_plate(img_path)
        # 如果最终判定为军用白牌，所属地区标记为军区
        if plate_type == "军用白牌":
            location = "军区"
        else:
            location = PROVINCE_MAP.get(plate[0], "未知") if plate else "未知"
        
        results.append({
            "图片名称": img_name,
            "识别结果": plate or "未识别",
            "车牌颜色": color or "未知",
            "车牌类型": plate_type or "未知",
            "所属地区": location,
            "状态": status
        })
    
    return results

if __name__ == "__main__":
    target_folder = r"E:\HuaweiMoveData\Users\yelan\Pictures\data_jpg"  # 路径
    results = batch_process(target_folder)
    # 简化输出：固定列宽，使用简单字符串长度对齐（兼容性更好）
    COLS = {
        'name': 24,
        'plate': 14,
        'color': 10,
        'type': 14,
        'location': 12,
        'status': 24
    }

    def fmt_simple(s, w):
        s = '' if s is None else str(s)
        if len(s) > w:
            return s[:w-1] + '…'
        return s.ljust(w)

    sep = ' | '
    header = sep.join([
        fmt_simple('图片名称', COLS['name']),
        fmt_simple('识别结果', COLS['plate']),
        fmt_simple('颜色', COLS['color']),
        fmt_simple('类型', COLS['type']),
        fmt_simple('所属地区', COLS['location']),
        fmt_simple('状态', COLS['status'])
    ])

    total_width = sum(COLS.values()) + len(sep) * 5
    print('=' * total_width)
    print(header)
    print('-' * total_width)
    for res in results:
        print(sep.join([
            fmt_simple(res.get('图片名称') or '', COLS['name']),
            fmt_simple(res.get('识别结果') or '', COLS['plate']),
            fmt_simple(res.get('车牌颜色') or '', COLS['color']),
            fmt_simple(res.get('车牌类型') or '', COLS['type']),
            fmt_simple(res.get('所属地区') or '', COLS['location']),
            fmt_simple(res.get('状态') or '', COLS['status'])
        ]))

    # 统计分析（判断是否成功）
    def is_success(st):
        return isinstance(st, str) and st.startswith('识别成功')

    success_count = sum(1 for r in results if is_success(r.get('状态')))
    color_stats = {}
    type_stats = {}
    for res in results:
        if is_success(res.get('状态')):
            color_stats[res.get('车牌颜色', '未知')] = color_stats.get(res.get('车牌颜色', '未知'), 0) + 1
            type_stats[res.get('车牌类型', '未知')] = type_stats.get(res.get('车牌类型', '未知'), 0) + 1

    print('\n统计结果：')
    print(f"总图片数：{len(results)}")
    print(f"识别成功率：{(success_count/len(results) if len(results)>0 else 0):.1%}")
    print('\n颜色分布：')
    if success_count == 0:
        print('  无识别成功结果')
    else:
        for color, count in color_stats.items():
            print(f"  {color}: {count}张 ({count/success_count:.1%})")
    print('\n类型分布：')
    if success_count == 0:
        print('  无识别成功结果')
    else:
        for ptype, count in type_stats.items():
            print(f"  {ptype}: {count}张 ({count/success_count:.1%})")