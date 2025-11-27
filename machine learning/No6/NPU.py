import numpy as np
import matplotlib.pyplot as plt
import os
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import openvino.runtime as ov  # Intel NPU 推理框架
from openvino.preprocess import PrePostProcessor
from openvino.runtime import Layout, Type

# ===================== 1. 加载LFW人脸数据集（保持原逻辑不变） =====================
lfw_path = r"F:\My-study\machine learning\No6\lfw_home\lfw_home\lfw_funneled"

X = []
y = []
target_names = []
label_map = {}

for person_name in os.listdir(lfw_path):
    person_dir = os.path.join(lfw_path, person_name)
    if not os.path.isdir(person_dir):
        continue
    img_files = os.listdir(person_dir)
    if len(img_files) < 5:
        continue
    if person_name not in label_map:
        label_map[person_name] = len(target_names)
        target_names.append(person_name)
    for img_file in img_files:
        img_path = os.path.join(person_dir, img_file)
        img = Image.open(img_path).convert('L')
        img = img.resize((64, 64))
        img_vector = np.array(img).flatten()
        X.append(img_vector)
        y.append(label_map[person_name])

X = np.array(X)
y = np.array(y)
num_classes = len(target_names)
print(f"数据集规模：{X.shape}，类别数：{num_classes}")

# ===================== 2. 数据预处理 + 划分数据集（新增适配NPU的维度调整） =====================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.3, random_state=42, stratify=y
)

# 适配深度学习模型输入格式：(样本数, 通道数, 高, 宽)（NPU更擅长处理4D张量）
# 原数据是(样本数, 64*64)，转为(样本数, 1, 64, 64)（单通道灰度图）
X_train = X_train.reshape(-1, 1, 64, 64).astype(np.float32)  # NPU要求float32
X_test = X_test.reshape(-1, 1, 64, 64).astype(np.float32)

# ===================== 3. 定义轻量CNN模型（替换SVM，适配NPU推理） =====================
class FaceCNN(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        # 轻量卷积层（避免NPU算力不足，简化模型）
        self.conv_layers = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        # 全连接层（输出类别概率）
        self.fc_layers = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 8 * 8, 128),  # 64*8*8 = 卷积输出扁平化后的维度
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.conv_layers(x)
        x = self.fc_layers(x)
        return x

# 初始化模型并训练（CPU训练后转NPU推理，消费级NPU多不支持训练）
model = FaceCNN(num_classes)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)

# 定义数据集类（适配PyTorch DataLoader）
class FaceDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# 训练参数
train_dataset = FaceDataset(X_train, y_train)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
epochs = 10  # 轻量模型无需多轮训练

# CPU训练（消费级NPU通常只支持推理，训练仍用CPU/GPU）
print("开始CPU训练轻量CNN模型...")
model.train()
for epoch in range(epochs):
    total_loss = 0.0
    for inputs, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(train_loader):.4f}")

# 保存PyTorch模型（用于后续转换为NPU支持的格式）
torch.save(model.state_dict(), "face_cnn.pth")
print("CPU训练完成，模型已保存为 face_cnn.pth")

# ===================== 4. NPU加速推理核心代码块 =====================
"""
NPU调用逻辑说明：
1. 依赖：Intel Core Ultra NPU + Windows 11 24H2+ + OpenVINO Runtime
2. 步骤：PyTorch模型 → ONNX格式 → OpenVINO IR格式 → NPU加载推理
3. 关键：NPU只支持特定算子（轻量CNN完全兼容），输入必须是float32类型
"""
# 4.1 加载OpenVINO核心（初始化NPU设备）
core = ov.Core()
print("可用设备列表：", core.available_devices)  # 查看是否识别到NPU（通常显示为"NPU"）

# 4.2 PyTorch模型转ONNX（NPU的中间兼容格式）
onnx_model_path = "face_cnn.onnx"
# 构造虚拟输入（匹配模型输入维度：(1, 1, 64, 64)）
dummy_input = torch.randn(1, 1, 64, 64, dtype=torch.float32)
# 导出ONNX（指定动态批次维度，支持批量推理）
torch.onnx.export(
    model, dummy_input, onnx_model_path,
    input_names=["input"], output_names=["output"],
    dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
    opset_version=12  # 选择NPU兼容的ONNX版本
)
print(f"PyTorch模型已转为ONNX格式：{onnx_model_path}")

# 4.3 加载ONNX模型并编译到NPU（核心步骤：将模型部署到NPU）
# 读取ONNX模型
ov_model = core.read_model(model=onnx_model_path)
# 预处理配置（确保输入格式与NPU要求一致）
ppp = PrePostProcessor(ov_model)
# 指定输入布局：(N, C, H, W)（批次、通道、高、宽）
ppp.input().tensor().set_layout(Layout("NCHW")).set_element_type(Type.f32)
# 应用预处理配置
ov_model = ppp.build()
# 编译模型到NPU设备（device_name="NPU"指定调用NPU）
compiled_npu_model = core.compile_model(model=ov_model, device_name="NPU")
print("模型已编译到NPU，开始NPU加速推理...")

# 4.4 NPU推理（批量处理测试集）
# 创建推理请求
infer_request = compiled_npu_model.create_infer_request()
# 执行推理（输入测试集数据）
infer_request.infer(inputs={"input": X_test})
# 获取NPU推理结果（输出为类别得分）
npu_outputs = infer_request.get_output_tensor().data
# 转换为预测类别（取得分最高的类别）
y_pred = np.argmax(npu_outputs, axis=1)

# ===================== 5. 评估模型（保持原逻辑不变） =====================
accuracy = accuracy_score(y_test, y_pred)
print("\n===== LFW人脸数据集 NPU加速分类结果 =====")
print(f"模型：轻量CNN + NPU加速（Intel Core Ultra NPU）")
print(f"测试集准确率：{accuracy:.4f}")
print("分类报告：")
print(classification_report(y_test, y_pred, target_names=target_names))
print("混淆矩阵：")
cm = confusion_matrix(y_test, y_pred)
print(cm)

# ===================== 6. 可视化（保持原逻辑不变） =====================
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 混淆矩阵可视化
plt.figure(figsize=(8, 7))
im = plt.imshow(cm, cmap='Blues')
plt.title("LFW人脸数据集 混淆矩阵（NPU加速）")
plt.xticks(range(len(target_names)), target_names, rotation=45)
plt.yticks(range(len(target_names)), target_names)
for x in range(len(target_names)):
    for y_idx in range(len(target_names)):
        plt.text(y_idx, x, cm[x, y_idx], ha='center', va='center', color='black')
plt.colorbar(im)
plt.tight_layout()
plt.show()

# 2. 样本图像可视化
plt.figure(figsize=(12, 3))
sample_indices = np.random.choice(len(X_test), 10, replace=False)
for i, idx in enumerate(sample_indices):
    # 还原为原始图像（反标准化）
    img_vector = X_test[idx].reshape(-1)  # (1,64,64)→(4096,)
    img_vector = scaler.inverse_transform([img_vector])[0].reshape(64, 64)
    plt.subplot(1, 10, i+1)
    plt.imshow(img_vector, cmap='gray')
    plt.title(f"真实：{target_names[y_test[idx]]}\n预测：{target_names[y_pred[idx]]}", fontsize=8)
    plt.axis('off')
plt.tight_layout()
plt.show()