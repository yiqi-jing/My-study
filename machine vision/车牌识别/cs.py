import os
import sys
import re
import numpy as np
import glob
import cv2
from hyperlpr import HyperLPR_plate_recognition

# 解决numpy兼容问题
if not hasattr(np, 'int'):
    np.int = np.int64

# 省份简称映射表
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

def postprocess_plate(plate_str):
    """修正字符错误，统一格式"""
    plate_str = re.sub(r'[\s·-]', '', plate_str).upper()  # 去除分隔符
    char_correction = {
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
        '浙': '浙', '港': '港', '澳': '澳', '台': '台'
    }
    # 过滤无效字符
    filtered = [c for c in plate_str if c in char_correction]
    return ''.join(filtered)

def get_plate_color(image, plate_region):
    """分析车牌颜色"""
    if not plate_region.any():
        return "未知"
    
    # 提取车牌区域
    x1, y1, x2, y2 = map(int, plate_region)
    plate_img = image[y1:y2, x1:x2]
    if plate_img.size == 0:
        return "未知"
    
    # 转换为HSV颜色空间
    hsv = cv2.cvtColor(plate_img, cv2.COLOR_BGR2HSV)
    
    # 定义颜色范围
    blue_lower = np.array([90, 40, 40])
    blue_upper = np.array([130, 255, 255])
    yellow_lower = np.array([20, 100, 100])
    yellow_upper = np.array([30, 255, 255])
    green_lower = np.array([40, 40, 50])
    green_upper = np.array([80, 255, 255])
    white_lower = np.array([0, 0, 200])
    white_upper = np.array([180, 30, 255])
    
    # 计算颜色像素占比
    blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
    yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
    green_mask = cv2.inRange(hsv, green_lower, green_upper)
    white_mask = cv2.inRange(hsv, white_lower, white_upper)
    
    total_pixels = plate_img.shape[0] * plate_img.shape[1]
    if total_pixels == 0:
        return "未知"
    
    blue_ratio = cv2.countNonZero(blue_mask) / total_pixels
    yellow_ratio = cv2.countNonZero(yellow_mask) / total_pixels
    green_ratio = cv2.countNonZero(green_mask) / total_pixels
    white_ratio = cv2.countNonZero(white_mask) / total_pixels
    
    # 确定主要颜色
    max_ratio = max(blue_ratio, yellow_ratio, green_ratio, white_ratio)
    if max_ratio < 0.2:  # 颜色特征不明显
        return "未知"
    
    if max_ratio == blue_ratio:
        return "蓝色"
    elif max_ratio == yellow_ratio:
        return "黄色"
    elif max_ratio == green_ratio:
        return "绿色"
    else:
        return "白色"

def get_plate_region(plate_info):
    """从识别结果中提取车牌位置信息"""
    if len(plate_info) >= 3 and isinstance(plate_info[2], list) and len(plate_info[2]) == 4:
        return plate_info[2]
    return [0, 0, 0, 0]

def get_plate_location(plate_str):
    """根据车牌首字符判断所属地区"""
    if not plate_str or len(plate_str) < 1:
        return "未知"
    first_char = plate_str[0]
    return PROVINCE_MAP.get(first_char, f"未知({first_char})")

def enhance_image_for_plate(image):
    """对车牌区域进行颜色和对比度增强"""
    # 转换为HSV空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # 增强蓝色通道（蓝牌）
    lower_blue = np.array([90, 40, 40])
    upper_blue = np.array([130, 255, 255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    s[mask_blue > 0] = np.clip(s[mask_blue > 0] + 30, 0, 255)
    
    # 增强绿色通道（新能源绿牌）
    lower_green = np.array([40, 40, 50])
    upper_green = np.array([80, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    v[mask_green > 0] = np.clip(v[mask_green > 0] + 20, 0, 255)
    
    # 合并通道并转回BGR
    enhanced_hsv = cv2.merge([h, s, v])
    return cv2.cvtColor(enhanced_hsv, cv2.COLOR_HSV2BGR)

def recognize_plate(image_path):
    if not os.path.exists(image_path):
        return None, "文件不存在", None
    
    if not image_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        return None, "非图片格式", None

    image = cv2.imread(image_path)
    if image is None:
        return None, "无法读取图片", None

    # 增强图像特征
    enhanced_img = enhance_image_for_plate(image)
    
    try:
        # 多尺度检测（针对不同大小的车牌）
        scales = [0.8, 1.0, 1.2]
        all_results = []
        for scale in scales:
            if scale != 1.0:
                resized = cv2.resize(enhanced_img, (0, 0), fx=scale, fy=scale)
            else:
                resized = enhanced_img.copy()
            results = HyperLPR_plate_recognition(resized)
            if results:
                all_results.extend(results)
        
        if not all_results:
            return None, "未识别到车牌", None

        # 选择置信度最高的结果
        best_result = max(all_results, key=lambda x: x[1])
        merged_str = best_result[0]
        processed_plate = postprocess_plate(merged_str)
        
        # 获取车牌颜色
        plate_region = get_plate_region(best_result)
        plate_color = get_plate_color(enhanced_img, plate_region)
        
        return processed_plate, "识别成功", plate_color
    except Exception as e:
        return None, f"识别错误：{str(e)}", None

def get_image_paths(folder):
    paths = []
    for ext in ('.jpg', '.jpeg', '.png', '.bmp'):
        paths.extend(glob.glob(os.path.join(folder, f'*{ext}'), recursive=False))
        paths.extend(glob.glob(os.path.join(folder, f'*{ext.upper()}'), recursive=False))
    return sorted(list(set(paths)))

if __name__ == "__main__":
    # 请修改为你的图片文件夹路径
    target_folder = r"E:\HuaweiMoveData\Users\yelan\Pictures\data_jpg"  # 替换为你的图片路径
    all_images = get_image_paths(target_folder)

    if not all_images:
        print("未找到图片文件！")
        sys.exit(1)

    overall_results = []
    print(f"发现 {len(all_images)} 张图片，开始识别...\n")

    for img_path in all_images:
        img_name = os.path.basename(img_path)
        plate, status, color = recognize_plate(img_path)
        
        # 分析所属地
        location = get_plate_location(plate) if plate else "未知"
        
        overall_results.append({
            "图片名称": img_name,
            "识别结果": plate if plate else "未识别",
            "车牌颜色": color if color else "未知",
            "所属地区": location,
            "状态": status
        })

    # 输出结果表格
    print("=" * 80)
    print(f"{'图片名称':<30} | {'识别结果':<20} | {'颜色':<8} | {'所属地区':<15} | 状态")
    print("-" * 80)
    for res in overall_results:
        print(f"{res['图片名称']:<30} | {res['识别结果']:<20} | {res['车牌颜色']:<8} | {res['所属地区']:<15} | {res['状态']}")
    print("=" * 80)

    # 统计分析
    total = len(all_images)
    success = sum(1 for res in overall_results if res['状态'] == "识别成功")
    
    # 颜色统计
    color_stats = {}
    for res in overall_results:
        if res['状态'] == "识别成功":
            color = res['车牌颜色']
            color_stats[color] = color_stats.get(color, 0) + 1
    
    # 地区统计
    location_stats = {}
    for res in overall_results:
        if res['状态'] == "识别成功" and res['所属地区'] != "未知":
            loc = res['所属地区']
            location_stats[loc] = location_stats.get(loc, 0) + 1

    # 输出统计结果
    print(f"\n总图片数：{total}")
    print(f"成功识别：{success}（识别率：{success/total:.2%}）")
    print(f"未识别/错误：{total - success}")
    
    print("\n车牌颜色分布：")
    for color, count in color_stats.items():
        print(f"  {color}: {count} 张 ({count/success:.2%})")
    
    print("\n车辆所属地分布（前10名）：")
    # 按数量排序，取前10
    sorted_locations = sorted(location_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    for loc, count in sorted_locations:
        print(f"  {loc}: {count} 张 ({count/success:.2%})")
