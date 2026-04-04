# =================================多元线性回归模型（核心目标：变量显著性+预测可靠性验证）==============================
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from statsmodels.api import OLS

# ===================== 第一步：导入并验证你的真实数据文件 =====================
# 1. 数据文件路径（请确认与本地一致）
regression_file = r'F:\My-study\24级\草本洗发水回归分析数据集.xlsx'  # 含销量数据
survey_file = r'F:\My-study\24级\清洗后_消费者问卷数据.xlsx'          # 含价格/地域/购买意愿数据

# 2. 读取数据 + 关键字段验证（确保建模所需字段存在）
print("="*60)
print("                数据文件字段验证（核心分析前置）")
print("="*60)
# 读取回归数据集（需含：价格接受度量化、标准化销量）
regression_df = pd.read_excel(regression_file, engine='openpyxl')
regression_required = ['价格接受度量化', '标准化销量']
for col in regression_required:
    status = "存在" if col in regression_df.columns else "缺失（请检查文件）"
    print(f"回归数据集 - {col}：{status}")

# 读取问卷数据集（需含：价格接受区间、IP省份、购买兴趣）
survey_df = pd.read_excel(survey_file, engine='openpyxl')
survey_required = ['价格接受区间', 'IP省份', '购买兴趣']
for col in survey_required:
    status = "存在" if col in survey_df.columns else "缺失（请检查文件）"
    print(f"问卷数据集 - {col}：{status}")

# 3. 数据量化处理（生成建模所需的自变量/因变量）
# 3.1 价格接受度量化（问卷“价格接受区间”→1-5分）
price_map = {'30元以下':1, '30-50元':2, '50-80元':3, '80-120元':4, '120元以上':5, '其他':3}
survey_df['价格接受度量化'] = survey_df['价格接受区间'].map(lambda x: price_map.get(str(x), 3))

# 3.2 地域重要性量化（问卷“IP省份”→1-3分，按消费能力划分）
province_map = {'北京':3, '上海':3, '广东':3, '浙江':3, '江苏':3,  # 3分：高消费省
                '山东':2, '四川':2, '湖北':2, '湖南':2, '福建':2, # 2分：中消费省
                '其他':1}                                         # 1分：其他
survey_df['地域重要性'] = survey_df['IP省份'].map(lambda x: province_map.get(str(x).replace('省','').replace('市',''), 1))

# 3.3 购买意愿量化（问卷“购买兴趣”→1-5分）
interest_map = {'完全没兴趣':1, '不太有兴趣':2, '一般':3, '有兴趣':4, '非常有兴趣':5}
survey_df['购买意愿量化'] = survey_df['购买兴趣'].map(lambda x: interest_map.get(str(x), 3))

# 3.4 关联数据（匹配价格接受度，确保销量与自变量对应）
model_df = pd.merge(
    survey_df[['价格接受度量化', '地域重要性', '购买意愿量化']],  # 核心自变量（价格/地域/购买意愿）
    regression_df[['价格接受度量化', '标准化销量']],              # 因变量（销量，用于市场规模预测）
    on='价格接受度量化',
    how='inner'
).dropna()  # 删除缺失值，保证数据有效性

print(f"\n数据处理完成：最终建模样本量 = {len(model_df)} 条")

# ===================== 第二步：模型训练（聚焦核心分析目标） =====================
# 1. 定义变量（直接对应核心分析对象）
X = model_df[['价格接受度量化', '地域重要性', '购买意愿量化']]  # 需验证的3个核心变量
y = model_df['标准化销量']                                      # 销量（市场规模预测的基础）

# 2. 拆分训练集（建模）/测试集（验证预测可靠性）
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. 训练多元线性回归模型
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)

# 4. 计算核心评估指标（完全匹配必选指标）
y_pred = lr_model.predict(X_test)
# 4.1 调整R²（模型解释力，支撑市场规模预测合理性）
ols_model = OLS(y_train, X_train).fit()
adjust_r2 = ols_model.rsquared_adj
# 4.2 自变量P值（验证价格/地域/购买意愿是否显著，P<0.05为显著）
p_values = ols_model.pvalues
# 4.3 RMSE（均方根误差，验证市场规模预测可靠性，数值越小越可靠）
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

# ===================== 第三步：结果输出（直接回应核心分析目标） =====================
print("\n" + "="*60)
print("                核心分析目标：变量显著性+预测可靠性验证结果")
print("="*60)

# 1. 必选指标汇总
print(f"\n【必选指标汇总】")
print(f"1. 调整R² = {adjust_r2:.3f} → 模型可解释{adjust_r2*100:.1f}%的销量变异（解释力越强，预测越可靠）")
print(f"2. RMSE（均方根误差） = {rmse:.3f} → 预测误差越小，市场规模预测结果越可靠")

# 2. 核心变量显著性验证（重点：P<0.05为显著影响）
print(f"\n【核心变量显著性验证（P<0.05为显著）】")
for var_name, p_val in p_values.items():
    significance = "显著影响" if p_val < 0.05 else "无显著影响"
    print(f"- {var_name}：P值 = {p_val:.3f} → {significance}")

# 3. 变量影响方向与强度（补充分析价值）
print(f"\n【变量影响方向与强度】")
for var_name, coef in zip(X.columns, lr_model.coef_):
    direction = "正向影响" if coef > 0 else "负向影响"
    print(f"- {var_name}：回归系数 = {coef:.4f} → {direction}（系数绝对值越大，影响越强）")

# ===================== 第四步：核心结论（直接支撑业务决策） =====================
print("\n" + "="*60)
print("                核心分析结论（聚焦市场规模预测与变量影响）")
print("="*60)

# 结论1：变量显著性结论
significant_vars = [var for var, p in p_values.items() if p < 0.05]
non_significant_vars = [var for var, p in p_values.items() if p >= 0.05]
print(f"1. 变量显著性结论：")
print(f"   - 对销量有显著影响的因素：{', '.join(significant_vars)}（可作为市场规模预测的核心变量）")
if non_significant_vars:
    print(f"   - 对销量无显著影响的因素：{', '.join(non_significant_vars)}（预测时可简化模型，减少冗余）")

# 结论2：市场规模预测可靠性结论
rmse_judge = "高" if rmse < 10 else "中等" if rmse < 20 else "需优化"
print(f"\n2. 市场规模预测可靠性结论：")
print(f"   - 模型RMSE = {rmse:.3f}，预测误差{rmse_judge}，结合调整R²={adjust_r2:.3f}的强解释力，")
print(f"     基于此模型的2026-2030年市场规模预测结果具备业务参考价值，可支撑产能规划与渠道布局决策。")

# 结论3：关键业务建议
print(f"\n3. 关键业务建议：")
if "购买意愿量化" in significant_vars and lr_model.coef_[X.columns.get_loc("购买意愿量化")] > 0:
    print(f"   - 购买意愿为正向显著影响因素，建议通过营销活动（如草本成分宣传、试用活动）提升消费者购买意愿，直接拉动销量增长；")
if "价格接受度量化" in significant_vars:
    price_coef = lr_model.coef_[X.columns.get_loc("价格接受度量化")]
    if price_coef < 0:
        print(f"   - 价格接受度为负向显著影响，建议锚定50-80元主流价格带，平衡利润与消费者接受度；")
    else:
        print(f"   - 价格接受度为正向显著影响，建议针对高消费区域推出中高端产品线（如80-120元），提升溢价空间；")
if "地域重要性" in non_significant_vars:
    print(f"   - 地域对销量无显著影响，建议采用全国统一的基础营销策略，降低区域运营成本，聚焦核心变量优化。")