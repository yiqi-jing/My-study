import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class Perceptron:
    def __init__(self, input_size, learning_rate=0.01, initializer='random'):
        """
        初始化感知机
        input_size: 输入特征维度
        learning_rate: 学习率
        initializer: 权重初始化方式，'random' 或 'zero'
        """
        self.input_size = input_size
        self.learning_rate = learning_rate
        
        # 初始化权重和偏置
        if initializer == 'random':
            self.weights = np.random.randn(input_size)
            self.bias = np.random.randn()
        else:  # zero
            self.weights = np.zeros(input_size)
            self.bias = 0
        
        self.loss_history = []
    
    def sigmoid(self, z):
        """sigmoid 激活函数"""
        return 1 / (1 + np.exp(-z))
    
    def predict(self, X):
        """预测函数"""
        z = np.dot(X, self.weights) + self.bias
        return self.sigmoid(z)
    
    def compute_loss(self, X, y):
        """计算交叉熵损失"""
        y_pred = self.predict(X)
        # 防止log(0)的情况
        y_pred = np.clip(y_pred, 1e-10, 1 - 1e-10)
        loss = -np.mean(y * np.log(y_pred) + (1 - y) * np.log(1 - y_pred))
        return loss
    
    def train(self, X, y, epochs=1000):
        """训练函数"""
        for epoch in range(epochs):
            # 前向传播
            y_pred = self.predict(X)
            
            # 计算梯度
            error = y_pred - y
            dw = np.dot(X.T, error) / len(y)
            db = np.mean(error)
            
            # 更新参数
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db
            
            # 计算并记录损失
            loss = self.compute_loss(X, y)
            self.loss_history.append(loss)
            
            # 每100个epoch打印一次损失
            if epoch % 100 == 0:
                print(f'Epoch {epoch}, Loss: {loss:.4f}')

# 准备数据
def prepare_data():
    """准备鸢尾花数据集，提取两个类别进行二分类"""
    iris = load_iris()
    
    # 只取前两个类别（0和1），并且只取前两个特征（便于可视化）
    X = iris.data[:100, :2]
    y = iris.target[:100]
    
    # 数据集分割
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 数据标准化
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    return X_train, X_test, y_train, y_test, scaler

# 绘制综合实验结果
def plot_combined_results(models, histories, experiment_params, X_train, y_train, accuracies):
    """将所有实验结果整合到一个图片中"""
    fig = plt.figure(figsize=(20, 20))
    
    # 1. 损失曲线对比 (顶部)
    ax1 = fig.add_subplot(4, 2, 1)
    for i, (lr, init) in enumerate(experiment_params):
        ax1.plot(histories[i], label=f'学习率: {lr}')
    ax1.set_title('不同学习率的损失曲线对比')
    ax1.set_xlabel('迭代次数')
    ax1.set_ylabel('损失值')
    ax1.legend()
    ax1.grid(True)
    
    # 2. 实验结果表格 (顶部右侧)
    ax2 = fig.add_subplot(4, 2, 2)
    ax2.axis('tight')
    ax2.axis('off')
    
    # 准备表格数据
    table_data = [['实验', '学习率', '训练准确率', '测试准确率']]
    for i, ((lr, init), (train_acc, test_acc)) in enumerate(zip(experiment_params, accuracies)):
        table_data.append([f'{i+1}', f'{lr}', f'{train_acc:.4f}', f'{test_acc:.4f}'])
    
    # 创建表格
    table = ax2.table(cellText=table_data, colLabels=None, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    ax2.set_title('实验结果表格')
    
    # 3. 决策边界 (底部)
    num_models = len(models)
    
    # 计算坐标范围
    x_min, x_max = X_train[:, 0].min() - 1, X_train[:, 0].max() + 1
    y_min, y_max = X_train[:, 1].min() - 1, X_train[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.01),
                         np.arange(y_min, y_max, 0.01))
    
    for i, (model, (lr, init)) in enumerate(zip(models, experiment_params)):
        ax = fig.add_subplot(4, 2, i+3)  # 从第3个子图开始 (0-based索引+3)
        # 绘制数据点
        ax.scatter(X_train[y_train == 0][:, 0], X_train[y_train == 0][:, 1], label='类别 0', c='blue')
        ax.scatter(X_train[y_train == 1][:, 0], X_train[y_train == 1][:, 1], label='类别 1', c='red')
        # 绘制决策边界
        Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)
        ax.contourf(xx, yy, Z, alpha=0.3, cmap='coolwarm')
        ax.set_title(f'学习率: {lr}')
        ax.set_xlabel('特征 1')
        ax.set_ylabel('特征 2')
        ax.legend()
    
    # 添加总标题
    fig.suptitle('单层神经网络与鸢尾花分类实验结果', fontsize=16, y=0.99)
    
    # 调整子图之间的间距
    plt.subplots_adjust(
        top=0.95,
        bottom=0.05,
        left=0.05,
        right=0.95,
        hspace=0.3,  # 增加垂直间距
        wspace=0.2  # 增加水平间距
    )
    plt.show()

# 计算准确率
def calculate_accuracy(model, X, y):
    """计算模型准确率"""
    y_pred = model.predict(X)
    y_pred = np.round(y_pred)
    accuracy = np.mean(y_pred == y)
    return accuracy

# 主函数
def main():
    print("=== 实验二：单层神经网络与鸢尾花分类 ===")
    
    # 1. 准备数据
    print("\n1. 准备鸢尾花数据集")
    X_train, X_test, y_train, y_test, scaler = prepare_data()
    print(f"训练集大小: {len(X_train)}, 测试集大小: {len(X_test)}")
    
    # 2. 不同学习率的实验
    print("\n2. 不同学习率的实验")
    
    # 存储模型和历史记录
    models = []
    histories = []
    experiment_params = []
    accuracies = []
    
    # 定义不同的学习率
    learning_rates = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
    
    for i, lr in enumerate(learning_rates):
        print(f"\n实验{i+1}: 随机初始化，学习率{lr}")
        model = Perceptron(input_size=2, learning_rate=lr, initializer='random')
        model.train(X_train, y_train, epochs=1000)
        train_acc = calculate_accuracy(model, X_train, y_train)
        test_acc = calculate_accuracy(model, X_test, y_test)
        print(f"训练准确率: {train_acc:.4f}, 测试准确率: {test_acc:.4f}")
        models.append(model)
        histories.append(model.loss_history)
        experiment_params.append((lr, 'random'))
        accuracies.append((train_acc, test_acc))
    
    # 3. 绘制所有结果
    print("\n3. 绘制实验结果")
    plot_combined_results(models, histories, experiment_params, X_train, y_train, accuracies)
    
    # 4. 结果比较
    print("\n4. 实验结果比较")
    print("| 实验 | 初始化方式 | 学习率 | 训练准确率 | 测试准确率 |")
    print("|------|------------|--------|------------|------------|")
    for i, (lr, init) in enumerate(experiment_params):
        print(f"| {i+1}    | {init}       | {lr}   | {accuracies[i][0]:.4f}   | {accuracies[i][1]:.4f}   |")
    
    print("\n5. 实验总结")
    print("- 学习率对模型收敛速度有显著影响")
    print("- 较小的学习率（如0.001）收敛较慢")
    print("- 较大的学习率（如0.1-0.5）收敛速度快，但需注意过拟合")
    print("- 单层神经网络（感知机）能够很好地处理线性可分的二分类问题")
    print("- 对于鸢尾花数据集的前两个类别，线性模型已经能够达到很高的准确率")

if __name__ == "__main__":
    main()
