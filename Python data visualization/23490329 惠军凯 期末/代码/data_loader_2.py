"""
数据加载和预处理模块 (Data Loader Module)
==========================================

本模块负责从CSV文件加载数据、提取关键指标并进行数据清洗。

主要功能:
    - 加载所有CSV文件数据
    - 提取关键经济指标
    - 数据清洗和预处理
    - 保存处理后的数据

数据处理流程:
    1. 读取所有CSV文件
    2. 提取关键经济指标
    3. 计算衍生指标
    4. 处理缺失值
    5. 保存清洗后的数据

作者: 惠军凯
学号: 23490329
版本: 2.0
更新日期: 2026-06-08
"""

import pandas as pd
import numpy as np
import os
import glob
import logging
from typing import Dict, List, Optional, Any
from config_1 import (
    DATA_DIR, OUTPUT_DIR, YEAR_COLUMNS, YEARS,
    FILE_ENCODING, INTERPOLATION_METHOD
)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_all_data() -> Dict[str, List[float]]:
    """
    加载所有CSV文件数据
    
    从指定目录读取所有CSV文件，提取统计指标数据。
    每个指标包含10年的数据（2016-2025年）。
    
    Returns:
        Dict[str, List[float]]: 指标字典，键为指标名称，值为数据列表
        
    Raises:
        FileNotFoundError: 数据目录不存在时抛出异常
        IOError: 文件读取失败时抛出异常
        
    Example:
        >>> all_data = load_all_data()
        >>> print(len(all_data))  # 输出指标数量
        1438
        
    Note:
        - 数据文件格式：前3行为标题，第4行起为数据
        - 数据顺序：2025年 -> 2016年（需要反转）
        - 缺失值处理：空值转换为np.nan
    """
    # 检查数据目录是否存在
    if not os.path.exists(DATA_DIR):
        raise FileNotFoundError(f"数据目录不存在: {DATA_DIR}")
    
    # 获取所有CSV文件
    csv_files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
    
    if not csv_files:
        raise FileNotFoundError(f"未找到CSV文件: {DATA_DIR}")
    
    print(f"\n找到 {len(csv_files)} 个CSV文件:")
    for f in csv_files:
        print(f"  - {os.path.basename(f)}")
    
    all_data: Dict[str, List[float]] = {}
    total_records = 0
    failed_files = []
    
    for csv_file in csv_files:
        try:
            # 使用上下文管理器读取文件
            with open(csv_file, 'r', encoding=FILE_ENCODING) as f:
                lines = f.readlines()
            
            # 数据行数（跳过前3行标题）
            data_lines = lines[3:]
            file_records = 0
            
            # 逐行解析数据
            for line in data_lines:
                # 数据清洗：去除制表符和空格
                parts = [p.strip().replace('\t', '') for p in line.strip().split(',')]
                
                # 验证数据格式（至少需要指标名+10年数据）
                if len(parts) >= 11:
                    indicator = parts[0].strip()
                    
                    if indicator:
                        # 提取10年的数据（2025-2016）
                        values = []
                        for i in range(1, 11):
                            val_str = parts[i] if i < len(parts) else ''
                            try:
                                # 转换数值，空值处理为np.nan
                                val = float(val_str) if val_str else np.nan
                            except (ValueError, TypeError):
                                val = np.nan
                                logger.debug(f"数值转换失败: {indicator} - {val_str}")
                            values.append(val)
                        
                        all_data[indicator] = values
                        file_records += 1
            
            total_records += file_records
            print(f"  {os.path.basename(csv_file)}: {file_records} 条记录")
            logger.info(f"成功加载文件: {os.path.basename(csv_file)}, 记录数: {file_records}")
            
        except IOError as e:
            failed_files.append(os.path.basename(csv_file))
            print(f"  {os.path.basename(csv_file)}: 读取失败 - {e}")
            logger.error(f"文件读取失败: {csv_file}, 错误: {e}")
        except Exception as e:
            failed_files.append(os.path.basename(csv_file))
            print(f"  {os.path.basename(csv_file)}: 处理失败 - {e}")
            logger.error(f"文件处理失败: {csv_file}, 错误: {e}")
    
    # 输出统计信息
    print(f"\n总共提取 {len(all_data)} 个指标")
    
    if failed_files:
        print(f"\n警告: {len(failed_files)} 个文件处理失败:")
        for f in failed_files:
            print(f"  - {f}")
        logger.warning(f"失败文件: {failed_files}")
    
    return all_data


def get_indicator_data(all_data: Dict[str, List[float]], 
                       indicator_pattern: str) -> List[float]:
    """
    根据关键词匹配提取指标数据
    
    在指标字典中查找包含指定关键词的指标，并返回其数据。
    数据顺序会从原始的2025-2016反转为2016-2025。
    
    Args:
        all_data: 所有指标的字典
        indicator_pattern: 指标关键词（如"国内生产总值 (亿元)"）
        
    Returns:
        List[float]: 指标数据列表（2016-2025年顺序），如果未找到则返回全NaN列表
        
    Example:
        >>> gdp = get_indicator_data(all_data, '国内生产总值 (亿元)')
        >>> print(len(gdp))
        10
        
    Note:
        - 使用模糊匹配（包含关系）
        - 返回第一个匹配的指标
        - 数据顺序自动反转
    """
    # 参数验证
    if not all_data:
        logger.warning("指标字典为空")
        return [np.nan] * 10
    
    if not indicator_pattern:
        logger.warning("指标关键词为空")
        return [np.nan] * 10
    
    # 查找匹配的指标
    for key in all_data.keys():
        if indicator_pattern in key:
            # 数据顺序是2025-2016，需要反转为2016-2025
            data = list(reversed(all_data[key]))
            logger.debug(f"提取指标: {key}, 数据长度: {len(data)}")
            return data
    
    # 未找到指标
    logger.warning(f"未找到指标: {indicator_pattern}")
    return [np.nan] * 10


def create_dataframe(all_data: Dict[str, List[float]]) -> pd.DataFrame:
    """
    创建综合数据框
    
    从指标字典中提取关键经济指标，创建包含所有主要指标的DataFrame。
    同时计算衍生指标（如城镇化率、产业结构占比等）。
    
    Args:
        all_data: 所有指标的字典
        
    Returns:
        pd.DataFrame: 包含所有经济指标的数据框
        
    Raises:
        ValueError: 数据提取失败时抛出异常
        
    Example:
        >>> df = create_dataframe(all_data)
        >>> print(df.shape)
        (10, 27)
        
    Note:
        数据框包含以下指标:
        - GDP相关: GDP、人均GDP、GDP增长率
        - 产业结构: 三次产业增加值及占比
        - 人口统计: 总人口、城乡人口、出生率、死亡率
        - 就业数据: 就业人员、城镇就业
        - 收入消费: 人均可支配收入、消费支出、恩格尔系数
        - 对外贸易: 进出口总额、贸易顺差
        - 能源消费: 能源消费总量、电力消费
    """
    print("\n【提取关键经济指标】")
    
    # ==================== GDP相关指标 ====================
    gdp = get_indicator_data(all_data, '国内生产总值 (亿元)')
    gdp_per_capita = get_indicator_data(all_data, '人均国内生产总值 (元)')
    gdp_growth = get_indicator_data(all_data, '国内生产总值指数 (上年=100)')
    
    # ==================== 三次产业 ====================
    primary_industry = get_indicator_data(all_data, '第一产业增加值 (亿元)')
    secondary_industry = get_indicator_data(all_data, '第二产业增加值 (亿元)')
    tertiary_industry = get_indicator_data(all_data, '第三产业增加值 (亿元)')
    
    # ==================== 人口数据 ====================
    total_pop = get_indicator_data(all_data, '年末总人口 (万人)')
    urban_pop = get_indicator_data(all_data, '城镇人口 (万人)')
    rural_pop = get_indicator_data(all_data, '乡村人口 (万人)')
    birth_rate = get_indicator_data(all_data, '人口出生率 (‰)')
    death_rate = get_indicator_data(all_data, '人口死亡率 (‰)')
    natural_growth = get_indicator_data(all_data, '人口自然增长率 (‰)')
    
    # ==================== 就业数据 ====================
    employment = get_indicator_data(all_data, '就业人员 (万人)')
    urban_employment = get_indicator_data(all_data, '城镇就业人员 (万人)')
    
    # ==================== 居民收入消费 ====================
    disposable_income = get_indicator_data(all_data, '居民人均可支配收入 (元)')
    consumption = get_indicator_data(all_data, '居民人均消费支出 (元)')
    food_expense = get_indicator_data(all_data, '居民人均食品烟酒支出 (元)')
    
    # ==================== 进出口贸易 ====================
    import_export = get_indicator_data(all_data, '进出口总额 (人民币) (亿元)')
    export_total = get_indicator_data(all_data, '出口总额 (人民币) (亿元)')
    import_total = get_indicator_data(all_data, '进口总额 (人民币) (亿元)')
    
    # ==================== 能源消费 ====================
    energy_consumption = get_indicator_data(all_data, '能源消费总量 (万吨标准煤)')
    electricity_consumption = get_indicator_data(all_data, '电力消费量 (亿千瓦小时)')
    
    # 创建综合数据框
    data = {
        '年份': YEARS,
        'GDP(亿元)': gdp,
        '人均GDP(元)': gdp_per_capita,
        'GDP增长率(%)': gdp_growth,
        '第一产业(亿元)': primary_industry,
        '第二产业(亿元)': secondary_industry,
        '第三产业(亿元)': tertiary_industry,
        '总人口(万人)': total_pop,
        '城镇人口(万人)': urban_pop,
        '乡村人口(万人)': rural_pop,
        '出生率(‰)': birth_rate,
        '死亡率(‰)': death_rate,
        '自然增长率(‰)': natural_growth,
        '就业人员(万人)': employment,
        '城镇就业(万人)': urban_employment,
        '人均可支配收入(元)': disposable_income,
        '人均消费支出(元)': consumption,
        '食品支出(元)': food_expense,
        '进出口总额(亿元)': import_export,
        '出口总额(亿元)': export_total,
        '进口总额(亿元)': import_total,
        '能源消费(万吨标煤)': energy_consumption,
        '电力消费(亿千瓦时)': electricity_consumption
    }
    
    df = pd.DataFrame(data)
    
    # ==================== 计算衍生指标 ====================
    print("\n【计算衍生指标】")
    
    # 城镇化率 = 城镇人口 / 总人口 * 100
    df['城镇化率(%)'] = _safe_divide(df['城镇人口(万人)'], df['总人口(万人)']) * 100
    
    # 三次产业占比
    df['第一产业占比(%)'] = _safe_divide(df['第一产业(亿元)'], df['GDP(亿元)']) * 100
    df['第二产业占比(%)'] = _safe_divide(df['第二产业(亿元)'], df['GDP(亿元)']) * 100
    df['第三产业占比(%)'] = _safe_divide(df['第三产业(亿元)'], df['GDP(亿元)']) * 100
    
    # 消费收入比
    df['消费收入比(%)'] = _safe_divide(df['人均消费支出(元)'], df['人均可支配收入(元)']) * 100
    
    # 恩格尔系数 = 食品支出 / 消费支出 * 100
    df['恩格尔系数(%)'] = _safe_divide(df['食品支出(元)'], df['人均消费支出(元)']) * 100
    
    # 贸易顺差 = 出口 - 进口
    df['贸易顺差(亿元)'] = df['出口总额(亿元)'] - df['进口总额(亿元)']
    
    print(f"  数据框维度: {df.shape[0]} 行 × {df.shape[1]} 列")
    logger.info(f"数据框创建完成: {df.shape}")
    
    return df


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """
    安全除法运算，处理除零和NaN情况
    
    Args:
        numerator: 分子序列
        denominator: 分母序列
        
    Returns:
        pd.Series: 除法结果序列，分母为零或NaN时返回NaN
    """
    # 使用numpy的divide函数，自动处理除零情况
    result = np.divide(numerator, denominator, out=np.full_like(numerator, np.nan), where=denominator!=0)
    return pd.Series(result, index=numerator.index)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    数据清洗
    
    对数据框进行清洗，包括缺失值处理、异常值检测等。
    
    Args:
        df: 待清洗的数据框
        
    Returns:
        pd.DataFrame: 清洗后的数据框
        
    清洗步骤:
        1. 缺失值处理：使用线性插值填充
        2. 重复值检测：检查并报告重复值
        3. 异常值检测：使用IQR方法检测异常值
        
    Example:
        >>> df_clean = clean_data(df)
        >>> print(df_clean.isna().sum().sum())  # 应该为0或很少
        0
    """
    print("\n【缺失值处理】")
    
    # 创建数据框副本，避免修改原数据
    df_clean = df.copy()
    
    # 统计缺失值
    total_nan = 0
    for col in df_clean.columns:
        if col != '年份':
            nan_count = df_clean[col].isna().sum()
            if nan_count > 0:
                total_nan += nan_count
                # 使用线性插值填充缺失值
                df_clean[col] = df_clean[col].interpolate(
                    method=INTERPOLATION_METHOD, 
                    limit_direction='both'
                )
                print(f"  {col}: 填充 {nan_count} 个缺失值")
                logger.info(f"缺失值填充: {col}, 数量: {nan_count}")
    
    # 检查重复值
    print("\n【重复值检测】")
    duplicates = df_clean.duplicated().sum()
    if duplicates > 0:
        print(f"  发现 {duplicates} 个重复行")
        logger.warning(f"发现重复行: {duplicates}")
    else:
        print("  无重复数据 ✓")
    
    # 异常值检测（使用IQR方法）
    print("\n【异常值检测】")
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    outlier_count = 0
    
    for col in numeric_cols:
        if col == '年份':
            continue
        
        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1
        
        # 定义异常值边界
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # 检测异常值
        outliers = df_clean[(df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)]
        if len(outliers) > 0:
            outlier_count += len(outliers)
            logger.info(f"异常值检测: {col}, 数量: {len(outliers)}")
    
    if outlier_count > 0:
        print(f"  检测到 {outlier_count} 个潜在异常值（已保留）")
    else:
        print("  未检测到明显异常值 ✓")
    
    print("\n【数据清洗完成】")
    print(f"  - 缺失值处理: 填充 {total_nan} 个缺失值")
    print(f"  - 重复值处理: 发现 {duplicates} 个重复行")
    print(f"  - 异常值处理: 检测到 {outlier_count} 个潜在异常值（已保留）")
    
    logger.info(f"数据清洗完成: 缺失值={total_nan}, 重复值={duplicates}, 异常值={outlier_count}")
    
    return df_clean


def save_data(df: pd.DataFrame, output_dir: str) -> str:
    """
    保存数据到CSV文件
    
    将清洗后的数据框保存为CSV文件，使用UTF-8-BOM编码以确保Excel兼容性。
    
    Args:
        df: 待保存的数据框
        output_dir: 输出目录路径
        
    Returns:
        str: 保存的文件路径
        
    Raises:
        IOError: 文件保存失败时抛出异常
        
    Example:
        >>> csv_path = save_data(df, OUTPUT_DIR)
        >>> print(csv_path)
        'f:\\...\\分析结果\\综合数据表.csv'
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 构建文件路径
    csv_path = os.path.join(output_dir, '综合数据表.csv')
    
    try:
        # 保存为CSV文件，使用UTF-8编码
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"\n综合数据表已保存至: {csv_path}")
        logger.info(f"数据保存成功: {csv_path}")
        
        # 输出文件信息
        file_size = os.path.getsize(csv_path) / 1024  # KB
        print(f"  文件大小: {file_size:.2f} KB")
        print(f"  数据维度: {df.shape[0]} 行 × {df.shape[1]} 列")
        
        return csv_path
        
    except IOError as e:
        logger.error(f"文件保存失败: {csv_path}, 错误: {e}")
        raise IOError(f"无法保存文件: {csv_path}")


def validate_data(df: pd.DataFrame) -> bool:
    """
    验证数据完整性
    
    检查数据框是否符合预期格式和完整性要求。
    
    Args:
        df: 待验证的数据框
        
    Returns:
        bool: 数据是否有效
        
    验证项:
        1. 数据框非空
        2. 年份列存在且完整
        3. 数值列无全NaN
        4. 数据行数正确
    """
    if df is None or df.empty:
        logger.error("数据框为空")
        return False
    
    # 检查年份列
    if '年份' not in df.columns:
        logger.error("缺少年份列")
        return False
    
    if df['年份'].isna().any():
        logger.error("年份列存在缺失值")
        return False
    
    # 检查数据行数
    if len(df) != len(YEARS):
        logger.error(f"数据行数不正确: 期望{len(YEARS)}, 实际{len(df)}")
        return False
    
    # 检查数值列
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isna().all():
            logger.warning(f"列 '{col}' 全为NaN")
    
    logger.info("数据验证通过")
    return True
