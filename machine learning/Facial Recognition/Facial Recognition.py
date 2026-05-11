"""
纯 OpenCV 人脸识别系统（无 face_recognition，零报错版）
"""
import cv2
import numpy as np
import os
import json

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

# ====================== 核心功能 ======================
def preprocess_face(img, face_rect):
    x, y, w, h = face_rect
    face_img = img[y:y+h, x:x+w]
    face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    face_img = cv2.resize(face_img, (100, 100))
    return face_img

def capture_face():
    cap = cv2.VideoCapture(0)
    print("按 c 捕获 | 按 q 退出")

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

        if key == ord('c') and len(faces) > 0:
            face_img = preprocess_face(frame, faces[0])
            cap.release()
            cv2.destroyAllWindows()
            return face_img
        if key == ord('q'):
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
    print("按 q 退出")

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
                name = "Unknown"

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# ====================== 主程序 ======================
def main():
    print("=== OpenCV 纯人脸识别系统 ===")
    while True:
        print("\n1. 注册人脸")
        print("2. 识别人脸")
        print("3. 退出")
        choice = input("请选择：")

        if choice == "1":
            register_face()
        elif choice == "2":
            recognize_faces()
        elif choice == "3":
            print("退出")
            break
        else:
            print("输入错误")

if __name__ == "__main__":
    main()