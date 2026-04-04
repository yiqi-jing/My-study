import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from collections import Counter
import warnings

warnings.filterwarnings('ignore')

# -------------------------- 基础配置 --------------------------
# 设置中文字体（Windows系统适配）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
# 图表样式配置
plt.rcParams['figure.figsize'] = (18, 14)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['xtick.major.width'] = 0.8
plt.rcParams['ytick.major.width'] = 0.8

# 全国标准省份/直辖市/自治区列表（含简称映射）
STANDARD_PROVINCES = {
    '北京': ['北京', '北京市'],
    '上海': ['上海', '上海市'],
    '天津': ['天津', '天津市'],
    '重庆': ['重庆', '重庆市'],
    '河北': ['河北', '河北省'],
    '山西': ['山西', '山西省'],
    '辽宁': ['辽宁', '辽宁省'],
    '吉林': ['吉林', '吉林省'],
    '黑龙江': ['黑龙江', '黑龙江省'],
    '江苏': ['江苏', '江苏省'],
    '浙江': ['浙江', '浙江省'],
    '安徽': ['安徽', '安徽省'],
    '福建': ['福建', '福建省'],
    '江西': ['江西', '江西省'],
    '山东': ['山东', '山东省'],
    '河南': ['河南', '河南省'],
    '湖北': ['湖北', '湖北省'],
    '湖南': ['湖南', '湖南省'],
    '广东': ['广东', '广东省'],
    '海南': ['海南', '海南省'],
    '四川': ['四川', '四川省'],
    '贵州': ['贵州', '贵州省'],
    '云南': ['云南', '云南省'],
    '陕西': ['陕西', '陕西省'],
    '甘肃': ['甘肃', '甘肃省'],
    '青海': ['青海', '青海省'],
    '台湾': ['台湾', '台湾省'],
    '内蒙古': ['内蒙古', '内蒙古自治区'],
    '广西': ['广西', '广西壮族自治区'],
    '西藏': ['西藏', '西藏自治区'],
    '宁夏': ['宁夏', '宁夏回族自治区'],
    '新疆': ['新疆', '新疆维吾尔自治区'],
    '香港': ['香港', '香港特别行政区'],
    '澳门': ['澳门', '澳门特别行政区']
}

# -------------------------- 数据读取与预处理 --------------------------
# 读取Excel文件
product_df = pd.read_excel(r'F:\Data Analysis\CleanedProductListData.xlsx')
survey_df = pd.read_excel(r'F:\Data Analysis\ShampooQuestionnaireSurvey.xlsx')

# 数据预处理1：产品价格与销量分组
price_ranges = ['30元以内', '30-50元', '50-80元', '80-120元', '120元以上']


def assign_price_range(price):
    if price < 30:
        return '30元以内'
    elif 30 <= price <= 50:
        return '30-50元'
    elif 50 < price <= 80:
        return '50-80元'
    elif 80 < price <= 120:
        return '80-120元'
    else:
        return '120元以上'


# 为产品添加价格区间标签
product_df['价格区间'] = product_df['产品价格'].apply(assign_price_range)
# 按价格区间统计总销量和产品数量
product_sales_by_price = product_df.groupby('价格区间').agg({
    '付款人数': 'sum',  # 该价格区间总销量
    '产品名称': 'count'  # 该价格区间产品数量
}).rename(columns={'产品名称': '产品数量'}).reindex(price_ranges)

# 问卷数据：按价格接受度统计人数（消费者需求占比）
survey_price_accept = survey_df.iloc[:, 16].value_counts()  # 16为价格接受度列索引
# 统一价格区间格式，确保与产品数据匹配
survey_price_dist = pd.Series(0, index=price_ranges)
for range_name in price_ranges:
    if range_name in survey_price_accept.index:
        survey_price_dist[range_name] = survey_price_accept[range_name]
# 计算消费者需求占比
survey_price_pct = (survey_price_dist / survey_price_dist.sum() * 100).round(1)


# -------------------------- 核心优化：标准地域统计 --------------------------
def normalize_province(province_name):
    """将省份名称标准化为全国统一格式"""
    if pd.isna(province_name) or province_name == '未知':
        return '未知'

    province_name = str(province_name).strip()
    # 匹配标准省份名称
    for std_prov, aliases in STANDARD_PROVINCES.items():
        if province_name in aliases or any(alias in province_name for alias in aliases):
            return std_prov
    # 无法匹配的归为"其他"
    return '其他'


def extract_standard_region(ip_info):
    """提取标准化的省份和城市信息"""
    if pd.isna(ip_info):
        return '未知', '未知'

    ip_str = str(ip_info).strip()
    # 匹配格式1：IP(省份-城市)
    match = re.search(r'\((.*?)-(.*?)\)', ip_str)
    if match:
        province_raw = match.group(1).strip()
        city_raw = match.group(2).strip()
        # 标准化省份名称
        province_std = normalize_province(province_raw)
        # 城市名称清理（去除特殊字符）
        city_std = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', str(city_raw))
        city_std = city_std.strip() if city_std.strip() else '未知'
        return province_std, city_std

    # 匹配格式2：IP(省份)
    match_province = re.search(r'\((.*?)\)', ip_str)
    if match_province:
        province_raw = match_province.group(1).strip()
        province_std = normalize_province(province_raw)
        return province_std, '未知'

    # 无法提取的情况
    return '未知', '未知'


# 为问卷数据添加标准化地域信息
survey_df[['标准省份', '标准城市']] = pd.DataFrame(
    survey_df['来自IP'].apply(extract_standard_region).tolist(),
    index=survey_df.index
)

# -------------------------- 标准化地域统计 --------------------------
# 1. 省份级别统计（按全国标准分类）
province_stats = survey_df['标准省份'].value_counts().reset_index()
province_stats.columns = ['省份', '样本数']

# 确保所有标准省份都在统计结果中（即使样本数为0）
all_provinces = list(STANDARD_PROVINCES.keys()) + ['未知', '其他']
province_full_stats = pd.DataFrame({'省份': all_provinces})
province_full_stats = province_full_stats.merge(
    province_stats, on='省份', how='left'
).fillna({'样本数': 0})
province_full_stats['样本数'] = province_full_stats['样本数'].astype(int)

# 计算占比
total_samples = province_full_stats['样本数'].sum()
province_full_stats['占比(%)'] = (province_full_stats['样本数'] / total_samples * 100).round(1)

# 按样本数排序（降序），并添加总计行
province_full_stats = province_full_stats.sort_values('样本数', ascending=False).reset_index(drop=True)
province_total = pd.DataFrame({
    '省份': ['总计'],
    '样本数': [total_samples],
    '占比(%)': [100.0]
})
province_final_stats = pd.concat([province_full_stats, province_total], ignore_index=True)

# 2. 城市级别统计（只显示样本数≥2的城市，去除"其他"行）
city_stats = survey_df['标准城市'].value_counts().reset_index()
city_stats.columns = ['城市', '样本数']

# 筛选有效城市（排除"未知"，且样本数≥2）
valid_cities = city_stats[
    (city_stats['城市'] != '未知') &
    (city_stats['样本数'] >= 2)
    ].copy()


# 计算城市占比（基于有效城市样本数）
valid_cities['占比(%)'] = (valid_cities['样本数'] / valid_cities['样本数'].sum() * 100).round(1)
city_final_stats = valid_cities.sort_values('样本数', ascending=False).reset_index(drop=True)

# -------------------------- 可视化图表生成 --------------------------
fig = plt.figure(figsize=(18, 14))
gs = plt.GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

# 1. 子图1：各价格段销售销量 vs 消费者需求占比（双轴柱状图）
ax1 = fig.add_subplot(gs[0, 0])

# 准备x轴位置
x = np.arange(len(price_ranges))
width = 0.35

# 左y轴：产品销量（柱状图）
bars1 = ax1.bar(x - width / 2, product_sales_by_price['付款人数'],
                width, label='产品总销量（人）', color='#2E86AB', alpha=0.8, edgecolor='#1A5276')
ax1.set_xlabel('价格区间', fontsize=12, fontweight='bold')
ax1.set_ylabel('产品总销量（人）', fontsize=11, color='#2E86AB', fontweight='bold')
ax1.tick_params(axis='y', labelcolor='#2E86AB')
ax1.set_title('各价格段产品销量 vs 消费者需求占比', fontsize=13, fontweight='bold', pad=20)

# 右y轴：消费者需求占比（柱状图）
ax1_twin = ax1.twinx()
bars2 = ax1_twin.bar(x + width / 2, survey_price_pct,
                     width, label='消费者需求占比（%）', color='#A23B72', alpha=0.8, edgecolor='#712250')
ax1_twin.set_ylabel('消费者需求占比（%）', fontsize=11, color='#A23B72', fontweight='bold')
ax1_twin.tick_params(axis='y', labelcolor='#A23B72')

# 设置x轴标签
ax1.set_xticks(x)
ax1.set_xticklabels(price_ranges, rotation=45, ha='right')

# 添加数值标签
# 销量标签
for bar in bars1:
    height = bar.get_height()
    if height > 0:
        ax1.text(bar.get_x() + bar.get_width() / 2., height + 1,
                 f'{int(height)}', ha='center', va='bottom', fontsize=9, color='#1A5276')
# 需求占比标签
for bar in bars2:
    height = bar.get_height()
    if height > 0:
        ax1_twin.text(bar.get_x() + bar.get_width() / 2., height + 0.5,
                      f'{height}%', ha='center', va='bottom', fontsize=9, color='#712250')


lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1_twin.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', frameon=True, fancybox=True, shadow=True)

# 添加网格
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# 2. 子图2：标准化省份分布饼图（显示前8个省份+其他）
ax2 = fig.add_subplot(gs[0, 1])

# 准备饼图数据
province_pie_data = province_final_stats[province_final_stats['省份'].isin(['总计', '未知']) == False]
top_provinces = province_pie_data.nlargest(8, '样本数')
other_province_count = province_pie_data[~province_pie_data['省份'].isin(top_provinces['省份'])]['样本数'].sum()

pie_labels = list(top_provinces['省份'])
pie_values = list(top_provinces['样本数'])
if other_province_count > 0:
    pie_labels.append('其他省份')
    pie_values.append(other_province_count)

# 美化饼图
colors = plt.cm.Set3(np.linspace(0, 1, len(pie_labels)))
explode = [0.05 if i == 0 else 0 for i in range(len(pie_labels))]  # 突出样本数最多的省份

wedges, texts, autotexts = ax2.pie(pie_values, labels=pie_labels, colors=colors,autopct='%1.1f%%', startangle=90, explode=explode,textprops={'fontsize': 9}, pctdistance=0.85)

# 美化饼图文字
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(8)

# 添加标题
ax2.set_title('消费者地域分布（全国标准省份）', fontsize=13, fontweight='bold', pad=20)

# 添加样本数信息文本框
textstr = f'总样本数：{total_samples}人\n有效省份数：{len(province_pie_data)}个\n未知地区：{province_final_stats[province_final_stats["省份"] == "未知"]["样本数"].iloc[0]}人'
props = dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.8)
ax2.text(1.3, 0.5, textstr, transform=ax2.transAxes, fontsize=9,
         verticalalignment='center', bbox=props, fontweight='bold')

# 3. 子图3：标准化省份统计表格（显示前15个省份+总计）
ax3 = fig.add_subplot(gs[1, 0])
ax3.axis('tight')
ax3.axis('off')

# 准备表格数据（前15个省份+总计）
table_province_data = province_final_stats.head(16).values.tolist()
# 表格列名
table_columns = ['省份', '样本数', '占比(%)']

# 创建表格
table1 = ax3.table(cellText=table_province_data, colLabels=table_columns,
                   cellLoc='center', loc='center', bbox=[0, 0, 1, 1])

# 设置表头样式
for i in range(len(table_columns)):
    table1[(0, i)].set_facecolor('#2E86AB')
    table1[(0, i)].set_text_props(weight='bold', color='white', fontsize=11)
    table1[(0, i)].set_height(0.12)

# 2. 遍历数据行，仅对"总计"行设置紫色背景
for row_idx in range(1, len(table_province_data) + 1):  # 表头占第0行，数据从第1行开始
    # 获取当前行的省份名称
    province_name = table_province_data[row_idx - 1][0]

    for col_idx in range(len(table_columns)):
        # 设置行高
        table1[(row_idx, col_idx)].set_height(0.07)

        # 判断是否为总计行
        if province_name == '总计':
            # 总计行：紫色背景+白色粗体
            table1[(row_idx, col_idx)].set_facecolor('#A23B72')
            table1[(row_idx, col_idx)].set_text_props(weight='bold', color='white', fontsize=11)
        else:
            # 普通省份行：浅灰色背景+黑色字体
            table1[(row_idx, col_idx)].set_facecolor('#F8F9FA')
            table1[(row_idx, col_idx)].set_text_props(fontsize=10, color='black')

# 设置列宽
table1.auto_set_column_width(col=list(range(len(table_columns))))
table1.scale(1, 1.8)

# 添加表格标题
ax3.text(0.5, 1.1, '消费者地域分组统计（全国标准省份，前15）', transform=ax3.transAxes,
         ha='center', va='top', fontsize=13, fontweight='bold')

# 4. 子图4：标准化城市统计表格（显示前15个城市）
ax4 = fig.add_subplot(gs[1, 1])
ax4.axis('tight')
ax4.axis('off')

# 准备表格数据（前15个城市，无"其他"行）
table_city_data = city_final_stats.head(15).values.tolist()
# 表格列名
table_city_columns = ['城市', '样本数', '占比(%)']

# 创建表格
table2 = ax4.table(cellText=table_city_data, colLabels=table_city_columns,
                   cellLoc='center', loc='center', bbox=[0, 0, 1, 1])

# 美化城市表格样式（统一浅灰色背景）
# 1. 设置表头样式
for i in range(len(table_city_columns)):
    table2[(0, i)].set_facecolor('#4ECDC4')
    table2[(0, i)].set_text_props(weight='bold', color='white', fontsize=11)
    table2[(0, i)].set_height(0.12)

# 2. 遍历数据行设置样式（统一浅灰色背景）
for row_idx in range(1, len(table_city_data) + 1):
    for col_idx in range(len(table_city_columns)):
        # 设置行高
        table2[(row_idx, col_idx)].set_height(0.07)
        # 普通城市行：浅灰色背景+黑色字体
        table2[(row_idx, col_idx)].set_facecolor('#F8F9FA')
        table2[(row_idx, col_idx)].set_text_props(fontsize=10, color='black')

# 设置列宽
table2.auto_set_column_width(col=list(range(len(table_city_columns))))
table2.scale(1, 1.8)

# 添加表格标题
ax4.text(0.5, 1.1, '消费者地域分组统计（标准城市，样本数≥2，前15）', transform=ax4.transAxes,
         ha='center', va='top', fontsize=13, fontweight='bold')

# -------------------------- 保存图表与数据 --------------------------
# 调整布局并保存图表（Windows路径）
plt.tight_layout()
plt.savefig(r'F:\Data Analysis\StandardPriceRegionAnalysis.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

# 保存地域统计表格为Excel文件
with pd.ExcelWriter(r'F:\Data Analysis\StandardRegionStatistics.xlsx', engine='openpyxl') as writer:
    province_final_stats.to_excel(writer, sheet_name='标准省份统计', index=False)
    city_final_stats.to_excel(writer, sheet_name='标准城市统计', index=False)
    product_sales_by_price.reset_index().to_excel(writer, sheet_name='价格段销量统计', index=False)

# 打印结果摘要
print(" 可视化图表已生成：F:\\Data Analysis\\StandardPriceRegionAnalysis.png")
print(" 地域统计数据已保存：F:\\Data Analysis\\StandardRegionStatistics.xlsx")
print(f"\n 核心统计结果预览：")
print(f"1. 总调研样本数：{total_samples}人")
print(f"2. 覆盖省份数：{len(province_pie_data)}个（全国34个省级行政区）")
print(
    f"3. 样本数最多省份：{province_final_stats.iloc[0]['省份']}（{province_final_stats.iloc[0]['样本数']}人，{province_final_stats.iloc[0]['占比(%)']}%）")
print(
    f"4. 样本数最多城市：{city_final_stats.iloc[0]['城市']}（{city_final_stats.iloc[0]['样本数']}人，{city_final_stats.iloc[0]['占比(%)']}%）")
print(
    f"5. 未知地区样本数：{province_final_stats[province_final_stats['省份'] == '未知']['样本数'].iloc[0]}人（{province_final_stats[province_final_stats['省份'] == '未知']['占比(%)'].iloc[0]}%）")