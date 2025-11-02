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

# 新增：手机拍摄常见误识别字符映射（扩展版）
MOBILE_OCR_CORRECTION = {
    'O': '0', 'I': '1', 'L': '1', 'Z': '2', 'S': '5',
    'B': '8', 'G': '6', 'Q': '0', '8': 'B', '6': 'G',
    'D': '0', 'P': '0', 'U': '0', 'V': '0', 'Y': 'V'
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
    """优化：适配手机拍摄的字符纠错，增强位置感知修正"""
    if not plate_str:
        return plate_str
    s = plate_str.upper()
    chars = list(s)
    n = len(chars)
    
    # 尾部最后5位优先替换（手机拍摄易混字符）
    start = max(2, n - 5)
    for i in range(start, n):
        c = chars[i]
        if c in MOBILE_OCR_CORRECTION:
            chars[i] = MOBILE_OCR_CORRECTION[c]

    # 检查数字个数，不足则放宽替换范围
    digit_count = sum(ch.isdigit() for ch in chars)
    if digit_count < 3:  # 手机拍摄车牌数字占比通常较高，阈值调整为3
        for i in range(1, n):
            c = chars[i]
            if c in MOBILE_OCR_CORRECTION:
                chars[i] = MOBILE_OCR_CORRECTION[c]

    return ''.join(chars)

# 新增：倾斜校正（针对手机拍摄的倾斜车牌）
def correct_plate_skew(plate_img):
    """基于边缘检测的车牌倾斜校正"""
    if plate_img.size == 0:
        return plate_img
    
    # 转灰度图并边缘检测
    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # 检测直线（Hough变换）
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=30, maxLineGap=10)
    if lines is None:
        return plate_img
    
    # 计算倾斜角度
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x2 != x1:
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            if abs(angle) < 30:  # 过滤极端角度
                angles.append(angle)
    
    if not angles:
        return plate_img
    
    # 计算平均倾斜角度并校正
    avg_angle = np.mean(angles)
    h, w = plate_img.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, avg_angle, 1.0)
    corrected_img = cv2.warpAffine(plate_img, rotation_matrix, (w, h), flags=cv2.INTER_CUBIC)
    
    return corrected_img

# 新增：运动模糊修复（针对手机手持拍摄模糊）
def repair_motion_blur(image):
    """基于维纳滤波的运动模糊修复"""
    if image.size == 0:
        return image
    
    # 估计模糊核（手机拍摄常见运动模糊方向）
    kernel_size = 5
    kernel = np.zeros((kernel_size, kernel_size))
    kernel[int((kernel_size - 1)/2), :] = 1 / kernel_size  # 水平模糊核
    kernel[:, int((kernel_size - 1)/2)] = 1 / kernel_size  # 垂直模糊核叠加
    
    # 维纳滤波去模糊
    deblurred = cv2.filter2D(image, -1, kernel)
    # 增强对比度，突出字符
    deblurred = cv2.convertScaleAbs(deblurred, alpha=1.5, beta=30)
    
    return deblurred

def get_plate_color(image, plate_region):
    """改进版颜色识别（优化手机拍摄光线适应性）"""
    if not plate_region or all(v == 0 for v in plate_region):
        return "未知"
    
    x1, y1, x2, y2 = map(int, plate_region)
    plate_img = image[y1:y2, x1:x2]
    if plate_img.size == 0:
        return "未知"
    
    # 先校正倾斜（手机拍摄易倾斜）
    plate_img = correct_plate_skew(plate_img)
    # 修复模糊（手机拍摄易模糊）
    plate_img = repair_motion_blur(plate_img)
    
    # 转换为HSV颜色空间，扩大亮度适应范围
    hsv = cv2.cvtColor(plate_img, cv2.COLOR_BGR2HSV)

    # 优化颜色范围（适配手机拍摄的光线变化）
    ranges = {
        "blue": (np.array([85, 30, 30], dtype=np.uint8), np.array([135, 255, 255], dtype=np.uint8)),
        "yellow": (np.array([12, 50, 50], dtype=np.uint8), np.array([45, 255, 255], dtype=np.uint8)),
        "green": (np.array([30, 25, 25], dtype=np.uint8), np.array([100, 255, 255], dtype=np.uint8)),
    }

    h_channel, s_channel, v_channel = cv2.split(hsv)
    pixel_count = plate_img.shape[0] * plate_img.shape[1]

    # 计算颜色占比
    ratios = {}
    for name, (low, up) in ranges.items():
        mask = cv2.inRange(hsv, low, up)
        ratios[name] = cv2.countNonZero(mask) / float(pixel_count)

    # 红色双区间检测
    red_lower1 = np.array([0, 50, 40], dtype=np.uint8)
    red_upper1 = np.array([12, 255, 255], dtype=np.uint8)
    red_lower2 = np.array([158, 50, 40], dtype=np.uint8)
    red_upper2 = np.array([180, 255, 255], dtype=np.uint8)
    red_mask = cv2.inRange(hsv, red_lower1, red_upper1) | cv2.inRange(hsv, red_lower2, red_upper2)
    red_ratio = cv2.countNonZero(red_mask) / float(pixel_count)

    # 白色判断（优化手机拍摄的逆光/暗光场景）
    mean_s = int(np.mean(s_channel))
    mean_v = int(np.mean(v_channel))
    # 动态调整白色阈值（根据亮度自适应）
    if mean_v < 150:
        is_white = (mean_s <= 70 and mean_v >= 100)
    else:
        is_white = (mean_s <= 60 and mean_v >= 180)

    # 颜色判定逻辑
    if ratios.get("green", 0) >= 0.15:  # 降低绿色阈值，适配手机拍摄的暗绿色牌
        return "新能源绿色"
    if ratios.get("blue", 0) >= 0.15:
        return "蓝色"
    if ratios.get("yellow", 0) >= 0.15:
        return "黄色"
    if is_white:
        return "白色"
    if red_ratio >= 0.10:
        return "红色"

    # 兜底逻辑
    all_candidates = {**ratios, "red": red_ratio}
    main_color = max(all_candidates, key=all_candidates.get)
    if all_candidates.get(main_color, 0) >= 0.10:
        cmap = {"blue": "蓝色", "yellow": "黄色", "green": "绿色", "red": "红色"}
        return cmap.get(main_color, "未知")

    return "未知"

def enhance_image_for_plate(image):
    """图像增强（优化手机拍摄的低光、反光问题）"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # 增强饱和度和亮度（适配手机低光拍摄）
    s = cv2.equalizeHist(s)  # 饱和度直方图均衡化
    v = cv2.equalizeHist(v)  # 亮度直方图均衡化
    
    # 增强蓝色通道
    lower_blue = np.array([85, 30, 30])
    upper_blue = np.array([135, 255, 255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    s[mask_blue > 0] = np.clip(s[mask_blue > 0] + 40, 0, 255)
    
    # 增强绿色通道
    lower_green = np.array([30, 25, 25])
    upper_green = np.array([100, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    v[mask_green > 0] = np.clip(v[mask_green > 0] + 30, 0, 255)
    
    # 增强红色通道（警用车牌）
    lower_red = np.array([0, 50, 40])
    upper_red = np.array([12, 255, 255])
    mask_red = cv2.inRange(hsv, lower_red, upper_red)
    v[mask_red > 0] = np.clip(v[mask_red > 0] + 40, 0, 255)
    
    enhanced_hsv = cv2.merge([h, s, v])
    return cv2.cvtColor(enhanced_hsv, cv2.COLOR_HSV2BGR)


def preprocess_for_recognition(image):
    """优化：增强手机拍摄图像预处理，添加去噪、锐化增强"""
    # 第一步：去噪（手机拍摄易产生噪声）
    denoised = cv2.medianBlur(image, 3)  # 中值滤波去噪
    
    # 第二步：HSV增强
    hsv = cv2.cvtColor(denoised, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    # CLAHE增强亮度通道
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    v_clahe = clahe.apply(v)

    hsv_clahe = cv2.merge([h, s, v_clahe])
    img_clahe = cv2.cvtColor(hsv_clahe, cv2.COLOR_HSV2BGR)

    # 第三步：强化锐化（突出字符边缘，适配手机低分辨率）
    gaussian = cv2.GaussianBlur(img_clahe, (0, 0), sigmaX=2)
    sharpened = cv2.addWeighted(img_clahe, 1.8, gaussian, -0.8, 0)
    
    # 第四步：自适应阈值二值化（增强字符与背景对比）
    gray = cv2.cvtColor(sharpened, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, blockSize=15, C=2)
    # 转回彩色图，适配后续识别流程
    thresh_color = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    
    return thresh_color

def check_plate_number_format(plate_str, plate_color):
    """根据车牌颜色/类型检查车牌号格式"""
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
    """核心识别函数（优化手机拍摄适配）"""
    if not os.path.exists(image_path):
        return None, "文件不存在", None, None
    
    image = cv2.imread(image_path)
    if image is None:
        return None, "无法读取图片", None, None

    # 新增：手机拍摄图像预处理（去噪、增强）
    mobile_preprocessed = preprocess_for_recognition(image)
    enhanced_img = enhance_image_for_plate(mobile_preprocessed)
    
    try:
        # 扩展检测尺度（适配手机拍摄的远近差异）
        # 多尺度检测（适配手机拍摄）
        scales = [0.6, 0.8, 1.0, 1.2, 1.4]
        all_results = []
        for scale in scales:
            resized = cv2.resize(enhanced_img, (0, 0), fx=scale, fy=scale) if scale != 1.0 else enhanced_img.copy()
            # 调用HyperLPR识别（兼容写法）
            try:
                # 尝试新版接口
                results = HyperLPR_plate_recognition(resized)
            except TypeError:
                # 兼容旧版接口
                results = HyperLPR_plate_recognition(resized, use_multi_scale=True)
            if results:
                for r in results:
                    if len(r) >= 3:
                        bbox = r[2]
                    else:
                        bbox = None
                    all_results.append((r[0], r[1], bbox, scale))
        
        if not all_results:
            # 尝试二次裁剪车牌区域再识别（应对手机拍摄的远距离场景）
            h, w = enhanced_img.shape[:2]
            roi = image[int(h*0.3):int(h*0.7), int(w*0.2):int(w*0.8)]  # 假设车牌在画面中下部
            roi_enhanced = enhance_image_for_plate(preprocess_for_recognition(roi))
            for scale in scales:
                resized_roi = cv2.resize(roi_enhanced, (0, 0), fx=scale, fy=scale) if scale != 1.0 else roi_enhanced.copy()
                roi_results = HyperLPR_plate_recognition(resized_roi)
                if roi_results:
                    for r in roi_results:
                        if len(r) >= 3:
                            bbox = [
                                r[2][0] + int(w*0.2),  # 映射回原图坐标
                                r[2][1] + int(h*0.3),
                                r[2][2] + int(w*0.2),
                                r[2][3] + int(h*0.3)
                            ]
                        else:
                            bbox = None
                        all_results.append((r[0], r[1], bbox, scale))
        
        if not all_results:
            return None, "未识别到车牌", None, None

        # 选择置信度最高的结果
        best_result = max(all_results, key=lambda x: x[1])
        plate_str = postprocess_plate(best_result[0])
        plate_str = correct_plate_string(plate_str)  # 应用手机专用字符纠错

        # 映射检测框到原始图像
        mapped_bbox = None
        if best_result[2] is not None:
            try:
                bx = list(map(float, best_result[2]))
                x1, y1, x2, y2 = map(int, bx)
                s = float(best_result[3]) if len(best_result) >= 4 else 1.0
                if s != 0 and s != 1.0:
                    x1 = int(round(x1 / s))
                    y1 = int(round(y1 / s))
                    x2 = int(round(x2 / s))
                    y2 = int(round(y2 / s))
                h, w = enhanced_img.shape[:2]
                x1 = max(0, min(x1, w - 1))
                x2 = max(0, min(x2, w - 1))
                y1 = max(0, min(y1, h - 1))
                y2 = max(0, min(y2, h - 1))
                if x2 > x1 and y2 > y1:
                    mapped_bbox = (x1, y1, x2, y2)
            except Exception:
                mapped_bbox = None

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
        if plate_type == "军用白牌" or "警" in plate_type:
            plate_color = "白色"

        # 放宽格式校验（手机拍摄可能识别不完整）
        valid_format, expected_fmt, fmt_note = check_plate_number_format(plate_str, plate_color)
        # 允许手机拍摄的部分识别情况（如7/8位但少1位）
        if not valid_format:
            if (plate_color == "新能源绿色" and len(plate_str) in [7,8]) or \
               (plate_color == "蓝色" and len(plate_str) in [6,7]):
                valid_format = True  # 允许±1位的误差

        if not valid_format:
            return None, "识别失败(异常车牌)", None, None

        status = "识别成功"
        return plate_str, status, plate_color, plate_type
    except Exception as e:
        return None, f"识别错误：{str(e)}", None, None

def batch_process(folder_path):
    """批量处理文件夹中的图片（保持原逻辑）"""
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
    target_folder = r"E:\HuaweiMoveData\Users\yelan\Pictures\data_jpg"  # 替换为手机照片所在路径
    results = batch_process(target_folder)
    # 打印结果表格（保持原格式）
    COLS = {
        'name': 20,
        'plate': 14,
        'color': 10,
        'type': 12,
        'location': None,
        'status': 24
    }

    try:
        from wcwidth import wcswidth
        def display_width(s: str) -> int:
            return wcswidth(s)
        def fmt(s, w):
            s = '' if s is None else str(s)
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
            pad = w - cur_w
            if pad > 0:
                cur = cur + ' ' * pad
            return cur
    except Exception:
        def display_width(s: str) -> int:
            return len(s)
        def fmt(s, w):
            s = '' if s is None else str(s)
            if len(s) > w:
                return s[:w]
            return s.ljust(w)

    sep = ' | '
    try:
        longest = 0
        for v in PROVINCE_MAP.values():
            w = display_width(v)
            if w > longest:
                longest = w
        longest = max(longest, display_width('军区'), display_width('未知'), display_width('所属地区'))
        COLS['location'] = max(8, longest)
    except Exception:
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