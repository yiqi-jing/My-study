# ====================== 1. 导入核心库 ======================
# 数据处理核心库
import pandas as pd  # 表格数据读取/处理
import numpy as np   # 数值计算
# 可视化库
import matplotlib.pyplot as plt  # 图表绘制
# 文本处理库
import re  # 正则表达式：清理文本中的特殊字符
import jieba  # 中文分词
# 机器学习库（朴素贝叶斯分类）
from sklearn.feature_extraction.text import CountVectorizer  # 文本特征提取
from sklearn.naive_bayes import MultinomialNB  # 朴素贝叶斯分类器
from sklearn.model_selection import train_test_split  # 划分训练/测试集
from sklearn.metrics import classification_report, accuracy_score  # 模型评估指标
from sklearn.preprocessing import LabelEncoder  # 标签编码
# 辅助库
import warnings  # 忽略警告信息

# ====================== 全局配置 ======================
# 忽略警告
warnings.filterwarnings('ignore')
# 设置中文字体（解决matplotlib图表中文乱码问题）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']  # 黑体/微软雅黑
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示异常

# ====================== 2. 配置类 ======================

class Config:
    # ① 情感标签与关键词映射
    SENTIMENT_KEYWORDS = {
        '正面': ['控油清爽', '去屑止痒', '防脱、固发', '防脱', '固发',
                 '修护干枯', '柔顺亮泽', '天然温和、不伤头皮', '天然温和',
                 '比较有兴趣', '非常有兴趣'],  # 正向反馈关键词
        '负面': ['气味不习惯', '价格偏高', '担心成分不安全', '担心效果不好',
                 '完全没兴趣'],  # 负向反馈关键词
        '中性': ['不了解这类产品', '一般', '不太有兴趣']  # 中性反馈关键词
    }

    # ② 核心关注点与关键词映射
    FOCUS_KEYWORDS = {
        '功效': ['控油清爽', '去屑止痒', '防脱、固发', '防脱', '固发',
                 '修护干枯', '柔顺亮泽', '天然温和、不伤头皮', '天然温和',
                 '担心效果不好'],  # 产品功效相关
        '成分安全': ['担心成分不安全'],  # 成分安全相关
        '价格': ['价格偏高', '价格'],  # 价格相关
        '气味': ['气味不习惯'],  # 气味相关
        '其他': ['不容易购买', '不了解这类产品', '其他']  # 其他维度
    }

    # ③ Excel原始列名映射
    RAW_COLUMNS = {
        '是否使用': '4、您是否使用草本熬制洗发水',  # 用户类型（使用/不使用）
        '不使用原因': '5、您不使用草本熬制洗发水的主要原因',  # 不使用用户反馈
        '使用原因': '6、您使用草本熬制洗发水的主要原因',  # 使用用户反馈
        '购买兴趣': '9、有一款草本熬制洗发水，主要采用天然原料熬制而成，不添加任何化学材料，宣称能“去屑止痒、控油蓬松、养发固发、柔顺亮泽”，您的购买兴趣有多大',  # 购买兴趣度
        '建议意见': '13、您对草本熬制洗发水有什么建议/意见'  # 额外建议（备用）
    }

    # ④ 文件路径配置（输入/输出文件）
    INPUT_EXCEL = r"F:\Data Analysis\ShampooQuestionnaireSurvey.xlsx"  # 原始问卷数据
    OUTPUT_EXCEL = "草本洗发水_消费者情感分析结果.xlsx"  # 处理后的数据
    OUTPUT_SENTIMENT_PLOT = "购买兴趣情感分布.png"  # 情感分布饼图
    OUTPUT_FOCUS_PLOT = "核心关注点分布.png"  # 关注点分布柱状图


# ====================== 3. 文本预处理类 ======================
class TextPreprocessor:
    def __init__(self):
        # 初始化时加载配置
        self.config = Config()

    # -------------------------- 方法1：文本清洗 --------------------------
    def clean_text(self, text):
        # 处理空值
        if pd.isna(text):
            return ""
        # 转为字符串并去除首尾空格
        text = str(text).strip()
        # 剔除"跳过"相关无效数据
        if "跳过" in text or "(跳过)" in text:
            return ""
        # 正则表达式清理标点符号
        text = re.sub(r'[：，。！？""''()（）\s]', '', text)
        return text

    # -------------------------- 方法2：统一表述 --------------------------
    def unify_expression(self, text):
        text = text.replace("防脱、固发", "防脱固发")  # 统一防脱相关表述
        text = text.replace("天然温和、不伤头皮", "天然温和")  # 统一天然温和表述
        return text

    # -------------------------- 方法3：情感标签标注 --------------------------
    def label_sentiment(self, text):
        # 空文本默认中性
        if not text:
            return "中性"
        # 按优先级匹配情感关键词
        for sentiment, keywords in self.config.SENTIMENT_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return sentiment
        # 无匹配关键词时默认中性
        return "中性"

    # -------------------------- 方法4：核心关注点提取 --------------------------
    def extract_focus(self, text):
        if not text:
            return "其他"
        focus_list = []
        # 匹配所有相关关注点
        for focus, keywords in self.config.FOCUS_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                focus_list.append(focus)
        # 多关注点用"、"分隔，无匹配则为"其他"
        return "、".join(focus_list) if focus_list else "其他"


# ====================== 4. 数据读取与预处理主流程 ======================
def load_and_preprocess_data():
    # 加载配置和预处理工具
    config = Config()
    processor = TextPreprocessor()

    # 1. 读取原始Excel数据
    try:
        df = pd.read_excel(config.INPUT_EXCEL)
        print(f" 成功读取原始数据：共{df.shape[0]}条记录，{df.shape[1]}列")
    except Exception as e:
        print(f" 读取Excel失败：{e}")
        return None

    # 2. 检查必要列是否存在
    required_cols = list(config.RAW_COLUMNS.values())
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f" 缺失必要列：{missing_cols}")
        return None

    # 3. 核心预处理步骤
    processed_df = df.copy()

    # 3.1 清洗使用/不使用原因（剔除"跳过"数据）
    processed_df['不使用原因_清洗'] = processed_df[config.RAW_COLUMNS['不使用原因']].apply(processor.clean_text)
    processed_df['使用原因_清洗'] = processed_df[config.RAW_COLUMNS['使用原因']].apply(processor.clean_text)

    # 3.2 合并用户反馈
    def merge_feedback(row):
        use_reason = row['使用原因_清洗']
        not_use_reason = row['不使用原因_清洗']
        return use_reason if use_reason else not_use_reason
    processed_df['用户反馈'] = processed_df.apply(merge_feedback, axis=1)  # axis=1：按行处理

    # 3.3 统一表述
    processed_df['用户反馈'] = processed_df['用户反馈'].apply(processor.unify_expression)

    # 3.4 提取核心字段
    processed_df['用户类型'] = processed_df[config.RAW_COLUMNS['是否使用']]  # 使用/不使用
    processed_df['购买兴趣程度'] = processed_df[config.RAW_COLUMNS['购买兴趣']]  # 购买兴趣原始值
    processed_df['购买兴趣_清洗'] = processed_df['购买兴趣程度'].apply(processor.clean_text)  # 清洗购买兴趣

    # 3.5 标注情感类别
    processed_df['合并文本'] = processed_df['用户反馈'] + processed_df['购买兴趣_清洗']
    processed_df['情感类别'] = processed_df['合并文本'].apply(processor.label_sentiment)

    # 3.6 提取最终关注点
    processed_df['最终关注点'] = processed_df['合并文本'].apply(processor.extract_focus)

    # 3.7 筛选最终输出列并格式化
    final_df = processed_df[[
        config.RAW_COLUMNS['是否使用'],  # 用户类型
        '用户反馈',
        config.RAW_COLUMNS['购买兴趣'],  # 购买兴趣程度
        '情感类别',
        '最终关注点'
    ]].copy()

    # 重命名列名
    final_df.rename(columns={
        config.RAW_COLUMNS['是否使用']: '用户类型',
        config.RAW_COLUMNS['购买兴趣']: '购买兴趣程度'
    }, inplace=True)

    # 添加序号列
    final_df.insert(0, '序号', range(1, len(final_df) + 1))

    # 剔除所有无效数据
    final_df = final_df[final_df['用户反馈'] != ""].reset_index(drop=True)
    print(f"✅ 数据预处理完成：有效数据{final_df.shape[0]}条")

    return final_df


# ====================== 5. 朴素贝叶斯模型训练（情感分类） ======================
def train_naive_bayes_model(df):
    # 1. 准备训练数据（文本特征X + 情感标签y）
    X = df['用户反馈'].values  # 特征：用户反馈文本
    y = df['情感类别'].values  # 标签：情感类别（正面/负面/中性）

    # 过滤空文本（避免模型训练报错）
    valid_idx = [i for i, text in enumerate(X) if text != ""]
    X = [X[i] for i in valid_idx]
    y = [y[i] for i in valid_idx]

    # 样本不足时跳过训练（避免模型过拟合）
    if len(X) < 10:
        print(" 有效样本不足10条，跳过模型训练")
        return None, None, None

    # 2. 中文文本特征提取（词袋模型）
    vectorizer = CountVectorizer(
        tokenizer=jieba.lcut,  # 中文分词：jieba.lcut返回分词列表
        stop_words=['的', '了', '是', '在'],  # 停用词：无实际意义的虚词
        ngram_range=(1, 2),  # 特征范围：单字+双词（如"控油"+"控油清爽"）
        max_features=200  # 限制最大特征数：避免维度爆炸/过拟合
    )
    X_vec = vectorizer.fit_transform(X)  # 文本→稀疏矩阵（词频特征）

    # 3. 标签编码（文本标签→数值：正面=0/负面=1/中性=2）
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # 4. 划分训练集/测试集（8:2比例，random_state保证结果可复现）
    X_train, X_test, y_train, y_test = train_test_split(
        X_vec, y_encoded, test_size=0.2, random_state=42
    )

    # 5. 训练朴素贝叶斯模型（MultinomialNB适合离散特征如词频）
    nb_model = MultinomialNB(alpha=0.5)  # alpha：平滑参数，避免零概率问题
    nb_model.fit(X_train, y_train)

    # 6. 模型评估（准确率+分类报告）
    y_pred = nb_model.predict(X_test)  # 测试集预测
    accuracy = accuracy_score(y_test, y_pred)  # 整体准确率
    # 分类报告：精确率/召回率/F1值（按类别细分）
    report = classification_report(
        y_test, y_pred, target_names=le.classes_, zero_division=0
    )

    # 输出评估结果
    print("\n 朴素贝叶斯模型评估结果：")
    print(f"准确率：{accuracy:.4f} ({accuracy * 100:.1f}%)")
    print("分类报告：\n", report)

    return nb_model, vectorizer, le


# ====================== 6. 数据可视化（情感分布+关注点分布） ======================
def visualize_data(df):
    config = Config()

    # -------------------------- 子图1：购买兴趣情感分布饼图 --------------------------
    # 统计各情感类别数量
    sentiment_count = df['情感类别'].value_counts()
    # 设置画布大小
    plt.figure(figsize=(8, 8))
    # 定义颜色（正面绿、负面红、中性黄）
    colors = ['#2E8B57', '#DC143C', '#FFD700']
    # 绘制饼图
    plt.pie(
        sentiment_count.values,  # 数值
        labels=sentiment_count.index,  # 标签（正面/负面/中性）
        autopct='%1.1f%%',  # 显示百分比（保留1位小数）
        colors=colors[:len(sentiment_count)],  # 适配实际类别数
        startangle=90,  # 起始角度
        textprops={'fontsize': 12}  # 文本大小
    )
    # 设置标题
    plt.title('消费者购买兴趣情感分布', fontsize=14, fontweight='bold')
    # 紧凑布局
    plt.tight_layout()
    # 保存图表
    plt.savefig(config.OUTPUT_SENTIMENT_PLOT, dpi=300, bbox_inches='tight')
    plt.close()
    print(f" 购买兴趣情感分布图已保存：{config.OUTPUT_SENTIMENT_PLOT}")

    # -------------------------- 子图2：核心关注点分布柱状图 --------------------------
    # 拆分多关注点（以"、"分割，如"功效、价格"→["功效","价格"]）
    focus_list = []
    for focus in df['最终关注点']:
        focus_list.extend(focus.split('、'))
    # 统计各关注点数量
    focus_count = pd.Series(focus_list).value_counts()
    # 计算百分比
    total_focus = focus_count.sum()
    focus_percent = (focus_count / total_focus * 100).round(1)  # 保留1位小数

    # 设置画布大小
    plt.figure(figsize=(10, 6))
    # 定义颜色区分不同关注点
    colors = ['#4682B4', '#32CD32', '#FF6347', '#FFA500', '#9370DB']
    # 绘制柱状图
    bars = plt.bar(focus_percent.index, focus_percent.values, color=colors[:len(focus_percent)])

    # 设置坐标轴标签
    plt.xlabel('核心关注点', fontsize=12)
    plt.ylabel('占比（%）', fontsize=12)
    # 设置标题
    plt.title('核心关注点分布（成分安全/功效/价格/气味/其他）', fontsize=14, fontweight='bold')

    # 为每个柱子添加百分比数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2, height + 0.5,  # 标签位置（柱子顶部+0.5）
            f'{height}%', ha='center', va='bottom', fontsize=10  # 居中对齐
        )

    # 设置y轴范围（顶部留5%空白，避免标签超出画布）
    plt.ylim(0, max(focus_percent.values) + 5)

    # 紧凑布局+保存
    plt.tight_layout()
    plt.savefig(config.OUTPUT_FOCUS_PLOT, dpi=300, bbox_inches='tight')
    plt.close()
    print(f" 核心关注点分布图已保存：{config.OUTPUT_FOCUS_PLOT}")


# ====================== 7. 主函数（执行全流程） ======================
def main():
    # 步骤1：数据预处理（读取+清洗+标注）
    df = load_and_preprocess_data()
    if df is None:  # 数据读取失败时终止程序
        return

    # 步骤2：训练朴素贝叶斯模型（验证情感分类效果）
    model, vectorizer, le = train_naive_bayes_model(df)

    # 步骤3：保存处理后的数据到Excel（便于后续人工分析）
    df.to_excel(Config.OUTPUT_EXCEL, index=False)
    print(f"✅ 处理后的数据已保存：{Config.OUTPUT_EXCEL}")

    # 步骤4：生成可视化图表（直观展示分析结果）
    visualize_data(df)

    # 步骤5：输出统计摘要（快速了解核心结果）
    print("\n 数据统计摘要：")
    print(f"1. 有效样本数：{len(df)}")
    print(f"2. 情感分布：\n{df['情感类别'].value_counts()}")


    focus_list = [f for focus in df['最终关注点'] for f in focus.split('、')]
    focus_count = pd.Series(focus_list).value_counts()
    focus_percent = (focus_count / focus_count.sum() * 100).round(1)
    print(f"3. 核心关注点分布（百分比）：\n{focus_percent}")

# 程序入口
if __name__ == "__main__":
    main()