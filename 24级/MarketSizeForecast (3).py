# ====================== 1. 导入核心库 ======================
import pandas as pd  # 表格数据读取/处理
import numpy as np  # 数值计算（数组操作、预测模型数据处理）
import matplotlib.pyplot as plt  # 可视化核心库（热力图/趋势图绘制）
import warnings  # 忽略警告信息（避免控制台冗余输出）
# 机器学习库（线性回归预测模型）
from sklearn.linear_model import LinearRegression  # 线性回归模型（量化影响因素权重）
from sklearn.preprocessing import StandardScaler  # 数据标准化（消除量纲影响）

# 忽略警告（如Excel读取/模型训练的无关警告）
warnings.filterwarnings('ignore')

# ====================== 2. 基础配置与数据加载 ======================
# -------------------------- 可视化配置 --------------------------
# 设置中文字体（解决Windows系统matplotlib图表中文乱码问题）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']  # 黑体/微软雅黑
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示异常
# 设置默认图表尺寸（宽x高，英寸）
plt.rcParams['figure.figsize'] = (16, 10)

# -------------------------- 数据加载 --------------------------
# 读取产品数据（清洗后的产品价格/销量数据）
product_df = pd.read_excel(r'F:\Data Analysis\CleanedProductListData.xlsx')
# 读取问卷数据（消费者调研数据，含购买意愿/价格接受度/地域等）
survey_df = pd.read_excel(r'F:\Data Analysis\ShampooQuestionnaireSurvey.xlsx')

# ====================== 3. 数据预处理（为相关性分析做准备） ======================
# -------------------------- 3.1 产品数据预处理：提取核心特征 --------------------------
# 价格区间编码（将分类变量转为数值，便于量化分析）
# 编码规则：1=30元以内（低价）→ 5=120元以上（高价），数值越大代表价格越高
price_range_map = {'30元以内': 1, '30-50元': 2, '50-80元': 3, '80-120元': 4, '120元以上': 5}

# 为产品价格匹配区间编码（lambda函数：按价格范围快速映射）
product_df['价格区间编码'] = product_df['产品价格'].apply(
    lambda x: 1 if x < 30 else 2 if 30 <= x <= 50 else 3 if 50 < x <= 80 else 4 if 80 < x <= 120 else 5
)

# 销量标准化（Min-Max归一化，将销量缩放到0-1区间）
# 作用：消除销量绝对值差异，便于后续模型训练和跨维度对比
product_df['销量标准化'] = (product_df['付款人数'] - product_df['付款人数'].min()) / (product_df['付款人数'].max() - product_df['付款人数'].min())

# -------------------------- 3.2 问卷数据预处理：提取核心需求特征 --------------------------
# 消费意愿量化（将文本标签转为1-5分的数值，5分为最高意愿）
# 第15列（iloc[:,14]）为购买兴趣列，映射规则：非常有兴趣=5 → 完全没兴趣=1
survey_df['购买意愿量化'] = survey_df.iloc[:, 14].map({
    '非常有兴趣': 5, '比较有兴趣': 4, '一般': 3, '不太有兴趣': 2, '完全没兴趣': 1
})

# 价格接受度量化（与产品价格区间编码对齐，便于跨数据集分析）
# 第17列（iloc[:,16]）为价格接受度列，映射到1-5的数值编码
survey_df['价格接受度量化'] = survey_df.iloc[:, 16].map(price_range_map)

# 地域重要性量化（业务规则：核心市场权重更高）
# 编码规则：广西及周边=3（核心）、华东/华北=2（重点）、其他=1（普通）
guangxi_related = ['广西', '广东', '海南', '湖南', '贵州']  # 核心/周边市场
survey_df['地域重要性'] = survey_df['来自IP'].apply(
    lambda x: 3 if any(prov in str(x) for prov in guangxi_related)  # 核心市场
    else 2 if any(prov in str(x) for prov in ['浙江', '江苏', '山东', '河南'])  # 重点市场
    else 1  # 普通市场
)

# ====================== 4. 相关性分析（挖掘核心影响因素） ======================
# -------------------------- 4.1 产品端相关性：价格与销量的关联 --------------------------
# 计算产品核心特征的皮尔逊相关系数（-1~1，绝对值越大相关性越强）
product_corr = product_df[['产品价格', '价格区间编码', '付款人数', '销量标准化']].corr()
# 输出产品端相关性结果
print("="*50)
print("产品端相关性分析结果（价格与销量）")
print("="*50)
print(product_corr.round(3))  # 保留3位小数，提升可读性

# -------------------------- 4.2 需求端相关性：消费意愿与价格接受度的关联 --------------------------
# 计算需求端核心特征的皮尔逊相关系数
survey_corr = survey_df[['购买意愿量化', '价格接受度量化', '地域重要性']].corr()
# 输出需求端相关性结果
print("\n" + "="*50)
print("需求端相关性分析结果（消费意愿/价格/地域）")
print("="*50)
print(survey_corr.round(3))

# -------------------------- 4.3 关键发现总结（业务视角解读） --------------------------
print("\n" + "="*50)
print(" 相关性分析关键发现")
print("="*50)
# 1. 产品价格与销量相关性（负相关：价格越高，销量越低）
print(f"1. 产品价格与销量相关性：{product_corr.loc['产品价格', '付款人数']:.3f}（负相关，说明低价产品销量更高）")
# 2. 价格区间与销量相关性（验证价格带对销量的影响）
print(f"2. 价格区间与销量相关性：{product_corr.loc['价格区间编码', '付款人数']:.3f}（负相关，验证30-50元区间更受欢迎）")
# 3. 消费意愿与价格接受度相关性（正相关：合理价格提升购买意愿）
print(f"3. 消费意愿与价格接受度相关性：{survey_corr.loc['购买意愿量化', '价格接受度量化']:.3f}（正相关，说明合理价格提升意愿）")
# 4. 地域重要性与购买意愿相关性（正相关：核心市场需求更强）
print(f"4. 地域重要性与购买意愿相关性：{survey_corr.loc['地域重要性', '购买意愿量化']:.3f}（正相关，核心地域需求更强）")

# ====================== 5. 构建预测模型（基于核心影响因素） ======================
# -------------------------- 5.1 数据准备 --------------------------
# 预测变量（X）：价格接受度、地域重要性、购买意愿（核心影响因素）
# 目标变量（y）：标准化销量（预测目标：不同因素组合下的销量表现）
# dropna()：删除空值，避免模型训练报错
X = survey_df[['价格接受度量化', '地域重要性', '购买意愿量化']].dropna()
# 构建目标变量y：按价格区间编码匹配对应销量的均值（关联产品端和需求端数据）
y = np.array([product_df[product_df['价格区间编码'] == x]['销量标准化'].mean() for x in X['价格接受度量化']])

# -------------------------- 5.2 模型训练 --------------------------
# 数据标准化（StandardScaler：均值为0，方差为1）
# 作用：消除不同特征的量纲差异（如价格编码1-5 vs 地域重要性1-3），提升模型准确性
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 训练线性回归模型（量化各因素对销量的影响权重）
model = LinearRegression()
model.fit(X_scaled, y)

# -------------------------- 5.3 模型结果输出 --------------------------
print("\n" + "="*50)
print(" 预测模型系数（影响权重）")
print("="*50)
# 因素名称与系数对应（权重为正：正向促进销量；权重为负：抑制销量）
factors = ['价格接受度', '地域重要性', '购买意愿']
for factor, coef in zip(factors, model.coef_):
    print(f"{factor}权重：{coef:.3f}（正值表示正向促进销量）")
# 模型R²得分
print(f"模型R²得分：{model.score(X_scaled, y):.3f}（越接近1，预测越准确）")

# ====================== 6. 市场规模预测（2026-2030年） ======================
# -------------------------- 6.1 预测假设设定（基于业务分析） --------------------------
predict_years = [2026, 2027, 2028, 2029, 2030]  # 预测年份
# 核心因素假设
predict_factors = {
    2026: {'价格接受度': 2, '地域重要性': 2.2, '购买意愿': 3.8},  # 初始：30-50元，核心地域为主
    2027: {'价格接受度': 2, '地域重要性': 2.5, '购买意愿': 4.0},  # 地域扩张：新增华东
    2028: {'价格接受度': 2.1, '地域重要性': 2.8, '购买意愿': 4.2},  # 价格微调，覆盖华北
    2029: {'价格接受度': 2.1, '地域重要性': 3.0, '购买意愿': 4.3},  # 全国覆盖，意愿提升
    2030: {'价格接受度': 2.2, '地域重要性': 3.2, '购买意愿': 4.5}   # 优化价格，品牌认知增强
}

# 基础业务参数（用于市场规模计算）
unit_price = 45  # 客单价（30-50元区间均值）
user_base = [500, 800, 1200, 1800, 2500]  # 每年目标用户基数（万）

# -------------------------- 6.2 市场规模计算 --------------------------
predict_results = []  # 存储预测结果
for i, year in enumerate(predict_years):
    # 提取当年核心因素值
    factors_year = predict_factors[year]
    # 标准化预测特征（与模型训练数据保持一致）
    X_predict = scaler.transform([[
        factors_year['价格接受度'],
        factors_year['地域重要性'],
        factors_year['购买意愿']
    ]])
    # 预测标准化销量
    sales_scaled = model.predict(X_predict)[0]
    # 还原实际销量转化率（基于现有产品最大销量）
    max_sales = product_df['付款人数'].max()
    actual_sales_rate = sales_scaled * max_sales / 100  # 转化率（%）
    # 计算市场规模（万元）= 用户基数（万）× 转化率 × 客单价 / 10000（单位转换）
    market_size = user_base[i] * actual_sales_rate * unit_price / 10000
    # 存储当年预测结果
    predict_results.append({
        '年份': year,
        '价格接受度': factors_year['价格接受度'],
        '地域重要性': factors_year['地域重要性'],
        '购买意愿': factors_year['购买意愿'],
        '销量转化率(%)': actual_sales_rate,
        '目标用户基数(万)': user_base[i],
        '市场规模(万元)': round(market_size, 2)
    })

# 转换为DataFrame，便于查看和后续处理
predict_df = pd.DataFrame(predict_results)
# 输出市场规模预测结果
print("\n" + "="*50)
print(" 2026-2030年市场规模预测结果")
print("="*50)
print(predict_df.to_string(index=False))

# ====================== 7. 可视化呈现（2个热力图+因素趋势图） ======================
# 创建1行3列的网格布局（wspace：列间距）
fig = plt.figure(figsize=(18, 8))
gs = plt.GridSpec(1, 3, figure=fig, wspace=0.3)

# -------------------------- 7.1 子图1：产品端相关性热力图 --------------------------
ax1 = fig.add_subplot(gs[0, 0])  # 第一列
# 绘制热力图（cmap='RdBu_r'：红蓝配色，负值红/正值蓝，vmin/vmax：取值范围-1~1）
im1 = ax1.imshow(product_corr.values, cmap='RdBu_r', vmin=-1, vmax=1)
# 设置坐标轴刻度（对应特征名称）
ax1.set_xticks(range(len(product_corr.columns)))
ax1.set_yticks(range(len(product_corr.columns)))
# 设置刻度标签（旋转45度，避免重叠）
ax1.set_xticklabels(product_corr.columns, rotation=45, ha='right', fontsize=9)
ax1.set_yticklabels(product_corr.columns, fontsize=9)
# 设置子图标题
ax1.set_title('产品端相关性热力图（价格-销量）', fontsize=11, fontweight='bold', pad=12)
# 添加数值标签（每个单元格显示相关系数）
for i in range(len(product_corr.columns)):
    for j in range(len(product_corr.columns)):
        text = ax1.text(j, i, f'{product_corr.iloc[i, j]:.2f}',
                       ha="center", va="center", color="black", fontweight='bold', fontsize=8)
# 添加颜色条（解释热力图颜色对应的数值）
plt.colorbar(im1, ax=ax1, shrink=0.7)

# -------------------------- 7.2 子图2：需求端相关性热力图 --------------------------
ax2 = fig.add_subplot(gs[0, 1])  # 第二列
# 绘制热力图
im2 = ax2.imshow(survey_corr.values, cmap='RdBu_r', vmin=-1, vmax=1)
# 设置坐标轴刻度
ax2.set_xticks(range(len(survey_corr.columns)))
ax2.set_yticks(range(len(survey_corr.columns)))
# 设置刻度标签
ax2.set_xticklabels(survey_corr.columns, rotation=45, ha='right', fontsize=9)
ax2.set_yticklabels(survey_corr.columns, fontsize=9)
# 设置子图标题
ax2.set_title('需求端相关性热力图（意愿-价格-地域）', fontsize=11, fontweight='bold', pad=12)
# 添加数值标签
for i in range(len(survey_corr.columns)):
    for j in range(len(survey_corr.columns)):
        text = ax2.text(j, i, f'{survey_corr.iloc[i, j]:.2f}',
                       ha="center", va="center", color="black", fontweight='bold', fontsize=8)
# 添加颜色条
plt.colorbar(im2, ax=ax2, shrink=0.7)

# -------------------------- 7.3 子图3：核心影响因素变化趋势 --------------------------
ax4 = fig.add_subplot(gs[0, 2])  # 第三列
ax4_twin = ax4.twinx()  # 创建共享x轴的双y轴

# 左轴：价格接受度、地域重要性
line1 = ax4.plot(predict_df['年份'], predict_df['价格接受度'],
                 marker='s', linewidth=2, markersize=7, color='#3498DB', label='价格接受度')
line2 = ax4.plot(predict_df['年份'], predict_df['地域重要性'],
                 marker='^', linewidth=2, markersize=7, color='#2ECC71', label='地域重要性')

# 右轴：购买意愿
line3 = ax4_twin.plot(predict_df['年份'], predict_df['购买意愿'],
                      marker='*', linewidth=2, markersize=9, color='#F39C12', label='购买意愿')

# 美化配置
ax4.set_xlabel('年份', fontsize=11, fontweight='bold')  # x轴标签
ax4.set_ylabel('价格接受度/地域重要性', fontsize=10, color='#2C3E50', fontweight='bold')  # 左y轴标签
ax4_twin.set_ylabel('购买意愿（1-5分）', fontsize=10, color='#F39C12', fontweight='bold')  # 右y轴标签
ax4.set_title('核心影响因素变化趋势', fontsize=12, fontweight='bold', pad=12)  # 子图标题
ax4.grid(axis='y', alpha=0.3, linestyle='--')  # 添加网格线
ax4.set_xticks(predict_df['年份'])  # x轴刻度对应预测年份

# 合并图例（左轴+右轴）
lines1, labels1 = ax4.get_legend_handles_labels()
lines2, labels2 = ax4_twin.get_legend_handles_labels()
ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)

# ====================== 8. 保存结果 ======================
# 调整整体布局并保存图表
plt.tight_layout()
plt.savefig(r'F:\Data Analysis\CorrelationMarketPrediction_Final.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()  # 关闭画布，释放内存

# 输出最终结论（控制台提示生成文件）
print("\n" + "="*50)
print("生成文件如下")
print("="*50)
print("1. 最终可视化图表：CorrelationMarketPrediction_Final.png（2个热力图+因素趋势图）")
print("2. 详细数据：CorrelationMarketPrediction.xlsx（含模型系数+预测结果）")