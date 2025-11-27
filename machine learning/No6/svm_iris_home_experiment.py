import numpy as np
import matplotlib.pyplot as plt
import os
from PIL import Image
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler

# ===================== 1. 加载LFW人脸数据集 =====================
# 替换为你的lfw_home文件夹路径（解压后的路径）
lfw_path = r"F:\My-study\machine learning\No6\lfw_home\lfw_home\lfw_funneled"

# 读取文件夹下的所有人脸（仅选择样本数≥5的类别，避免类别不平衡）
X = []
y = []
target_names = []
label_map = {}  # 姓名→标签的映射

for person_name in os.listdir(lfw_path):
    person_dir = os.path.join(lfw_path, person_name)
    if not os.path.isdir(person_dir):
        continue
    # 只选择样本数≥5的人物（参考word中的分类报告）
    img_files = os.listdir(person_dir)
    if len(img_files) < 5:
        continue
    # 分配标签
    if person_name not in label_map:
        label_map[person_name] = len(target_names)
        target_names.append(person_name)
    # 读取图像并转为特征向量
    for img_file in img_files:
        img_path = os.path.join(person_dir, img_file)
        img = Image.open(img_path).convert('L')  # 转为灰度图
        img = img.resize((64, 64))  # 统一尺寸（可根据需求调整）
        img_vector = np.array(img).flatten()  # 2D图像→1D向量
        X.append(img_vector)
        y.append(label_map[person_name])

# 转为numpy数组
X = np.array(X)
y = np.array(y)
print(f"数据集规模：{X.shape}，类别数：{len(target_names)}")


# ===================== 2. 数据预处理 + 划分数据集 =====================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.3, random_state=42, stratify=y  # stratify保持类别分布
)


# ===================== 3. 训练SVM模型（参考word中的参数） =====================
# word中参数：C=5, gamma=0.001
model = SVC(kernel='rbf', C=5, gamma=0.001, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)


# ===================== 4. 评估模型（匹配word中的输出） =====================
accuracy = accuracy_score(y_test, y_pred)
print("===== LFW人脸数据集 SVM分类结果 =====")
print(f"最优参数：C=5, gamma=0.001")
print(f"测试集准确率：{accuracy:.4f}")
print("分类报告：")
print(classification_report(y_test, y_pred, target_names=target_names))
print("混淆矩阵：")
cm = confusion_matrix(y_test, y_pred)
print(cm)


# ===================== 5. 可视化（混淆矩阵 + 样本图像） =====================
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 混淆矩阵可视化
plt.figure(figsize=(8, 7))
im = plt.imshow(cm, cmap='Blues')
plt.title("LFW人脸数据集 混淆矩阵")
plt.xticks(range(len(target_names)), target_names, rotation=45)
plt.yticks(range(len(target_names)), target_names)
# 标注数值
for x in range(len(target_names)):
    for y_idx in range(len(target_names)):
        plt.text(y_idx, x, cm[x, y_idx], ha='center', va='center', color='black')
plt.colorbar(im)
plt.tight_layout()
plt.show()

# 2. 样本图像可视化（展示部分测试集样本）
plt.figure(figsize=(12, 3))
sample_indices = np.random.choice(len(X_test), 10, replace=False)  # 随机选10个样本
for i, idx in enumerate(sample_indices):
    img_vector = X_test[idx]
    img = img_vector.reshape(64, 64)  # 1D向量→2D图像
    plt.subplot(1, 10, i+1)
    plt.imshow(img, cmap='gray')
    plt.title(f"真实：{target_names[y_test[idx]]}\n预测：{target_names[y_pred[idx]]}", fontsize=8)
    plt.axis('off')
plt.tight_layout()
plt.show()