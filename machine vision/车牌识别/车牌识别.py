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
    """修正字符错误并识别特殊车牌类型"""
    plate_str = re.sub(r'[\s·-]', '', plate_str).upper()
    
    # 字符合法性校验
    valid_chars = {
        '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
        '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
        'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E',
        'F': 'F', 'G': 'G', 'H': 'H', 'J': 'J', 'K': 'K',
        'L': 'L', 'M': 'M', 'N': 'N', 'P': 'P', 'Q': 'Q',
        'R': 'R', 'S': 'S', 'T': 'T', 'U': 'U', 'V': 'V',
        'W': 'W', 'X': 'X', 'Y': 'Y', 'Z': 'Z',
        '藏': '藏', '川': '川', '鄂': '鄂', '甘': '甘', '赣': '赣',
        '贵': '贵', '桂': '桂', '黑': '黑', '沪': '沪', '吉': '吉',
        '冀': '冀', '津': '津', '晋': '晋', '京': '京', '辽': '辽',
        '鲁': '鲁', '蒙': '蒙', '闽': '闽', '宁': '宁', '青': '青',
        '琼': '琼', '陕': '陕', '苏': '苏', '皖': '皖', '湘': '湘',
        '新': '新', '渝': '渝', '豫': '豫', '云': '云', '粤': '粤',
        '浙': '浙', '港': '港', '澳': '澳', '台': '台', '警': '警',
        '学': '学', '领': '领', '使': '使'
    }
    filtered = [c for c in plate_str if c in valid_chars]
    return ''.join(filtered)


def correct_plate_string(plate_str):
    """对常见 OCR 误识别进行位置感知修正。
    - 在车牌尾部（最后5位）优先把易混字符替换为数字：O->0, I/L->1, Z->2, S->5, B->8, G->6
    - 如果替换后数字太少，会做一次更宽松的替换。
    保持首位中文省份字符不变。
    """
    if not plate_str:
        return plate_str
    s = plate_str.upper()
    # 保留中文首字符（如果是中文字符）
    chars = list(s)
    mapping = {'O': '0','I':'i6'}

    n = len(chars)
    # 对尾部最后5位先做保守替换
    start = max(2, n - 5)  # 从第二位或倒数第五位开始，避免修改省份简称
    for i in range(start, n):
        c = chars[i]
        if c in mapping:
            chars[i] = mapping[c]

    # 检查数字个数，如数字太少则放宽替换范围
    digit_count = sum(ch.isdigit() for ch in chars)
    if digit_count < 2:
        for i in range(1, n):
            c = chars[i]
            if c in mapping:
                chars[i] = mapping[c]
        digit_count = sum(ch.isdigit() for ch in chars)

    return ''.join(chars)

def get_plate_color(image, plate_region):
    """改进版颜色识别（支持警用白牌和新能源绿牌）"""
    if not plate_region or all(v == 0 for v in plate_region):
        return "未知"
    
    x1, y1, x2, y2 = map(int, plate_region)
    plate_img = image[y1:y2, x1:x2]
    if plate_img.size == 0:
        return "未知"
    
    # 转换为HSV颜色空间
    hsv = cv2.cvtColor(plate_img, cv2.COLOR_BGR2HSV)

    # 颜色范围定义（针对实际情况做出更稳健的范围）
    ranges = {
        "blue": (np.array([90, 40, 40], dtype=np.uint8), np.array([130, 255, 255], dtype=np.uint8)),
        "yellow": (np.array([15, 60, 60], dtype=np.uint8), np.array([40, 255, 255], dtype=np.uint8)),
        # 绿色适当放宽，覆盖深浅不同的新能源绿
        "green": (np.array([35, 30, 30], dtype=np.uint8), np.array([95, 255, 255], dtype=np.uint8)),
    }

    h_channel, s_channel, v_channel = cv2.split(hsv)
    pixel_count = plate_img.shape[0] * plate_img.shape[1]

    # 计算蓝/黄/绿三色的像素占比
    ratios = {}
    for name, (low, up) in ranges.items():
        mask = cv2.inRange(hsv, low, up)
        ratios[name] = cv2.countNonZero(mask) / float(pixel_count)

    # 红色需要使用两个区间（低端和高端）
    red_lower1 = np.array([0, 60, 50], dtype=np.uint8)
    red_upper1 = np.array([10, 255, 255], dtype=np.uint8)
    red_lower2 = np.array([160, 60, 50], dtype=np.uint8)
    red_upper2 = np.array([180, 255, 255], dtype=np.uint8)
    red_mask = cv2.inRange(hsv, red_lower1, red_upper1) | cv2.inRange(hsv, red_lower2, red_upper2)
    red_ratio = cv2.countNonZero(red_mask) / float(pixel_count)

    # 白色判断：通常白色 S 低且 V 高，我们用统计量而不是仅靠 inRange
    mean_s = int(np.mean(s_channel))
    mean_v = int(np.mean(v_channel))
    is_white = (mean_s <= 60 and mean_v >= 180)

    # 判定优先级：新能源绿（绿色占比较高） -> 蓝/黄 -> 白（含警用白） -> 红（特殊）
    # 绿色阈值可以相对较低以适应不同亮度环境
    if ratios.get("green", 0) >= 0.18:
        return "新能源绿色"

    # 蓝色与黄色判断
    if ratios.get("blue", 0) >= 0.18:
        return "蓝色"
    if ratios.get("yellow", 0) >= 0.18:
        return "黄色"

    # 白色：如果整体色度较低且亮度高，则为白色，进一步检测警用白色（红字）
    if is_white:
        # 不再区分警用白色与普通白色，统一返回白色
        return "白色"

    # 红色明显且不属于白/绿/蓝/黄，则优先判红
    if red_ratio >= 0.12:
        return "红色"

    # 兜底：如果某一颜色比率最高且超过较低阈值，则返回对应颜色
    all_candidates = {**ratios, "red": red_ratio}
    main_color = max(all_candidates, key=all_candidates.get)
    if all_candidates.get(main_color, 0) >= 0.12:
        cmap = {"blue": "蓝色", "yellow": "黄色", "green": "绿色", "red": "红色"}
        return cmap.get(main_color, "未知")

    return "未知"

def enhance_image_for_plate(image):
    """图像增强（优化颜色通道）"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # 增强蓝色通道（蓝牌）
    lower_blue = np.array([90, 40, 40])
    upper_blue = np.array([130, 255, 255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    s[mask_blue > 0] = np.clip(s[mask_blue > 0] + 30, 0, 255)
    
    # 增强绿色通道（新能源车牌）
    lower_green = np.array([35, 40, 40])  # 扩展绿色范围[7](@ref)
    upper_green = np.array([100, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    v[mask_green > 0] = np.clip(v[mask_green > 0] + 20, 0, 255)
    
    # 增强红色通道（警用车牌）
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    mask_red = cv2.inRange(hsv, lower_red, upper_red)
    v[mask_red > 0] = np.clip(v[mask_red > 0] + 30, 0, 255)
    
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

def recognize_plate(image_path):
    """核心识别函数"""
    if not os.path.exists(image_path):
        return None, "文件不存在", None, None
    
    image = cv2.imread(image_path)
    if image is None:
        return None, "无法读取图片", None, None

    enhanced_img = enhance_image_for_plate(image)
    
    try:
        # 多尺度检测（0.8x, 1.0x, 1.2x）
        # 为了后续用原图做颜色判断，这里记录每个检测结果对应的 scale
        scales = [0.8, 1.0, 1.2]
        all_results = []
        for scale in scales:
            resized = cv2.resize(enhanced_img, (0, 0), fx=scale, fy=scale) if scale != 1.0 else enhanced_img.copy()
            results = HyperLPR_plate_recognition(resized)
            if results:
                # results 中每项通常为 (plate_str, confidence, bbox)
                # 我们将其转为 (plate_str, confidence, bbox, scale)
                for r in results:
                    if len(r) >= 3:
                        bbox = r[2]
                    else:
                        bbox = None
                    all_results.append((r[0], r[1], bbox, scale))
        
        if not all_results:
            return None, "未识别到车牌", None, None

        # 选择置信度最高的结果（注意 all_results 中元素为 (plate, conf, bbox, scale)）
        best_result = max(all_results, key=lambda x: x[1])
        plate_str = postprocess_plate(best_result[0])
        # 对车牌文本做常见 OCR 误识别修正
        plate_str = correct_plate_string(plate_str)

        # 将检测框按检测时的 scale 映射回原始图像（enhanced_img）坐标
        mapped_bbox = None
        if best_result[2] is not None:
            try:
                bx = list(map(float, best_result[2]))
                # bbox 可能为 [x1, y1, x2, y2]
                x1, y1, x2, y2 = map(int, bx)
                s = float(best_result[3]) if len(best_result) >= 4 else 1.0
                if s != 0 and s != 1.0:
                    x1 = int(round(x1 / s))
                    y1 = int(round(y1 / s))
                    x2 = int(round(x2 / s))
                    y2 = int(round(y2 / s))
                # 边界裁剪，避免越界
                h, w = enhanced_img.shape[:2]
                x1 = max(0, min(x1, w - 1))
                x2 = max(0, min(x2, w - 1))
                y1 = max(0, min(y1, h - 1))
                y2 = max(0, min(y2, h - 1))
                # 确保有效框
                if x2 > x1 and y2 > y1:
                    mapped_bbox = (x1, y1, x2, y2)
            except Exception:
                mapped_bbox = None

        plate_color = get_plate_color(enhanced_img, mapped_bbox)
        
        # 特殊车牌类型判断
        plate_type = "普通车牌"

        # 规则：如果整个车牌由英文开头随后全为数字（例如 'ABC1234' 或 'WJ12345'），判定为军用白牌
        # 只在识别到纯英文+数字时生效，避免与带中文简称的民用牌冲突
        if re.match(r'^[A-Z]+\d+$', plate_str):
            plate_type = "军用白牌"
        else:
            for char, type_name in SPECIAL_PLATE_TYPES.items():
                if char in plate_str:
                    plate_type = type_name
                    break
        # 规则：一旦判定为军用白牌或警用（type 包含'警'），则车牌颜色一定为白色
        if plate_type == "军用白牌" or (isinstance(plate_type, str) and "警" in plate_type):
            plate_color = "白色"

        # 检查车牌号格式（新能源 2+6 -> 总长8；蓝牌 2+5 -> 总长7）
        valid_format, expected_fmt, fmt_note = check_plate_number_format(plate_str, plate_color)

        if not valid_format:
            # 不展示错误车牌，提示识别失败（异常车牌）
            return None, "识别失败(异常车牌)", None, None

        status = "识别成功"
        return plate_str, status, plate_color, plate_type
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
    target_folder = r"E:\HuaweiMoveData\Users\yelan\Pictures\data_jpg"  # 替换为实际路径
    results = batch_process(target_folder)
    # 打印结果表格（固定列宽，超长截断）
    COLS = {
        'name': 20,
        'plate': 14,
        'color': 10,
        'type': 12,
        'location': None,  # 之后根据 PROVINCE_MAP 计算
        'status': 24
    }

    # 尝试按显示宽度对齐（考虑中文为全角），优先使用 wcwidth
    try:
        from wcwidth import wcswidth
        def display_width(s: str) -> int:
            return wcswidth(s)

        def fmt(s, w):
            s = '' if s is None else str(s)
            # 截断使显示宽度不超过 w
            cur = ''
            cur_w = 0
            for ch in s:
                ch_w = wcswidth(ch)
                if ch_w < 0:
                    ch_w = 1
                if cur_w + ch_w > w:
                    break
                cur += ch
                cur_w += ch_w
            # 填充空格到宽度 w
            pad = w - cur_w
            if pad > 0:
                cur = cur + ' ' * pad
            return cur
    except Exception:
        # wcwidth 未安装或不可用，回退到简单字符长度对齐
        def display_width(s: str) -> int:
            return len(s)

        def fmt(s, w):
            s = '' if s is None else str(s)
            if len(s) > w:
                return s[:w]
            return s.ljust(w)

    sep = ' | '

    # 根据省份映射表（PROVINCE_MAP）中最长的地区名称，确定 location 列宽
    try:
        # display_width 在上文中已定义（使用 wcwidth 或回退）
        longest = 0
        for v in PROVINCE_MAP.values():
            w = display_width(v)
            if w > longest:
                longest = w
        # 考虑到可能出现的特殊值
        longest = max(longest, display_width('军区'), display_width('未知'), display_width('所属地区'))
        COLS['location'] = max(8, longest)
    except Exception:
        # 兜底为固定宽度
        COLS['location'] = 12

    header = sep.join([
        fmt('图片名称', COLS['name']),
        fmt('识别结果', COLS['plate']),
        fmt('颜色', COLS['color']),
        fmt('类型', COLS['type']),
        fmt('所属地区', COLS['location']),
        fmt('状态', COLS['status'])
    ])

    print('=' * (sum(COLS.values()) + len(sep) * 5))
    print(header)
    print('-' * (sum(COLS.values()) + len(sep) * 5))
    for res in results:
        name = res.get('图片名称') or ''
        plate = res.get('识别结果') or ''
        color = res.get('车牌颜色') or ''
        ptype = res.get('车牌类型') or ''
        location = res.get('所属地区') or ''
        status = res.get('状态') or ''

        print(sep.join([
            fmt(name, COLS['name']),
            fmt(plate, COLS['plate']),
            fmt(color, COLS['color']),
            fmt(ptype, COLS['type']),
            fmt(location, COLS['location']),
            fmt(status, COLS['status'])
        ]))

    # 统计分析（使用 helper 判断是否成功）
    def is_success(st):
        return isinstance(st, str) and st.startswith('识别成功')

    success_count = sum(1 for r in results if is_success(r.get('状态')))
    color_stats = {}
    type_stats = {}
    for res in results:
        if is_success(res.get('状态')):
            color_stats[res['车牌颜色']] = color_stats.get(res['车牌颜色'], 0) + 1
            type_stats[res['车牌类型']] = type_stats.get(res['车牌类型'], 0) + 1

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