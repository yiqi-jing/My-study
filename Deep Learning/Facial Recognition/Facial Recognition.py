"""
纯 OpenCV 人脸识别系统（优化版）
优化点：
- 添加直方图均衡化增强对比度
- 实现多帧投票机制平滑识别结果
- 添加人脸对齐功能
- 优化LBPH参数提高识别稳定性
- 添加置信度平滑处理减少跳变
- 支持多张人脸同时注册提高准确性
"""
import cv2
import numpy as np
import os
import json
import time
from typing import List, Tuple, Optional, Dict
from collections import deque

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ====================== 配置常量 ======================
DATA_FILE = 'face_database.json'
CONFIDENCE_THRESHOLD = 85  # 放宽阈值，LBPH的confidence越小越匹配
SMOOTH_THRESHOLD = 70      # 平滑后的判定阈值
FACE_SIZE = (150, 150)     # 增大尺寸保留更多特征
FONT_SIZE = 24
ESCAPE_KEY = 27
ENTER_KEY = 13

# 多帧投票配置
VOTE_FRAMES = 5            # 投票窗口大小
VOTE_THRESHOLD = 3         # 最少需要3帧一致才确认

# LBPH 参数优化
LBPH_RADIUS = 2
LBPH_NEIGHBORS = 8
LBPH_GRID_X = 8
LBPH_GRID_Y = 8

# ====================== 初始化人脸检测器 ======================
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# 加载眼睛检测器（用于人脸对齐）
eye_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

# ====================== 数据管理 ======================
def load_face_database() -> Tuple[List[np.ndarray], List[str]]:
    """加载人脸数据库"""
    if not os.path.exists(DATA_FILE):
        return [], []
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        face_images = [np.array(img, dtype=np.uint8) for img in data.get('images', [])]
        names = data.get('names', [])
        return face_images, names
    except (json.JSONDecodeError, KeyError) as e:
        print(f"数据库加载失败: {e}，将创建新数据库")
        return [], []

def save_face_database(face_images: List[np.ndarray], names: List[str]) -> bool:
    """保存人脸数据库"""
    try:
        data = {
            'images': [img.tolist() for img in face_images],
            'names': names
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存失败: {e}")
        return False

def clear_face_database() -> None:
    """清除所有人脸注册信息"""
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        print("✓ 已清除所有注册信息")
    else:
        print("ℹ 当前没有注册信息可清除")

# ====================== 图像预处理 ======================
def enhance_face(face_img: np.ndarray) -> np.ndarray:
    """增强人脸图像质量"""
    # 直方图均衡化增强对比度
    enhanced = cv2.equalizeHist(face_img)
    # 轻微高斯模糊去噪
    enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
    return enhanced

def align_face(img: np.ndarray, face_rect: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
    """人脸对齐：基于眼睛位置旋转校正"""
    x, y, w, h = face_rect
    face_roi = img[y:y+h, x:x+w]
    
    # 检测眼睛
    gray_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
    eyes = eye_detector.detectMultiScale(gray_roi, scaleFactor=1.1, minNeighbors=3, minSize=(20, 20))
    
    if len(eyes) >= 2:
        # 获取两个最大的眼睛
        eyes = sorted(eyes, key=lambda e: e[2]*e[3], reverse=True)[:2]
        eyes = sorted(eyes, key=lambda e: e[0])  # 按x坐标排序
        
        # 计算眼睛中心
        left_eye = (eyes[0][0] + eyes[0][2]//2, eyes[0][1] + eyes[0][3]//2)
        right_eye = (eyes[1][0] + eyes[1][2]//2, eyes[1][1] + eyes[1][3]//2)
        
        # 计算旋转角度
        dy = right_eye[1] - left_eye[1]
        dx = right_eye[0] - left_eye[0]
        angle = np.degrees(np.arctan2(dy, dx))
        
        # 旋转图像 - 修复：确保center是Python int类型
        center = (int(w // 2), int(h // 2))
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        aligned = cv2.warpAffine(face_roi, M, (w, h), flags=cv2.INTER_CUBIC)
        
        face_gray = cv2.cvtColor(aligned, cv2.COLOR_BGR2GRAY)
    else:
        face_gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
    
    face_gray = cv2.resize(face_gray, FACE_SIZE)
    return enhance_face(face_gray)

def preprocess_face(img: np.ndarray, face_rect: Tuple[int, int, int, int]) -> np.ndarray:
    """预处理人脸图像（带对齐）"""
    aligned = align_face(img, face_rect)
    if aligned is not None:
        return aligned
    
    # 回退到基础处理
    x, y, w, h = face_rect
    h_img, w_img = img.shape[:2]
    x, y = max(0, x), max(0, y)
    w, h = min(w, w_img - x), min(h, h_img - y)
    
    face_img = img[y:y+h, x:x+w]
    face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    face_img = cv2.resize(face_img, FACE_SIZE)
    return enhance_face(face_img)

# ====================== 字体处理 ======================
_chinese_font: Optional[ImageFont.FreeTypeFont] = None

def get_chinese_font(font_size: int = FONT_SIZE) -> Optional[ImageFont.FreeTypeFont]:
    """获取中文字体（带缓存）"""
    global _chinese_font
    if not PIL_AVAILABLE:
        return None
    
    if _chinese_font is not None:
        return _chinese_font

    possible_fonts = [
        "simhei.ttf", "msyh.ttc", "msyh.ttf",
        "simsun.ttc", "simsun.ttf", "arialuni.ttf"
    ]
    font_dir = os.path.join("C:", "Windows", "Fonts")

    for font_name in possible_fonts:
        font_path = os.path.join(font_dir, font_name)
        if os.path.exists(font_path):
            try:
                _chinese_font = ImageFont.truetype(font_path, font_size)
                return _chinese_font
            except Exception:
                continue

    try:
        _chinese_font = ImageFont.load_default()
    except Exception:
        _chinese_font = None
    return _chinese_font

def put_text(img: np.ndarray, text: str, position: Tuple[int, int], 
             font_size: int = FONT_SIZE, color: Tuple[int, int, int] = (0, 255, 0), 
             thickness: int = 2) -> None:
    """在图像上绘制文字（支持中文）"""
    if PIL_AVAILABLE:
        font = get_chinese_font(font_size)
        if font is not None:
            image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            image_pil = Image.fromarray(image_rgb)
            draw = ImageDraw.Draw(image_pil)
            draw.text(position, text, font=font, fill=(color[2], color[1], color[0]))
            img[:] = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
            return

    scale = max(font_size / 30.0, 0.4)
    cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness)

# ====================== 多帧投票器 ======================
class FaceVoter:
    """多帧投票器，平滑识别结果"""
    def __init__(self, window_size: int = VOTE_FRAMES):
        self.window: deque = deque(maxlen=window_size)
        self.confidence_history: deque = deque(maxlen=window_size)
    
    def vote(self, name: str, confidence: float) -> Tuple[str, float]:
        """添加一票并返回投票结果"""
        self.window.append(name)
        self.confidence_history.append(confidence)
        
        # 统计出现次数
        from collections import Counter
        counts = Counter(self.window)
        
        # 找出最频繁的名称
        best_name, count = counts.most_common(1)[0]
        
        # 计算平均置信度
        avg_confidence = sum(self.confidence_history) / len(self.confidence_history)
        
        # 如果最频繁的名称出现次数不足，返回Unknown
        if count < VOTE_THRESHOLD and len(self.window) >= VOTE_THRESHOLD:
            return "Unknown", avg_confidence
        
        return best_name, avg_confidence
    
    def reset(self):
        """重置投票器"""
        self.window.clear()
        self.confidence_history.clear()

# ====================== 人脸捕获 ======================
def capture_face() -> Optional[np.ndarray]:
    """从摄像头捕获单张人脸"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("错误：无法打开摄像头")
        return None
    
    print("按 Enter 捕获 | 按 Esc 退出")
    captured_face = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        display_frame = frame.copy()
        for (x, y, w, h) in faces:
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow("Capture - Press Enter to capture", display_frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ENTER_KEY and len(faces) > 0:
            captured_face = preprocess_face(frame, faces[0])
            break
        if key == ESCAPE_KEY:
            break

    cap.release()
    cv2.destroyAllWindows()
    return captured_face

def capture_multiple_faces(count: int = 3) -> List[np.ndarray]:
    """连续捕获多张人脸用于注册（提高准确性）"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("错误：无法打开摄像头")
        return []
    
    print(f"将连续捕获 {count} 张人脸，请保持姿势...")
    print("每张按 Enter 确认，按 Esc 取消")
    
    faces = []
    captured = 0

    while captured < count:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_detected = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        display_frame = frame.copy()
        status_text = f"Captured: {captured}/{count}"
        put_text(display_frame, status_text, (10, 30), font_size=20, color=(255, 255, 0))
        
        for (x, y, w, h) in faces_detected:
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow("Multi-Capture", display_frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ENTER_KEY and len(faces_detected) > 0:
            face_img = preprocess_face(frame, faces_detected[0])
            faces.append(face_img)
            captured += 1
            print(f"  ✓ 第 {captured} 张捕获成功")
            time.sleep(0.5)  # 短暂延迟，让用户调整姿势
        if key == ESCAPE_KEY:
            break

    cap.release()
    cv2.destroyAllWindows()
    return faces

# ====================== 注册功能 ======================
def register_face() -> None:
    """注册新的人脸（支持多张采样）"""
    name = input("输入姓名：").strip()
    if not name:
        print("错误：姓名不能为空")
        return

    # 询问采样数量
    try:
        sample_count = int(input("采样数量（推荐3-5，默认3）：").strip() or "3")
    except ValueError:
        sample_count = 3
    
    face_imgs = capture_multiple_faces(sample_count)
    if len(face_imgs) == 0:
        print("错误：未捕获到人脸")
        return

    imgs, names_list = load_face_database()
    
    # 检查是否已存在同名用户
    if name in names_list:
        confirm = input(f"姓名 '{name}' 已存在，是否覆盖？(y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消注册")
            return
        # 覆盖：删除旧的
        indices = [i for i, n in enumerate(names_list) if n == name]
        for idx in reversed(indices):
            imgs.pop(idx)
            names_list.pop(idx)
    
    # 添加所有采样
    for face_img in face_imgs:
        imgs.append(face_img)
        names_list.append(name)
    
    if save_face_database(imgs, names_list):
        print(f"✓ '{name}' 注册成功！共采样 {len(face_imgs)} 张，数据库总计 {len(names_list)} 张")
    else:
        print("✗ 注册失败")

# ====================== 识别功能 ======================
def recognize_faces() -> None:
    """实时人脸识别（带多帧投票）"""
    imgs, names = load_face_database()
    if len(imgs) == 0:
        print("请先注册人脸")
        return

    # 创建并训练识别器（优化参数）
    face_recognizer = cv2.face.LBPHFaceRecognizer_create(
        radius=LBPH_RADIUS,
        neighbors=LBPH_NEIGHBORS,
        grid_x=LBPH_GRID_X,
        grid_y=LBPH_GRID_Y
    )
    labels = np.arange(len(imgs), dtype=np.int32)
    face_recognizer.train(imgs, labels)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("错误：无法打开摄像头")
        return
    
    print("按 Esc 退出")
    
    # 为每个人脸跟踪器创建投票器
    voters: Dict[int, FaceVoter] = {}
    last_faces: Dict[int, Tuple[int, int, int, int]] = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        current_ids = set()
        
        for i, (x, y, w, h) in enumerate(faces):
            face_id = i  # 简化：使用索引作为ID
            current_ids.add(face_id)
            
            # 初始化投票器
            if face_id not in voters:
                voters[face_id] = FaceVoter()
            
            # 预处理
            test_img = preprocess_face(frame, (x, y, w, h))
            
            # 识别
            try:
                label, confidence = face_recognizer.predict(test_img)
                raw_name = names[label]
                
                # 投票平滑
                voted_name, avg_confidence = voters[face_id].vote(raw_name, confidence)
                
                # 判定
                if avg_confidence < SMOOTH_THRESHOLD:
                    display_name = voted_name
                    color = (0, 255, 0)  # 绿色
                    status = "✓"
                else:
                    display_name = "Unknown"
                    color = (0, 0, 255)  # 红色
                    status = "?"
                
                text = f"{status} {display_name} ({avg_confidence:.0f})"
                
            except Exception as e:
                display_name = "Error"
                color = (0, 165, 255)  # 橙色
                text = display_name

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            put_text(frame, text, (x, y-10), font_size=FONT_SIZE, color=color, thickness=2)
        
        # 清理消失的投票器
        for face_id in list(voters.keys()):
            if face_id not in current_ids:
                voters[face_id].reset()

        cv2.imshow("Recognition", frame)
        
        if cv2.waitKey(1) & 0xFF == ESCAPE_KEY:
            break

    cap.release()
    cv2.destroyAllWindows()

# ====================== 主程序 ======================
def main() -> None:
    """主菜单"""
    print("=" * 40)
    print("      人脸识别系统（优化版）")
    print("=" * 40)
    
    try:
        _ = cv2.face.LBPHFaceRecognizer_create()
    except AttributeError:
        print("\n错误：需要安装 opencv-contrib-python")
        print("请运行: pip install opencv-contrib-python")
        return

    while True:
        print("\n" + "-" * 40)
        print("1. 注册人脸（多采样）")
        print("2. 识别人脸（多帧投票）")
        print("3. 清除注册信息")
        print("4. 退出")
        print("-" * 40)
        
        choice = input("请选择 (1-4): ").strip()

        if choice == "1":
            register_face()
        elif choice == "2":
            recognize_faces()
        elif choice == "3":
            clear_face_database()
        elif choice == "4":
            print("再见！")
            break
        else:
            print("无效输入，请重新选择")

if __name__ == "__main__":
    main()