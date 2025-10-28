from aip import AipOcr
import os
import time
import random  # 用于随机延迟，避免固定间隔仍触发限制

# 1. 配置应用信息（替换为你的API Key和Secret Key）
APP_ID = '7164286'
API_KEY = '1ADn5vmAMWwFylDvXszYDeUs'
SECRET_KEY = 'f1YCztR01Qgp51sNpFp0VwICWt4noo6n'
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

def get_file_content(file_path):
    with open(file_path, 'rb') as fp:
        return fp.read()

def recognize_special_plate(image_path, max_retries=3):
    """识别车牌，支持失败重试（最多3次）"""
    image = get_file_content(image_path)
    retries = 0
    while retries < max_retries:
        try:
            result = client.licensePlate(image)
            if 'words_result' in result:
                plate_info = result['words_result']
                return {
                    "车牌号码": plate_info['number'],
                    "车牌类型": plate_info['color'],
                    "置信度": plate_info['probability'],
                    "状态": "识别成功"
                }
            else:
                error_msg = result.get('error_msg', '未知错误')
                # 若为QPS限制，等待后重试
                if "qps request limit" in error_msg:
                    retries += 1
                    wait_time = random.uniform(1.5, 3.0)  # 随机延迟1.5-3秒，避免固定间隔
                    print(f"  触发QPS限制，第{retries}次重试（等待{wait_time:.1f}秒）...")
                    time.sleep(wait_time)
                    continue
                return {"车牌号码": None, "车牌类型": None, "状态": f"识别失败：{error_msg}"}
        except Exception as e:
            return {"车牌号码": None, "车牌类型": None, "状态": f"异常错误：{str(e)}"}
    return {"车牌号码": None, "车牌类型": None, "状态": "超过最大重试次数，识别失败"}

def batch_recognize(folder_path):
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
    image_files = [
        os.path.join(folder_path, f) 
        for f in os.listdir(folder_path) 
        if f.lower().endswith(image_extensions)
    ]
    
    if not image_files:
        print("未找到图片文件")
        return
    
    print("=" * 80)
    print(f"{'文件名':<40} | {'车牌号码':<20} | {'车牌类型':<15} | 状态")
    print("-" * 80)
    
    for img_path in image_files:
        file_name = os.path.basename(img_path)
        res = recognize_special_plate(img_path)
        print(f"{file_name:<40} | {res['车牌号码'] or '未识别':<20} | {res['车牌类型'] or '未知':<15} | {res['状态']}")
        # 基础延迟，降低初始QPS压力
        time.sleep(random.uniform(1.0, 2.0))  # 随机1-2秒间隔
    
    print("=" * 80)

if __name__ == "__main__":
    test_folder = r"E:\HuaweiMoveData\Users\yelan\Pictures\data_jpg"
    batch_recognize(test_folder)