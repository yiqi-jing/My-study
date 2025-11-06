import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 1. 加载鸢尾花数据集并选择特征
iris = datasets.load_iris()
X = iris.data[:, [0, 2]]  # 选择第0列（花萼长度）和第2列（花瓣长度）
y = iris.target

# 2. 划分训练集和测试集（与题目代码保持一致）
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.4, random_state=42
)

# ========== （1）分析决策树深度对预测精度的影响 ==========
depths = [2, 6, 10, 15, 20]
accuracies = []

for depth in depths:
    # 训练不同深度的决策树
    dt = DecisionTreeClassifier(max_depth=depth, random_state=42)
    dt.fit(X_train, y_train)
    # 测试集预测精度
    y_pred = dt.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    accuracies.append(acc)
    print(f"决策树深度{depth}时，测试精度：{acc:.4f}")

# 绘制柱状图
plt.bar(range(len(depths)), accuracies, tick_label=depths)
plt.xlabel('决策树深度')
plt.ylabel('测试精度')
plt.title('决策树深度对鸢尾花分类精度的影响')
plt.show()

# ========== （2）绘制决策树在训练样本上的分类效果图 ==========
def plot_decision_boundary(model, X, y, feature_names):
    """绘制决策边界，展示分类效果"""
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    # 生成网格点
    xx, yy = np.meshgrid(
        np.arange(x_min, x_max, 0.02),
        np.arange(y_min, y_max, 0.02)
    )
    # 预测网格点类别
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    # 绘制等高线（决策边界）和散点（训练样本）
    plt.contourf(xx, yy, Z, alpha=0.4)
    plt.scatter(X[:, 0], X[:, 1], c=y, s=20, edgecolor='k')
    plt.xlabel(feature_names[0])
    plt.ylabel(feature_names[2])
    plt.title('决策树在训练样本上的分类效果')
    plt.show()

# 训练决策树（以深度6为例，可任选深度）
dt = DecisionTreeClassifier(max_depth=6, random_state=42)
dt.fit(X_train, y_train)
# 绘制决策边界
plot_decision_boundary(dt, X_train, y_train, iris.feature_names)