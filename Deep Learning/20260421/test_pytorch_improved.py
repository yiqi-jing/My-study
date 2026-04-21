import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from torchvision import datasets, transforms
import matplotlib.pyplot as plt

# 设置设备
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"使用设备: {device}")

# 1. 加载和预处理数据
def load_and_preprocess_data():
    """加载MNIST数据集并进行预处理"""
    # 数据转换
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))  # MNIST均值和标准差
    ])
    
    # 加载数据集
    train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)
    
    # 创建数据加载器
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)
    
    return train_loader, test_loader

# 2. 构建改进的卷积神经网络模型
class ImprovedCNN(nn.Module):
    """改进的卷积神经网络模型"""
    def __init__(self):
        super(ImprovedCNN, self).__init__()
        
        # 第一层卷积块
        self.conv_block1 = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout(0.25)
        )
        
        # 第二层卷积块
        self.conv_block2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout(0.25)
        )
        
        # 第三层卷积块
        self.conv_block3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Dropout(0.25)
        )
        
        # 全连接层
        self.fc_block = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 7 * 7, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, 10)
        )
    
    def forward(self, x):
        x = self.conv_block1(x)
        x = self.conv_block2(x)
        x = self.conv_block3(x)
        x = self.fc_block(x)
        return x

# 3. 训练模型
def train_model(model, train_loader, test_loader, epochs=15, lr=0.001):
    """训练模型并评估性能"""
    # 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=3, factor=0.5)
    
    # 训练历史
    train_losses = []
    train_accs = []
    test_losses = []
    test_accs = []
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()
            
            if batch_idx % 100 == 99:
                print(f'[{epoch+1}, {batch_idx+1}] loss: {running_loss/100:.3f}, acc: {100.*correct/total:.3f}%')
                running_loss = 0.0
        
        train_loss = running_loss / len(train_loader)
        train_acc = 100. * correct / total
        train_losses.append(train_loss)
        train_accs.append(train_acc)
        
        # 测试
        test_loss, test_acc = evaluate_model(model, test_loader, criterion)
        test_losses.append(test_loss)
        test_accs.append(test_acc)
        
        # 学习率调度
        scheduler.step(test_loss)
        
        print(f'Epoch {epoch+1}: Train Loss: {train_loss:.3f}, Train Acc: {train_acc:.2f}%, Test Loss: {test_loss:.3f}, Test Acc: {test_acc:.2f}%')
    
    return train_losses, train_accs, test_losses, test_accs

# 4. 评估模型
def evaluate_model(model, test_loader, criterion=None):
    """评估模型性能"""
    model.eval()
    test_loss = 0
    correct = 0
    
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            
            if criterion:
                test_loss += criterion(output, target).item()
            
            _, predicted = output.max(1)
            correct += predicted.eq(target).sum().item()
    
    test_loss /= len(test_loader)
    test_acc = 100. * correct / len(test_loader.dataset)
    
    return test_loss, test_acc

# 5. 预测和可视化
def predict_and_visualize(model, test_loader, num_samples=10):
    """预测并可视化结果"""
    model.eval()
    
    # 获取测试数据
    data_iter = iter(test_loader)
    images, labels = next(data_iter)
    
    # 选择样本
    indices = np.random.randint(0, images.shape[0], num_samples)
    sample_images = images[indices]
    sample_labels = labels[indices]
    
    # 预测
    with torch.no_grad():
        sample_images = sample_images.to(device)
        outputs = model(sample_images)
        _, predicted = outputs.max(1)
        probabilities = torch.softmax(outputs, dim=1)
    
    # 可视化
    plt.figure(figsize=(15, 6))
    for i in range(num_samples):
        plt.subplot(2, 5, i + 1)
        plt.imshow(sample_images[i].cpu().squeeze().numpy(), cmap='gray')
        plt.axis('off')
        true_label = sample_labels[i].item()
        pred_label = predicted[i].item()
        confidence = probabilities[i][pred_label].item()
        plt.title(f'True: {true_label}\nPred: {pred_label}\nConf: {confidence:.2f}')
    plt.tight_layout()
    plt.show()

# 6. 绘制训练历史
def plot_training_history(train_losses, train_accs, test_losses, test_accs):
    """绘制训练历史"""
    plt.figure(figsize=(12, 4))
    
    # 准确率曲线
    plt.subplot(1, 2, 1)
    plt.plot(train_accs, label='训练准确率')
    plt.plot(test_accs, label='测试准确率')
    plt.title('准确率曲线')
    plt.xlabel('epoch')
    plt.ylabel('准确率 (%)')
    plt.legend()
    
    # 损失曲线
    plt.subplot(1, 2, 2)
    plt.plot(train_losses, label='训练损失')
    plt.plot(test_losses, label='测试损失')
    plt.title('损失曲线')
    plt.xlabel('epoch')
    plt.ylabel('损失')
    plt.legend()
    
    plt.tight_layout()
    plt.show()

# 7. 主函数
def main():
    print("=== PyTorch 改进版卷积神经网络与手写数字识别实验 ===")
    
    # 加载数据
    print("1. 加载MNIST数据集...")
    train_loader, test_loader = load_and_preprocess_data()
    print(f"训练集大小: {len(train_loader.dataset)}")
    print(f"测试集大小: {len(test_loader.dataset)}")
    
    # 构建模型
    print("\n2. 构建改进的卷积神经网络模型...")
    model = ImprovedCNN().to(device)
    print(model)
    
    # 训练模型
    print("\n3. 训练模型...")
    train_losses, train_accs, test_losses, test_accs = train_model(model, train_loader, test_loader, epochs=15)
    
    # 绘制训练历史
    print("\n4. 绘制训练历史...")
    plot_training_history(train_losses, train_accs, test_losses, test_accs)
    
    # 评估模型
    print("\n5. 最终评估模型...")
    test_loss, test_acc = evaluate_model(model, test_loader)
    print(f'测试准确率: {test_acc:.4f}%')
    print(f'测试损失: {test_loss:.4f}')
    
    # 预测和可视化
    print("\n6. 预测和可视化结果...")
    predict_and_visualize(model, test_loader)
    
    # 保存模型
    print("\n7. 保存模型...")
    torch.save(model.state_dict(), 'mnist_cnn_pytorch_improved_model.pth')
    print("模型已保存为 mnist_cnn_pytorch_improved_model.pth")
    
    print(f"\n=== 实验完成 ===")
    print(f"最终测试准确率: {test_acc:.4f}%")

if __name__ == '__main__':
    main()
