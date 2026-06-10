"""
配置模块 (Configuration Module)
==============================

本模块定义了项目中使用的所有路径、常量和配置参数。

主要功能:
    - 定义项目基础路径和数据目录
    - 配置年份范围和列名
    - 定义图表颜色方案
    - 设置统计指标列表

使用方法:
    from config import DATA_DIR, OUTPUT_DIR, YEARS

作者: 惠军凯
学号: 23490329
版本: 2.0
更新日期: 2026-06-08
"""

import os
from typing import List, Dict

# ==================== 路径配置 ====================

# 项目基础路径
BASE_DIR: str = r'f:\My-study\Python data visualization\23490329 惠军凯 期末'

# 数据目录：存放国家统计局CSV文件
DATA_DIR: str = os.path.join(BASE_DIR, '国家统计局的年度数据')

# 输出目录：存放分析结果和图表
OUTPUT_DIR: str = os.path.join(BASE_DIR, '分析结果')

# ==================== 时间配置 ====================

# 分析年份范围（2016-2025年，共10年）
YEARS: List[int] = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

# 年份列名（用于DataFrame列名）
YEAR_COLUMNS: List[str] = [
    '2016年', '2017年', '2018年', '2019年', '2020年', 
    '2021年', '2022年', '2023年', '2024年', '2025年'
]

# ==================== 作者信息 ====================

# 项目作者
AUTHOR: str = '惠军凯'

# 学号
STUDENT_ID: str = '23490329'

# ==================== 可视化配置 ====================

# 图表颜色方案（使用十六进制颜色码）
COLORS: Dict[str, str] = {
    'primary': '#2E86AB',      # 主色调：蓝色
    'secondary': '#F18F01',    # 次色调：橙色
    'tertiary': '#A23B72',     # 第三色调：紫色
    'danger': '#C73E1D',       # 警告色：红色
    'success': '#28A745'       # 成功色：绿色
}

# 图表分辨率（DPI）
FIGURE_DPI: int = 300

# 图表尺寸
FIGURE_SIZE: tuple = (12, 6)

# ==================== 统计配置 ====================

# 主要统计指标列表（用于描述性统计分析）
STATS_COLUMNS: List[str] = [
    'GDP(亿元)', 
    '人均GDP(元)', 
    '总人口(万人)', 
    '人均可支配收入(元)', 
    '人均消费支出(元)', 
    '城镇化率(%)', 
    '能源消费(万吨标煤)'
]

# ==================== 数据处理配置 ====================

# 缺失值填充方法
INTERPOLATION_METHOD: str = 'linear'  # 线性插值

# 数据文件编码
FILE_ENCODING: str = 'utf-8'

# CSV文件分隔符
CSV_DELIMITER: str = ','

# ==================== 机器学习配置 ====================

# 随机种子（确保结果可复现）
RANDOM_STATE: int = 42

# K-means聚类数量
N_CLUSTERS: int = 3

# PCA主成分数量
N_COMPONENTS: int = 2

# ==================== 工具函数 ====================

def ensure_dir_exists(dir_path: str) -> bool:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        dir_path: 目录路径
        
    Returns:
        bool: 目录是否存在或创建成功
        
    Raises:
        OSError: 目录创建失败时抛出异常
    """
    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"创建目录: {dir_path}")
        return True
    except OSError as e:
        print(f"错误: 无法创建目录 {dir_path}: {e}")
        return False


def validate_config() -> bool:
    """
    验证配置是否有效
    
    Returns:
        bool: 配置是否有效
        
    检查项:
        1. 数据目录是否存在
        2. 年份列表是否有效
        3. 颜色配置是否完整
    """
    # 检查数据目录
    if not os.path.exists(DATA_DIR):
        print(f"警告: 数据目录不存在: {DATA_DIR}")
        return False
    
    # 检查年份列表
    if len(YEARS) != len(YEAR_COLUMNS):
        print("警告: 年份列表与列名列表长度不匹配")
        return False
    
    # 检查颜色配置
    required_colors = ['primary', 'secondary', 'tertiary', 'danger', 'success']
    for color in required_colors:
        if color not in COLORS:
            print(f"警告: 缺少颜色配置: {color}")
            return False
    
    print("配置验证通过 ✓")
    return True


# ==================== 初始化 ====================

# 模块加载时验证配置
if __name__ != '__main__':
    # 确保输出目录存在
    ensure_dir_exists(OUTPUT_DIR)
