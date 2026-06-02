import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import matplotlib.pyplot as plt

# ---------------------- 1. 超参数设置 ----------------------
batch_size = 64
lr = 0.001
num_epochs = 5
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---------------------- 2. 数据预处理与加载 ----------------------
# ResNet18 要求输入为 3 通道 224x224 图像，MNIST 是单通道 28x28，需做适配
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=3),  # 转为3通道
    transforms.Resize((224, 224)),                # 调整尺寸
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],  # ImageNet 预训练模型的归一化参数
                         std=[0.229, 0.224, 0.225])
])

# 加载 MNIST 数据集
train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

# ---------------------- 3. 构建迁移学习模型 ----------------------
# 加载预训练的 ResNet18
model = models.resnet18(pretrained=True)

# 冻结骨干网络参数
for param in model.parameters():
    param.requires_grad = False

# 替换分类头（适配 MNIST 的 10 分类）
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 10)  # 仅这一层会被训练

model = model.to(device)

# ---------------------- 4. 定义损失函数与优化器 ----------------------
criterion = nn.CrossEntropyLoss()
# 只优化分类头的参数
optimizer = optim.Adam(model.fc.parameters(), lr=lr)

# ---------------------- 5. 迭代训练 ----------------------
train_loss_history = []
train_acc_history = []

for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        # 前向传播
        outputs = model(images)
        loss = criterion(outputs, labels)

        # 反向传播 + 优化
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # 统计指标
        running_loss += loss.item() * images.size(0)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    epoch_loss = running_loss / len(train_dataset)
    epoch_acc = 100 * correct / total
    train_loss_history.append(epoch_loss)
    train_acc_history.append(epoch_acc)

    print(f"Epoch [{epoch+1}/{num_epochs}] "
          f"Train Loss: {epoch_loss:.4f} "
          f"Train Acc: {epoch_acc:.2f}%")

# ---------------------- 6. 模型评估 ----------------------
model.eval()
correct = 0
total = 0
with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

print(f"Test Accuracy of the model on the 10000 test images: {100 * correct / total:.2f}%")

# ---------------------- 7. 训练过程可视化 ----------------------
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(train_loss_history, label='Train Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training Loss')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(train_acc_history, label='Train Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy (%)')
plt.title('Training Accuracy')
plt.legend()
plt.show()