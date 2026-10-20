"""
可视化模块
生成各类图表
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import font_manager
import os
from config_1 import OUTPUT_DIR, COLORS

# 设置中文字体
def setup_chinese_font():
    """设置中文字体"""
    font_paths = [
        r'C:\Windows\Fonts\simhei.ttf',
        r'C:\Windows\Fonts\msyh.ttc',
        r'C:\Windows\Fonts\simsun.ttc',
    ]
    
    font_prop = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            font_prop = font_manager.FontProperties(fname=font_path)
            print(f"使用字体: {font_path}")
            break
    
    if font_prop is None:
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']
        plt.rcParams['axes.unicode_minus'] = False
        print("使用系统默认中文字体")
    else:
        plt.rcParams['font.family'] = font_prop.get_name()
        plt.rcParams['axes.unicode_minus'] = False
    
    return font_prop


def set_font(ax, font_prop):
    """设置图表字体"""
    if font_prop:
        for text in ax.get_xticklabels() + ax.get_yticklabels():
            text.set_fontproperties(font_prop)
        ax.xaxis.label.set_fontproperties(font_prop)
        ax.yaxis.label.set_fontproperties(font_prop)
        ax.title.set_fontproperties(font_prop)
        if ax.get_legend():
            for legend_text in ax.get_legend().get_texts():
                legend_text.set_fontproperties(font_prop)


def plot_gdp_trend(df, output_dir, font_prop):
    """图1: GDP增长趋势折线图"""
    fig, ax = plt.subplots(figsize=(12, 6))
    gdp_plot = df['GDP(亿元)'] / 10000
    ax.plot(df['年份'], gdp_plot, marker='o', linewidth=2.5, markersize=8, 
            color=COLORS['primary'], label='GDP')
    ax.set_xlabel('年份', fontsize=12, fontproperties=font_prop)
    ax.set_ylabel('GDP（万亿元）', fontsize=12, fontproperties=font_prop)
    ax.set_title('2016-2025年中国GDP增长趋势', fontsize=14, fontweight='bold', fontproperties=font_prop)
    ax.grid(True, alpha=0.3)
    for i, (x, y) in enumerate(zip(df['年份'], gdp_plot)):
        if pd.notna(y):
            ax.annotate(f'{y:.1f}', (x, y), textcoords="offset points", xytext=(0,10), 
                       ha='center', fontsize=9, fontproperties=font_prop)
    set_font(ax, font_prop)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '图1_GDP增长趋势.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  图1: GDP增长趋势折线图 - 已保存")


def plot_industry_structure(df, output_dir, font_prop):
    """图2: 产业结构变化柱状图"""
    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(df['年份']))
    width = 0.25
    ax.bar(x - width, df['第一产业(亿元)']/10000, width, label='第一产业', color=COLORS['tertiary'])
    ax.bar(x, df['第二产业(亿元)']/10000, width, label='第二产业', color=COLORS['secondary'])
    ax.bar(x + width, df['第三产业(亿元)']/10000, width, label='第三产业', color=COLORS['primary'])
    ax.set_xlabel('年份', fontsize=12, fontproperties=font_prop)
    ax.set_ylabel('增加值（万亿元）', fontsize=12, fontproperties=font_prop)
    ax.set_title('2016-2025年三次产业结构变化', fontsize=14, fontweight='bold', fontproperties=font_prop)
    ax.set_xticks(x)
    ax.set_xticklabels([str(int(y)) for y in df['年份']])
    ax.legend(prop=font_prop)
    ax.grid(True, alpha=0.3, axis='y')
    set_font(ax, font_prop)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '图2_产业结构变化.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  图2: 产业结构变化柱状图 - 已保存")


def plot_industry_pie(df, output_dir, font_prop):
    """图3: 2025年产业结构饼图"""
    fig, ax = plt.subplots(figsize=(10, 8))
    data_2025 = df[df['年份'] == 2025]
    if len(data_2025) > 0:
        data_2025 = data_2025.iloc[0]
        sizes = [data_2025['第一产业(亿元)'], data_2025['第二产业(亿元)'], data_2025['第三产业(亿元)']]
        labels = ['第一产业', '第二产业', '第三产业']
        colors = [COLORS['tertiary'], COLORS['secondary'], COLORS['primary']]
        explode = (0, 0, 0.05)
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors, 
                                           autopct='%1.1f%%', shadow=True, startangle=90)
        for text in texts:
            text.set_fontproperties(font_prop)
        for autotext in autotexts:
            autotext.set_fontproperties(font_prop)
        ax.set_title('2025年三次产业构成', fontsize=14, fontweight='bold', fontproperties=font_prop)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '图3_2025年产业结构.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  图3: 2025年产业结构饼图 - 已保存")


def plot_urbanization(df, output_dir, font_prop):
    """图4: 城镇化率变化趋势折线图"""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df['年份'], df['城镇化率(%)'], marker='s', linewidth=2.5, markersize=8, color=COLORS['danger'])
    ax.set_xlabel('年份', fontsize=12, fontproperties=font_prop)
    ax.set_ylabel('城镇化率（%）', fontsize=12, fontproperties=font_prop)
    ax.set_title('2016-2025年中国城镇化率变化趋势', fontsize=14, fontweight='bold', fontproperties=font_prop)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(55, 70)
    for i, (x, y) in enumerate(zip(df['年份'], df['城镇化率(%)'])):
        if pd.notna(y):
            ax.annotate(f'{y:.1f}%', (x, y), textcoords="offset points", xytext=(0,10), 
                       ha='center', fontsize=9, fontproperties=font_prop)
    set_font(ax, font_prop)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '图4_城镇化率变化.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  图4: 城镇化率变化趋势折线图 - 已保存")


def plot_income_consumption(df, output_dir, font_prop):
    """图5: 居民收入与消费对比柱状图"""
    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(df['年份']))
    width = 0.35
    ax.bar(x - width/2, df['人均可支配收入(元)'], width, label='人均可支配收入', color=COLORS['primary'])
    ax.bar(x + width/2, df['人均消费支出(元)'], width, label='人均消费支出', color=COLORS['secondary'])
    ax.set_xlabel('年份', fontsize=12, fontproperties=font_prop)
    ax.set_ylabel('金额（元）', fontsize=12, fontproperties=font_prop)
    ax.set_title('2016-2025年居民收入与消费对比', fontsize=14, fontweight='bold', fontproperties=font_prop)
    ax.set_xticks(x)
    ax.set_xticklabels([str(int(y)) for y in df['年份']])
    ax.legend(prop=font_prop)
    ax.grid(True, alpha=0.3, axis='y')
    set_font(ax, font_prop)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '图5_收入消费对比.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  图5: 居民收入与消费对比柱状图 - 已保存")


def plot_gdp_income_scatter(df, output_dir, font_prop):
    """图6: GDP与人均可支配收入散点图"""
    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(df['GDP(亿元)']/10000, df['人均可支配收入(元)'], 
                         c=df['年份'], cmap='viridis', s=100, alpha=0.8, edgecolors='black')
    ax.set_xlabel('GDP（万亿元）', fontsize=12, fontproperties=font_prop)
    ax.set_ylabel('人均可支配收入（元）', fontsize=12, fontproperties=font_prop)
    ax.set_title('GDP与人均可支配收入关系', fontsize=14, fontweight='bold', fontproperties=font_prop)
    ax.grid(True, alpha=0.3)
    for i, row in df.iterrows():
        ax.annotate(f"{int(row['年份'])}", 
                    (row['GDP(亿元)']/10000, row['人均可支配收入(元)']),
                    textcoords="offset points", xytext=(5,5), fontsize=9, fontproperties=font_prop)
    # 添加回归线
    if len(df.dropna(subset=['GDP(亿元)', '人均可支配收入(元)'])) > 2:
        z = np.polyfit(df['GDP(亿元)'].dropna()/10000, df['人均可支配收入(元)'].dropna(), 1)
        p = np.poly1d(z)
        x_line = np.linspace(df['GDP(亿元)'].min()/10000, df['GDP(亿元)'].max()/10000, 100)
        ax.plot(x_line, p(x_line), "r--", alpha=0.7, linewidth=2, label='回归线')
        ax.legend(prop=font_prop)
    plt.colorbar(scatter, label='年份')
    set_font(ax, font_prop)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '图6_GDP与收入关系.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  图6: GDP与人均可支配收入散点图 - 已保存")


def plot_birth_death_rate(df, output_dir, font_prop):
    """图7: 人口出生率与死亡率对比"""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df['年份'], df['出生率(‰)'], marker='o', linewidth=2.5, markersize=8, 
            color=COLORS['primary'], label='出生率')
    ax.plot(df['年份'], df['死亡率(‰)'], marker='s', linewidth=2.5, markersize=8, 
            color=COLORS['danger'], label='死亡率')
    ax.set_xlabel('年份', fontsize=12, fontproperties=font_prop)
    ax.set_ylabel('比率（‰）', fontsize=12, fontproperties=font_prop)
    ax.set_title('2016-2025年人口出生率与死亡率变化', fontsize=14, fontweight='bold', fontproperties=font_prop)
    ax.legend(prop=font_prop)
    ax.grid(True, alpha=0.3)
    set_font(ax, font_prop)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '图7_人口出生率死亡率.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  图7: 人口出生率与死亡率对比折线图 - 已保存")


def plot_trade_trend(df, output_dir, font_prop):
    """图8: 进出口贸易趋势"""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df['年份'], df['出口总额(亿元)']/10000, marker='o', linewidth=2.5, markersize=8, 
            color=COLORS['primary'], label='出口')
    ax.plot(df['年份'], df['进口总额(亿元)']/10000, marker='s', linewidth=2.5, markersize=8, 
            color=COLORS['secondary'], label='进口')
    ax.plot(df['年份'], df['贸易顺差(亿元)']/10000, marker='^', linewidth=2.5, markersize=8, 
            color=COLORS['danger'], label='贸易顺差')
    ax.set_xlabel('年份', fontsize=12, fontproperties=font_prop)
    ax.set_ylabel('金额（万亿元）', fontsize=12, fontproperties=font_prop)
    ax.set_title('2016-2025年进出口贸易趋势', fontsize=14, fontweight='bold', fontproperties=font_prop)
    ax.legend(prop=font_prop)
    ax.grid(True, alpha=0.3)
    set_font(ax, font_prop)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '图8_进出口贸易趋势.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  图8: 进出口贸易趋势折线图 - 已保存")


def plot_correlation_heatmap(corr_matrix, output_dir, font_prop):
    """图9: 相关性热力图"""
    fig, ax = plt.subplots(figsize=(10, 8))
    corr_display = corr_matrix.round(2)
    im = ax.imshow(corr_display.values, cmap='RdYlBu_r', aspect='auto', vmin=-1, vmax=1)
    ax.set_xticks(np.arange(len(corr_display.columns)))
    ax.set_yticks(np.arange(len(corr_display.index)))
    ax.set_xticklabels(corr_display.columns, rotation=45, ha='right', fontproperties=font_prop)
    ax.set_yticklabels(corr_display.index, fontproperties=font_prop)
    for i in range(len(corr_display.index)):
        for j in range(len(corr_display.columns)):
            text = ax.text(j, i, corr_display.values[i, j], ha="center", va="center", 
                          color="white" if abs(corr_display.values[i, j]) > 0.5 else "black",
                          fontsize=9)
    ax.set_title('经济指标相关性热力图', fontsize=14, fontweight='bold', fontproperties=font_prop)
    plt.colorbar(im, ax=ax)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '图9_相关性热力图.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  图9: 相关性热力图 - 已保存")


def plot_engel_coefficient(df, output_dir, font_prop):
    """图10: 恩格尔系数变化"""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df['年份'], df['恩格尔系数(%)'], marker='o', linewidth=2.5, markersize=8, color=COLORS['primary'])
    ax.set_xlabel('年份', fontsize=12, fontproperties=font_prop)
    ax.set_ylabel('恩格尔系数（%）', fontsize=12, fontproperties=font_prop)
    ax.set_title('2016-2025年恩格尔系数变化（生活水平提升）', fontsize=14, fontweight='bold', fontproperties=font_prop)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=30, color='r', linestyle='--', alpha=0.5, label='富裕标准线(30%)')
    ax.axhline(y=40, color='orange', linestyle='--', alpha=0.5, label='小康标准线(40%)')
    ax.legend(prop=font_prop)
    for i, (x, y) in enumerate(zip(df['年份'], df['恩格尔系数(%)'])):
        if pd.notna(y):
            ax.annotate(f'{y:.1f}%', (x, y), textcoords="offset points", xytext=(0,10), 
                       ha='center', fontsize=9, fontproperties=font_prop)
    set_font(ax, font_prop)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '图10_恩格尔系数变化.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  图10: 恩格尔系数变化折线图 - 已保存")


def generate_all_plots(df, corr_matrix=None):
    """生成所有图表"""
    print("\n【可视化分析】")
    
    # 设置字体
    font_prop = setup_chinese_font()
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 生成所有图表
    plot_gdp_trend(df, OUTPUT_DIR, font_prop)
    plot_industry_structure(df, OUTPUT_DIR, font_prop)
    plot_industry_pie(df, OUTPUT_DIR, font_prop)
    plot_urbanization(df, OUTPUT_DIR, font_prop)
    plot_income_consumption(df, OUTPUT_DIR, font_prop)
    plot_gdp_income_scatter(df, OUTPUT_DIR, font_prop)
    plot_birth_death_rate(df, OUTPUT_DIR, font_prop)
    plot_trade_trend(df, OUTPUT_DIR, font_prop)
    
    if corr_matrix is not None:
        plot_correlation_heatmap(corr_matrix, OUTPUT_DIR, font_prop)
    
    plot_engel_coefficient(df, OUTPUT_DIR, font_prop)
    
    print(f"\n所有图表已保存至: {OUTPUT_DIR}")
