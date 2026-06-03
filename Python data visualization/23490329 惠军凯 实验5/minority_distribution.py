# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 18:00:38 2021
@author: yubg
学生数据交互可视化
"""

import pandas as pd
import altair as alt

# ==================== 第一部分：数据读取 ====================
# 读取CSV数据
data = pd.read_csv(r"F:\My-study\Python data visualization\student.csv", encoding='gbk')
print("数据预览：")
print(data)
print(f"\n数据共有 {len(data)} 条记录")

# ==================== 第二部分：省、自治区、直辖市与民族数据图 ====================
# 创建交互选择器
brush = alt.selection_interval()

# 创建散点图：显示省份与民族的关系
points = alt.Chart(data).mark_circle(size=200).encode(
    y='民族:N',
    x='省份:N',
    color=alt.condition(
        brush,
        '民族:N',
        alt.value('lightgray')
    )
).add_selection(
    brush
)

# 保存散点图
points.save('chart0.html')
print("\n散点图已保存为 chart0.html")

# 创建条形图：显示各省份的少数民族数量统计
bars = alt.Chart(data).mark_bar().encode(
    y='省份:N',
    color='民族:N',
    x='count(民族):Q'
).transform_filter(
    brush
)

# 保存条形图
bars.save('chart2.html')
print("条形图已保存为 chart2.html")

# 合并图表并保存
(points & bars).save('chart3.html')
print("合并图表已保存为 chart3.html")

# ==================== 第三部分：成绩分析 ====================
# 计算总成绩（语文+外语+数学）
data['cj'] = data['语文'] + data['外语'] + data['数学']
print("\n添加总成绩列后的数据预览：")
print(data)

# 创建交互式成绩可视化图表
brush2 = alt.selection_interval()

# 散点图：显示选定区域的民族成绩分布
points_score = alt.Chart(data).mark_circle(size=200).encode(
    x='民族:N',
    y='省份:N',
    color=alt.condition(
        brush2,
        '民族:N',
        alt.value('lightgray')
    )
).add_selection(
    brush2
)

points_score.save('t1.html')
print("\n成绩散点图已保存为 t1.html")

# 条形图：显示各民族的平均成绩
bars_score = alt.Chart(data).mark_bar().encode(
    y='民族:N',
    color='民族:N',
    x='mean(cj):Q'
).transform_filter(
    brush2
)

bars_score.save('t2.html')
print("成绩条形图已保存为 t2.html")

# 合并成绩图表
(points_score & bars_score).save('t.html')
print("合并成绩图表已保存为 t.html")

# ==================== 第四部分：数据分析 ====================
# 按民族分组计算平均成绩
df_group = data.groupby('民族')['cj'].mean()
df_group_sorted = df_group.sort_values(ascending=True)
print("\n各民族平均成绩（升序排列）：")
print(df_group_sorted)

# 显示成绩最高的民族
print(f"\n平均成绩最高的民族是：{df_group_sorted.index[-1]}，平均成绩为：{df_group_sorted.iloc[-1]:.2f}")

# 如果需要更多统计信息（标准差、人数、最大值）
df_group_stats = data.groupby('民族')['cj'].agg(['mean', 'std', 'count', 'max'])
df_group_stats_sorted = df_group_stats.sort_values(by='mean', ascending=True)
print("\n各民族成绩统计信息（按平均分升序排列）：")
print(df_group_stats_sorted)

print("\n所有图表已生成完成！")
