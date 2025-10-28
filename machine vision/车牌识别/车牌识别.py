# os/glob 负责文件管理，cv2/numpy 负责图像处理，re 负责字符串清洗，hyperlpr 负责核心的车牌识别，共同实现了车牌识别的功能
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

def postprocess_plate(plate_str):
    """修正字符错误，统一格式"""
    plate_str = re.sub(r'[\s·-]', '', plate_str).upper()  # 去除分隔符
    char_correction = {
    }
    for wrong, right in char_correction.items():
        plate_str = plate_str.replace(wrong, right)
    return plate_str

def enhance_image_for_plate(image):
    """对车牌区域进行颜色和对比度增强（修复维度错误）"""
    # 转换为HSV空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # 增强蓝色通道（蓝牌）- 使用NumPy直接运算避免维度问题
    lower_blue = np.array([90, 40, 40])
    upper_blue = np.array([130, 255, 255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    # 直接对符合条件的像素进行数值增加，并用clip限制范围
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
        return None, "文件不存在"
    if not image_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        return None, "非图片格式"

    image = cv2.imread(image_path)
    if image is None:
        return None, "无法读取图片"

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
            return None, "未识别到车牌"

        # 选择置信度最高的结果
        merged_str = max(all_results, key=lambda x: x[1])[0]
        processed_plate = postprocess_plate(merged_str)
        return processed_plate, "识别成功"
    except Exception as e:
        return None, f"识别错误：{str(e)}"

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
        plate, status = recognize_plate(img_path)
        
        overall_results.append({
            "图片名称": img_name,
            "识别结果": plate if plate else "未识别",
            "状态": status
        })

    # 输出结果表格
    print("=" * 60)
    print(f"{'图片名称':<30} | {'识别结果':<20} | 状态")
    print("-" * 60)
    for res in overall_results:
        print(f"{res['图片名称']:<30} | {res['识别结果']:<20} | {res['状态']}")
    print("=" * 60)

    # 简单统计
    total = len(all_images)
    success = sum(1 for res in overall_results if res['状态'] == "识别成功")
    print(f"\n总图片数：{total}")
    print(f"成功识别：{success}（识别率：{success/total:.2%}）")
    print(f"未识别/错误：{total - success}")