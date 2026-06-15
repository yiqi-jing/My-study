﻿"""
中国经济发展数据分析与可视化 - 主程序
=====================================

主程序入口，整合所有分析模块。

作者: 惠军凯
学号: 23490329
更新日期: 2026-06-08
"""

import os
import warnings
from config_1 import OUTPUT_DIR, AUTHOR, STUDENT_ID
from data_loader_2 import load_all_data, create_dataframe, clean_data, save_data
from statistical_analysis_3 import descriptive_statistics, distribution_analysis, comparison_analysis, trend_analysis
from ml_analysis_4 import run_all_ml_analysis
from visualization_5 import generate_all_plots

# 忽略警告
warnings.filterwarnings('ignore')


def print_header():
    """
    打印程序头部信息
    
    显示程序标题、作者信息和数据来源。
    """
    print("=" * 70)
    print("中国经济发展数据分析与可视化")
    print(f"作者: {AUTHOR}  学号: {STUDENT_ID}")
    print("=" * 70)
    print("\n详细分析报告请查看: 分析报告.md")
    print("数据说明请查看: 国家统计局的年度数据/数据说明.md")


def print_completion():
    """
    打印完成信息
    
    显示输出文件位置和生成的文件列表。
    """
    print("\n" + "=" * 70)
    print("分析完成！")
    print("=" * 70)
    print(f"\n输出文件位置: {OUTPUT_DIR}")
    print("\n生成的文件:")
    print("  数据文件:")
    print("    - 综合数据表.csv")
    print("\n  可视化图表:")
    print("    - 图1_GDP增长趋势.png")
    print("    - 图2_产业结构变化.png")
    print("    - 图3_2025年产业结构.png")
    print("    - 图4_城镇化率变化.png")
    print("    - 图5_收入消费对比.png")
    print("    - 图6_GDP与收入关系.png")
    print("    - 图7_人口出生率死亡率.png")
    print("    - 图8_进出口贸易趋势.png")
    print("    - 图9_相关性热力图.png")
    print("    - 图10_恩格尔系数变化.png")
    print("\n  分析报告:")
    print("    - 分析报告.md (详细分析结果和结论)")
    print("    - README.md (项目说明文档)")


def main():
    """
    主函数
    
    执行完整的数据分析流程:
        1. 打印头部信息
        2. 数据加载与预处理
        3. 描述性统计分析
        4. 探索性分析（EDA）
        5. 机器学习分析
        6. 可视化分析
        7. 打印完成信息
    """
    # ==================== 1. 打印头部信息 ====================
    print_header()
    
    # ==================== 2. 数据加载与预处理 ====================
    print("\n" + "=" * 70)
    print("步骤 1/6: 数据加载与预处理")
    print("=" * 70)
    
    # 加载所有数据
    all_data = load_all_data()
    
    # 创建数据框
    df = create_dataframe(all_data)
    
    # 数据清洗
    df = clean_data(df)
    
    # 显示数据概览
    print("\n【综合数据表概览】")
    print(f"数据维度: {df.shape[0]} 行 × {df.shape[1]} 列")
    print(f"时间范围: {df['年份'].min()} - {df['年份'].max()}")
    print("\n前5行数据:")
    print(df.head().round(2).to_string(index=False))
    
    # 保存数据
    save_data(df, OUTPUT_DIR)
    
    # ==================== 3. 描述性统计分析 ====================
    print("\n" + "=" * 70)
    print("步骤 2/6: 描述性统计分析")
    print("=" * 70)
    
    descriptive_statistics(df)
    
    # ==================== 4. 探索性分析 ====================
    print("\n" + "=" * 70)
    print("步骤 3/6: 探索性分析（EDA）")
    print("=" * 70)
    
    print("\n【分布分析】")
    distribution_analysis(df)
    
    print("\n【对比分析】")
    comparison_analysis(df)
    
    print("\n【趋势分析】")
    trend_analysis(df)
    
    # ==================== 5. 机器学习分析 ====================
    print("\n" + "=" * 70)
    print("步骤 4/6: 机器学习分析")
    print("=" * 70)
    
    corr_matrix = run_all_ml_analysis(df)
    
    # ==================== 6. 可视化分析 ====================
    print("\n" + "=" * 70)
    print("步骤 5/6: 可视化分析")
    print("=" * 70)
    
    generate_all_plots(df, corr_matrix)
    
    # ==================== 7. 打印完成信息 ====================
    print("\n" + "=" * 70)
    print("步骤 6/6: 生成分析报告")
    print("=" * 70)
    print("详细分析报告已保存至: 分析报告.md")
    
    print_completion()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n\n程序执行出错: {e}")
        import traceback
        traceback.print_exc()
