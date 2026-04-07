import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.neural_network import MLPClassifier


# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


# 加载葡萄酒数据集
def load_data():
    wine = load_wine()
    X = wine.data
    y = wine.target
    print(f"数据集形状: X={X.shape}, y={y.shape}")
    print(f"类别数: {len(np.unique(y))}")
    print(f"类别标签: {np.unique(y)}")
    return X, y, wine.target_names

# 数据预处理
def preprocess_data(X, y):
    # 数据集拆分
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"训练集: X_train={X_train.shape}, y_train={y_train.shape}")
    print(f"测试集: X_test={X_test.shape}, y_test={y_test.shape}")
    
    # 特征缩放
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    return X_train_scaled, X_test_scaled, y_train, y_test

# 搭建全连接神经网络模型
def build_model():
    # 使用MLPClassifier，隐藏层为(64, 32)，激活函数为relu，输出层为softmax
    model = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation='relu',
        solver='adam',
        max_iter=1000,
        random_state=42,
        verbose=True
    )
    print("模型结构:")
    print(f"隐藏层: (64, 32)")
    print(f"激活函数: relu")
    print(f"求解器: adam")
    print(f"最大迭代次数: 1000")
    return model

# 训练模型
def train_model(model, X_train, y_train):
    print("\n开始训练模型...")
    model.fit(X_train, y_train)
    return model

# 评估模型
def evaluate_model(model, X_test, y_test, class_names):
    accuracy = model.score(X_test, y_test)
    print(f"\n模型评估结果:")
    print(f"测试集准确率: {accuracy:.4f}")
    
    # 预测
    y_pred_classes = model.predict(X_test)
    
    # 混淆矩阵
    cm = confusion_matrix(y_test, y_pred_classes)
    print(f"\n混淆矩阵:")
    print(cm)
    
    # 分类报告
    print(f"\n分类报告:")
    print(classification_report(y_test, y_pred_classes, target_names=class_names))
    
    return y_pred_classes, cm

# 可视化训练过程
def plot_training_history(model):
    plt.figure(figsize=(10, 6))
    plt.plot(model.loss_curve_)
    plt.title('模型训练损失曲线')
    plt.xlabel('迭代次数')
    plt.ylabel('损失')
    plt.grid(True)
    plt.savefig('training_loss.png')
    plt.show()

# 可视化混淆矩阵
def plot_confusion_matrix(cm, class_names):
    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('混淆矩阵')
    plt.colorbar()
    tick_marks = np.arange(len(class_names))
    plt.xticks(tick_marks, class_names, rotation=45)
    plt.yticks(tick_marks, class_names)
    
    # 在矩阵中显示数值
    fmt = 'd'
    thresh = cm.max() / 2.
    for i, j in np.ndindex(cm.shape):
        plt.text(j, i, format(cm[i, j], fmt),
                 ha="center", va="center",
                 color="white" if cm[i, j] > thresh else "black")
    
    plt.ylabel('真实标签')
    plt.xlabel('预测标签')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png')
    plt.show()

# 主函数
def main():
    print("=== 葡萄酒分类实验 ===")
    
    # 加载数据
    X, y, class_names = load_data()
    
    # 数据预处理
    X_train, X_test, y_train, y_test = preprocess_data(X, y)
    
    # 搭建模型
    model = build_model()
    
    # 训练模型
    model = train_model(model, X_train, y_train)
    
    # 评估模型
    y_pred_classes, cm = evaluate_model(model, X_test, y_test, class_names)
    
    # 可视化结果
    plot_training_history(model)
    plot_confusion_matrix(cm, class_names)
    
    print("\n实验完成！")

if __name__ == "__main__":
    main()