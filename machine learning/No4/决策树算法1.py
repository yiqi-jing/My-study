import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# 1. 构建数据集
data = {
    '天气': ['晴天', '晴天', '阴天', '雨天', '雨天', '雨天', '阴天', '晴天', '晴天', '雨天', '雨天', '晴天', '雨天', '阴天', '阴天', '晴天'],
    '温度': ['热', '热', '热', '温和', '冷', '冷', '冷', '温和', '冷', '温和', '温和', '冷', '冷', '温和', '冷', '热'],
    '风': ['无风', '有风', '无风', '无风', '无风', '有风', '有风', '无风', '无风', '无风', '有风', '无风', '有风', '无风', '无风', '有风'],
    '是否打球': ['否', '否', '是', '是', '是', '否', '是', '否', '是', '是', '否', '是', '否', '是', '是', '否']
}
df = pd.DataFrame(data)

# 2. 分类变量编码（将字符串转换为数值）
le = LabelEncoder()
df['天气'] = le.fit_transform(df['天气'])   # 晴天=0, 阴天=1, 雨天=2
df['温度'] = le.fit_transform(df['温度'])   # 热=0, 温和=1, 冷=2
df['风'] = le.fit_transform(df['风'])       # 无风=0, 有风=1
df['是否打球'] = le.fit_transform(df['是否打球'])  # 否=0, 是=1

# 3. 划分特征(X)和标签(y)
X = df[['天气', '温度', '风']]
y = df['是否打球']

# 4. 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 5. 训练决策树模型
dt_model = DecisionTreeClassifier(random_state=42)
dt_model.fit(X_train, y_train)

# 6. 预测并计算精度
y_pred = dt_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("小明打网球决策树预测精度：", accuracy)

# 7. 预测“明天”是否打球（示例：假设明天天气=晴天(0)、温度=温和(1)、风=无风(0)）
tomorrow_feature = [[0, 1, 0]]  # 对应编码后的特征
tomorrow_pred = dt_model.predict(tomorrow_feature)
print("明天是否打球预测（0=否，1=是）：", tomorrow_pred)