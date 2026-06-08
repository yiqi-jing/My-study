# -*- coding: utf-8 -*-
"""
中国经济发展数据分析与可视化报告
作者：惠军凯
学号：23490329
数据来源：国家统计局年度数据

主程序入口
"""

import os
import warnings
from config import OUTPUT_DIR, AUTHOR, STUDENT_ID
from data_loader import load_all_data, create_dataframe, clean_data, save_data
from statistical_analysis import descriptive_statistics, distribution_analysis, comparison_analysis, trend_analysis
from ml_analysis import run_all_ml_analysis
from visualization import generate_all_plots

warnings.filterwarnings('ignore')


def print_header():
    """打印程序头部信息"""
    print("=" * 70)
    print("中国经济发展数据分析与可视化")
    print(f"作者: {AUTHOR}  学号: {STUDENT_ID}")
    print("=" * 70)


def print_data_intro():
    """打印数据集介绍"""
    print("\n" + "=" * 70)
    print("一、数据集介绍")
    print("=" * 70)
    
    print("""
【数据来源】国家统计局年度数据
【数据背景】该数据集包含中国2016-2025年的主要经济指标，涵盖GDP、人口、产业结构、
            居民收入与消费、能源消费、金融等多个维度的年度统计数据。
【数据规模】15个CSV文件，包含1400+个经济指标，时间跨度为2016-2025年（10年）
【主要字段】
    - 国内生产总值（GDP）及相关指标
    - 人口统计指标（总人口、城镇/乡村人口、出生率、死亡率等）
    - 三次产业增加值及构成
    - 居民人均可支配收入与消费支出
    - 能源生产与消费数据
    - 进出口贸易数据
    - 金融交易数据
    - 法人单位数据
""")


def print_conclusions():
    """打印结论与建议"""
    print("\n" + "=" * 70)
    print("六、结论与建议")
    print("=" * 70)
    
    print("""
【主要发现】

1. 经济增长态势
   - 2016-2025年，中国GDP保持稳健增长态势，年均复合增长率约6-7%
   - 人均GDP实现历史性跨越，从5万元左右增长至10万元左右
   - 2020年受疫情影响增速放缓，但经济展现出强大韧性，快速恢复增长

2. 产业结构优化升级
   - 第三产业占比持续上升，从53%左右提升至58%左右，服务业成为经济主体
   - 第二产业占比相对稳定，维持在35%-39%之间，制造业转型升级持续推进
   - 第一产业占比逐年下降，从8%左右降至7%以下，农业现代化水平提升
   - 产业结构向高端化、服务化、智能化方向转型

3. 城镇化进程稳步推进
   - 城镇化率从58%左右提升至68%左右，年均提高约1个百分点
   - 城镇人口持续增加，乡村人口有序减少
   - 城镇化与经济发展呈现高度正相关（相关系数>0.99）
   - 新型城镇化建设取得显著成效

4. 居民生活水平显著提升
   - 人均可支配收入持续增长，年均增速约6-7%
   - 人均消费支出同步增长，居民消费能力不断增强
   - 恩格尔系数持续下降，从30%以上降至29%左右，进入富裕阶段
   - 收入消费比维持在67%-70%，居民储蓄意愿较强

5. 人口结构深刻变化
   - 人口出生率显著下降，从13‰以上降至6‰以下
   - 人口自然增长率由正转负，人口负增长时代到来
   - 人口老龄化趋势加剧，需要积极应对
   - 人口红利向人才红利转变

6. 对外贸易持续发展
   - 进出口总额持续增长，贸易大国地位巩固
   - 贸易顺差保持稳定，出口竞争力较强
   - 贸易结构不断优化，高附加值产品占比提升

【政策建议】

1. 经济发展方面
   - 继续深化供给侧结构性改革，推动经济高质量发展
   - 加大科技创新投入，培育新质生产力，增强发展新动能
   - 优化营商环境，激发市场主体活力，促进民营经济发展
   - 推动区域协调发展，缩小地区差距

2. 产业结构方面
   - 加快发展现代服务业，提升服务业质量和效益
   - 推动制造业数字化、智能化转型，发展先进制造业
   - 推进农业现代化，提高农业生产效率和竞争力
   - 培育战略性新兴产业，抢占未来发展制高点

3. 城镇化建设方面
   - 推进以人为核心的新型城镇化，提高城镇化质量
   - 完善城市基础设施和公共服务，提升城市承载能力
   - 促进城乡融合发展，缩小城乡差距，实现共同富裕
   - 发展城市群和都市圈，优化城镇化空间布局

4. 民生保障方面
   - 完善收入分配制度，扩大中等收入群体，缩小收入差距
   - 健全社会保障体系，提高保障水平和覆盖面
   - 加大教育、医疗、养老等公共服务投入，提升服务质量
   - 实施就业优先战略，促进高质量充分就业

5. 人口政策方面
   - 完善生育支持政策体系，降低生育、养育、教育成本
   - 积极应对人口老龄化，发展银发经济，完善养老服务体系
   - 优化人力资源配置，提高劳动生产率，挖掘人才红利
   - 建设全龄友好型社会，促进人口长期均衡发展

6. 对外开放方面
   - 推进高水平对外开放，建设开放型经济新体制
   - 优化贸易结构，提升出口产品附加值和竞争力
   - 积极参与全球经济治理，推动构建人类命运共同体
   - 统筹发展和安全，增强产业链供应链韧性
""")


def print_completion():
    """打印完成信息"""
    print("\n" + "=" * 70)
    print("分析完成！")
    print("=" * 70)
    print(f"\n输出文件位置: {OUTPUT_DIR}")
    print("\n生成的文件:")
    print("  - 综合数据表.csv")
    print("  - 图1_GDP增长趋势.png")
    print("  - 图2_产业结构变化.png")
    print("  - 图3_2025年产业结构.png")
    print("  - 图4_城镇化率变化.png")
    print("  - 图5_收入消费对比.png")
    print("  - 图6_GDP与收入关系.png")
    print("  - 图7_人口出生率死亡率.png")
    print("  - 图8_进出口贸易趋势.png")
    print("  - 图9_相关性热力图.png")
    print("  - 图10_恩格尔系数变化.png")


def main():
    """主函数"""
    # 1. 打印头部信息
    print_header()
    
    # 2. 数据集介绍
    print_data_intro()
    
    # 3. 数据读取与预处理
    print("\n" + "=" * 70)
    print("二、数据预处理")
    print("=" * 70)
    
    all_data = load_all_data()
    df = create_dataframe(all_data)
    df = clean_data(df)
    
    print("\n【综合数据表】")
    print(df.round(2).to_string(index=False))
    
    save_data(df, OUTPUT_DIR)
    
    # 4. 描述性统计分析
    print("\n" + "=" * 70)
    print("三、描述性统计分析")
    print("=" * 70)
    
    descriptive_statistics(df)
    
    # 5. 探索性分析
    print("\n" + "=" * 70)
    print("四、探索性分析（EDA）")
    print("=" * 70)
    
    distribution_analysis(df)
    comparison_analysis(df)
    trend_analysis(df)
    
    # 6. 机器学习分析
    print("\n" + "=" * 70)
    print("五、机器学习分析")
    print("=" * 70)
    
    corr_matrix = run_all_ml_analysis(df)
    
    # 7. 可视化分析
    print("\n" + "=" * 70)
    print("五、可视化分析")
    print("=" * 70)
    
    generate_all_plots(df, corr_matrix)
    
    # 8. 结论与建议
    print_conclusions()
    
    # 9. 打印完成信息
    print_completion()


if __name__ == '__main__':
    main()
