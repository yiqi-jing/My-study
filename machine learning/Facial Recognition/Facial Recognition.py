"""
纯 OpenCV 人脸识别系统（无 face_recognition，零报错版）
"""
import cv2
import numpy as np
import os
import json

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

DATA_FILE = 'face_database.json'

# 人脸检测器
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# ====================== 修复：数据存储用列表，不存对象 ======================
def load_face_database():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        face_images = [np.array(img, dtype=np.uint8) for img in data.get('images', [])]
        names = data.get('names', [])
        return face_images, names
    return [], []

def save_face_database(face_images, names):
    data = {
        'images': [img.tolist() for img in face_images],
        'names': names
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


def clear_face_database():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        print("已清除所有注册信息")
    else:
        print("当前没有注册信息可清除")

def preprocess_face(img, face_rect):
    x, y, w, h = face_rect
    face_img = img[y:y+h, x:x+w]
    face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    face_img = cv2.resize(face_img, (100, 100))
    return face_img


_chinese_font = None

def get_chinese_font(font_size=24):
    global _chinese_font
    if not PIL_AVAILABLE:
        return None
    if _chinese_font is not None:
        return _chinese_font

    possible_fonts = [
        "simhei.ttf",
        "msyh.ttc",
        "msyh.ttf",
        "simsun.ttc",
        "simsun.ttf",
        "arialuni.ttf"
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


def put_text(img, text, position, font_size=24, color=(0, 255, 0), thickness=2):
    if PIL_AVAILABLE:
        font = get_chinese_font(font_size)
        if font is not None:
            image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(image)
            draw.text(position, text, font=font, fill=(color[2], color[1], color[0]))
            img[:] = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            return

    scale = max(font_size / 30.0, 0.4)
    cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness)


def capture_face():
    cap = cv2.VideoCapture(0)
    print("按 Enter 捕获 | 按 Esc 退出")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow("Capture", frame)
        key = cv2.waitKey(1) & 0xFF

        if key in (13, 10) and len(faces) > 0:
            face_img = preprocess_face(frame, faces[0])
            cap.release()
            cv2.destroyAllWindows()
            return face_img
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    return None

def register_face():
    name = input("输入姓名：").strip()
    if not name:
        print("姓名不能为空")
        return

    face_img = capture_face()
    if face_img is None:
        print("未捕获人脸")
        return

    imgs, names = load_face_database()
    imgs.append(face_img)
    names.append(name)
    save_face_database(imgs, names)
    print(f"{name} 注册成功！")

def recognize_faces():
    imgs, names = load_face_database()
    if len(imgs) == 0:
        print("请先注册人脸")
        return

    # 训练
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    labels = np.arange(len(imgs), dtype=np.int32)
    face_recognizer.train(imgs, labels)

    cap = cv2.VideoCapture(0)
    print("按 Esc 退出")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            test_img = gray[y:y+h, x:x+w]
            test_img = cv2.resize(test_img, (100, 100))

            try:
                label, confidence = face_recognizer.predict(test_img)
                name = names[label] if confidence < 75 else "Unknown"
            except:
                name = "未知信息"

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            put_text(frame, name, (x, y-10), font_size=24, color=(0, 255, 0), thickness=2)

        cv2.imshow("Recognition", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    print("=== 人脸识别系统 ===")
    while True:
        print("\n1. 注册人脸")
        print("2. 识别人脸")
        print("3. 清除注册信息")
        print("4. 退出")
        choice = input("请选择：")

        if choice == "1":
            register_face()
        elif choice == "2":
            recognize_faces()
        elif choice == "3":
            clear_face_database()
        elif choice == "4":
            print("退出")
            break
        else:
            print("输入错误")

if __name__ == "__main__":
    main()