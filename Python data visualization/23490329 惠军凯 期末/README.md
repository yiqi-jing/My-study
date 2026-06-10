﻿﻿﻿# 中国经济发展数据分析与可视化

作者：惠军凯  
学号：23490329  
数据来源：国家统计局年度数据

## 项目结构

```
23490329 惠军凯 期末/
├── 代码/                           # 源代码目录
│   ├── config_1.py                # 配置文件（路径、常量等）
│   ├── data_loader_2.py           # 数据加载和预处理模块
│   ├── statistical_analysis_3.py  # 描述性统计分析模块
│   ├── ml_analysis_4.py           # 机器学习分析模块
│   ├── visualization_5.py         # 可视化模块
│   └── main_6.py                  # 主程序入口
├── 国家统计局的年度数据/            # 数据目录（15个CSV文件）
│   ├── 年度数据.csv
│   ├── 年度数据 (1).csv
│   ├── 年度数据 (2).csv
│   └── ...
├── 分析结果/                       # 输出目录
│   ├── 综合数据表.csv
│   ├── 图1_GDP增长趋势.png
│   ├── 图2_产业结构变化.png
│   ├── 图3_2025年产业结构.png
│   ├── 图4_城镇化率变化.png
│   ├── 图5_收入消费对比.png
│   ├── 图6_GDP与收入关系.png
│   ├── 图7_人口出生率死亡率.png
│   ├── 图8_进出口贸易趋势.png
│   ├── 图9_相关性热力图.png
│   └── 图10_恩格尔系数变化.png
├── README.md                    # 项目说明文档
├── 《数据分析与可视化》结课报告要求.docx
└── 惠军凯 23490329《数据分析与可视化》结课报告.docx
```

## 模块说明

### 1. config.py - 配置模块
- 定义所有路径和常量
- 包含年份列表、颜色配置等

### 2. data_loader.py - 数据加载模块
- `load_all_data()`: 加载所有CSV文件
- `create_dataframe()`: 创建综合数据框
- `clean_data()`: 数据清洗
- `save_data()`: 保存数据

### 3. statistical_analysis.py - 统计分析模块
- `descriptive_statistics()`: 描述性统计
- `distribution_analysis()`: 分布分析
- `comparison_analysis()`: 对比分析
- `trend_analysis()`: 趋势分析

### 4. ml_analysis.py - 机器学习模块
- `correlation_analysis()`: 相关性分析
- `linear_regression_analysis()`: 线性回归
- `multiple_regression_analysis()`: 多元回归
- `kmeans_clustering()`: K-means聚类
- `pca_analysis()`: PCA主成分分析

### 5. visualization.py - 可视化模块
- `plot_gdp_trend()`: GDP增长趋势图
- `plot_industry_structure()`: 产业结构图
- `plot_industry_pie()`: 产业构成饼图
- `plot_urbanization()`: 城镇化率图
- `plot_income_consumption()`: 收入消费对比图
- `plot_gdp_income_scatter()`: GDP与收入散点图
- `plot_birth_death_rate()`: 人口出生率死亡率图
- `plot_trade_trend()`: 进出口贸易趋势图
- `plot_correlation_heatmap()`: 相关性热力图
- `plot_engel_coefficient()`: 恩格尔系数图

### 6. main_6.py - 主程序
- 整合所有模块
- 按顺序执行分析流程
- 输出分析结果和结论

## 运行方法

```bash
# 安装依赖
pip install pandas numpy matplotlib

# 可选：安装机器学习库
pip install scikit-learn

# 运行分析
cd 代码
python main_6.py
```

## 输出结果

### 数据文件
- `综合数据表.csv`: 包含所有清洗后的经济指标数据

### 可视化图表（共10张）
1. 图1_GDP增长趋势.png - 折线图
2. 图2_产业结构变化.png - 柱状图
3. 图3_2025年产业结构.png - 饼图
4. 图4_城镇化率变化.png - 折线图
5. 图5_收入消费对比.png - 柱状图
6. 图6_GDP与收入关系.png - 散点图
7. 图7_人口出生率死亡率.png - 折线图
8. 图8_进出口贸易趋势.png - 折线图
9. 图9_相关性热力图.png - 热力图
10. 图10_恩格尔系数变化.png - 折线图

## 分析内容

### 一、数据预处理
- 整合15个CSV文件，提取1438个经济指标
- 数据清洗：缺失值填充、异常值处理
- 创建包含27个字段的综合数据表

### 二、描述性统计分析
- 主要指标的均值、中位数、标准差等统计特征
- 变异系数分析
- 极值分析

### 三、探索性分析（EDA）
- 分布分析：GDP、收入、城镇化率的分布特征
- 对比分析：三次产业结构、城乡人口、进出口贸易
- 趋势分析：GDP增长、城镇化率变化、收入增长趋势

### 四、机器学习分析
- 皮尔逊相关系数分析
- 线性回归：GDP对居民收入的影响
- 多元回归：影响消费支出的因素
- K-means聚类：经济发展阶段划分
- PCA主成分分析：经济指标降维

### 五、可视化分析
- 生成10张高质量可视化图表
- 使用中文字体，确保中文正常显示

### 六、结论与建议
- 经济增长态势分析
- 产业结构优化升级
- 城镇化进程分析
- 居民生活水平提升
- 人口结构变化
- 对外贸易发展
- 政策建议

## 技术特点

1. **模块化设计**: 代码拆分为独立模块，便于维护和扩展
2. **数据完整性**: 整合所有数据源，确保数据完整
3. **中文支持**: 完善的中文字体设置
4. **机器学习**: 可选的机器学习分析功能
5. **高质量图表**: 300dpi高清图表输出
