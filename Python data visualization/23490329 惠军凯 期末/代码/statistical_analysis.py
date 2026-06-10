"""
描述性统计分析模块
"""

import pandas as pd
import numpy as np
from config import STATS_COLUMNS


def descriptive_statistics(df):
    """描述性统计分析"""
    print("\n【主要指标描述性统计】")
    stats_df = df[STATS_COLUMNS].describe()
    print(stats_df.round(2).to_string())
    
    print("\n【各指标详细统计特征】")
    for col in STATS_COLUMNS:
        data_col = df[col].dropna()
        if len(data_col) > 0:
            print(f"\n{col}:")
            print(f"  均值: {data_col.mean():.2f}")
            print(f"  中位数: {data_col.median():.2f}")
            print(f"  最大值: {data_col.max():.2f} ({df.loc[data_col.idxmax(), '年份']}年)")
            print(f"  最小值: {data_col.min():.2f} ({df.loc[data_col.idxmin(), '年份']}年)")
            print(f"  标准差: {data_col.std():.2f}")
            print(f"  变异系数: {data_col.std() / data_col.mean() * 100:.2f}%")
    
    return stats_df


def distribution_analysis(df):
    """分布分析"""
    print("\n【4.1 分布分析】")
    
    print("\n(1) GDP分布分析")
    gdp_data = df['GDP(亿元)'].dropna()
    print(f"  GDP均值: {gdp_data.mean():.2f} 亿元")
    print(f"  GDP中位数: {gdp_data.median():.2f} 亿元")
    print(f"  GDP标准差: {gdp_data.std():.2f} 亿元")
    print(f"  变异系数: {gdp_data.std() / gdp_data.mean() * 100:.2f}%")
    print(f"  偏度: {gdp_data.skew():.4f}")
    print(f"  峰度: {gdp_data.kurtosis():.4f}")
    
    print("\n(2) 居民收入分布分析")
    income_data = df['人均可支配收入(元)'].dropna()
    print(f"  人均可支配收入均值: {income_data.mean():.2f} 元")
    print(f"  人均可支配收入中位数: {income_data.median():.2f} 元")
    print(f"  收入标准差: {income_data.std():.2f} 元")
    print(f"  收入范围: {income_data.min():.2f} - {income_data.max():.2f} 元")
    
    print("\n(3) 城镇化率分布分析")
    urban_data = df['城镇化率(%)'].dropna()
    print(f"  城镇化率均值: {urban_data.mean():.2f}%")
    print(f"  城镇化率范围: {urban_data.min():.2f}% - {urban_data.max():.2f}%")


def comparison_analysis(df):
    """对比分析"""
    print("\n【4.2 对比分析】")
    
    print("\n(1) 三次产业对比")
    for year in [2016, 2020, 2025]:
        row = df[df['年份'] == year]
        if len(row) > 0:
            row = row.iloc[0]
            print(f"\n{year}年产业结构:")
            print(f"  第一产业: {row['第一产业(亿元)']:.2f} 亿元 ({row['第一产业占比(%)']:.1f}%)")
            print(f"  第二产业: {row['第二产业(亿元)']:.2f} 亿元 ({row['第二产业占比(%)']:.1f}%)")
            print(f"  第三产业: {row['第三产业(亿元)']:.2f} 亿元 ({row['第三产业占比(%)']:.1f}%)")
    
    print("\n(2) 城乡人口对比")
    for year in [2016, 2020, 2025]:
        row = df[df['年份'] == year]
        if len(row) > 0:
            row = row.iloc[0]
            print(f"\n{year}年:")
            print(f"  城镇人口: {row['城镇人口(万人)']:.2f} 万人 ({row['城镇化率(%)']:.1f}%)")
            print(f"  乡村人口: {row['乡村人口(万人)']:.2f} 万人 ({100-row['城镇化率(%)']:.1f}%)")
    
    print("\n(3) 进出口贸易对比")
    for year in [2016, 2020, 2025]:
        row = df[df['年份'] == year]
        if len(row) > 0:
            row = row.iloc[0]
            print(f"\n{year}年:")
            print(f"  出口: {row['出口总额(亿元)']:.2f} 亿元")
            print(f"  进口: {row['进口总额(亿元)']:.2f} 亿元")
            print(f"  贸易顺差: {row['贸易顺差(亿元)']:.2f} 亿元")


def trend_analysis(df):
    """趋势分析"""
    print("\n【4.3 趋势分析】")
    
    print("\n(1) GDP增长趋势")
    for i in range(1, len(df)):
        prev_gdp = df.iloc[i-1]['GDP(亿元)']
        curr_gdp = df.iloc[i]['GDP(亿元)']
        if pd.notna(prev_gdp) and pd.notna(curr_gdp) and prev_gdp > 0:
            growth = (curr_gdp - prev_gdp) / prev_gdp * 100
            print(f"  {int(df.iloc[i-1]['年份'])}-{int(df.iloc[i]['年份'])}: 增长率 {growth:.2f}%")
    
    print("\n(2) 城镇化率变化趋势")
    for i in range(1, len(df)):
        prev_urban = df.iloc[i-1]['城镇化率(%)']
        curr_urban = df.iloc[i]['城镇化率(%)']
        if pd.notna(prev_urban) and pd.notna(curr_urban):
            change = curr_urban - prev_urban
            print(f"  {int(df.iloc[i-1]['年份'])}-{int(df.iloc[i]['年份'])}: 提高 {change:.2f} 个百分点")
    
    print("\n(3) 居民收入增长趋势")
    for i in range(1, len(df)):
        prev_income = df.iloc[i-1]['人均可支配收入(元)']
        curr_income = df.iloc[i]['人均可支配收入(元)']
        if pd.notna(prev_income) and pd.notna(curr_income) and prev_income > 0:
            growth = (curr_income - prev_income) / prev_income * 100
            print(f"  {int(df.iloc[i-1]['年份'])}-{int(df.iloc[i]['年份'])}: 增长率 {growth:.2f}%")
