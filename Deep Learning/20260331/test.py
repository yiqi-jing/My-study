import torch
import torch.nn as nn

class FullyConnectedNN(nn.Module):
    def __init__(self):
        super(FullyConnectedNN, self).__init__()
        # 定义网络层
        self.fc1 = nn.Linear(4, 5)
        self.fc2 = nn.Linear(5, 6)
        self.fc3 = nn.Linear(6, 4)
        self.fc4 = nn.Linear(4, 3)
        # 定义激活函数
        self.relu = nn.ReLU()
    
    def forward(self, x):
        # 前向传播 + 激活函数
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.relu(self.fc3(x))
        # 输出层一般不加激活函数（分类任务用Softmax，回归任务直接输出）
        x = self.fc4(x)
        return x

# 测试网络
if __name__ == "__main__":
    model = FullyConnectedNN()
    print("网络结构:")
    print(model)
    
    # 随机输入 (1个样本，每个样本4个特征)
    input_tensor = torch.randn(1, 4)
    print("\n输入张量:")
    print(input_tensor)
    
    # 前向计算
    output = model(input_tensor)
    print("\n输出张量:")
    print(output)
    print("输出形状:", output.shape)