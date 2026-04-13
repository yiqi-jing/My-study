import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# 数据预处理
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

# 加载数据集
train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)

# 定义卷积神经网络模型
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        # 第一层卷积
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        # 第二层卷积
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        # 最大池化
        self.pool = nn.MaxPool2d(2, 2)
        # 全连接层
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)
        # 激活函数
        self.relu = nn.ReLU()
        # Dropout层防止过拟合
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        # 输入形状: (batch_size, 1, 28, 28)
        x = self.pool(self.relu(self.conv1(x)))
        # 形状: (batch_size, 32, 14, 14)
        x = self.pool(self.relu(self.conv2(x)))
        # 形状: (batch_size, 64, 7, 7)
        x = x.view(-1, 64 * 7 * 7)  # 展平
        # 形状: (batch_size, 64*7*7)
        x = self.dropout(self.relu(self.fc1(x)))
        # 形状: (batch_size, 128)
        x = self.fc2(x)
        # 形状: (batch_size, 10)
        return x

# 初始化模型、损失函数和优化器
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = CNN().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 训练函数
def train(model, train_loader, criterion, optimizer, epoch):
    model.train()
    running_loss = 0.0
    
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        
        # 清零梯度
        optimizer.zero_grad()
        # 前向传播
        output = model(data)
        # 计算损失
        loss = criterion(output, target)
        # 反向传播
        loss.backward()
        # 更新参数
        optimizer.step()
        
        running_loss += loss.item()
        
        if batch_idx % 100 == 99:
            print(f'Epoch {epoch}, Batch {batch_idx+1}, Loss: {running_loss/100:.4f}')
            running_loss = 0.0

# 测试函数
def test(model, test_loader, criterion):
    model.eval()
    test_loss = 0
    correct = 0
    
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += criterion(output, target).item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
    
    test_loss /= len(test_loader.dataset)
    accuracy = 100. * correct / len(test_loader.dataset)
    print(f'Test set: Average loss: {test_loss:.4f}, Accuracy: {correct}/{len(test_loader.dataset)} ({accuracy:.2f}%)')

# 训练模型
if __name__ == '__main__':
    print(f'Using device: {device}')
    
    for epoch in range(1, 6):  # 训练5个epoch
        train(model, train_loader, criterion, optimizer, epoch)
        test(model, test_loader, criterion)
    
    # 保存模型
    torch.save(model.state_dict(), 'mnist_cnn.pth')
    print('Model saved to mnist_cnn.pth')
