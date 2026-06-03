"""
实验3: Matplotlib可视化绘图库
学号: 23490329
姓名: 惠军凯
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# 设置中文字体支持
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'STHeiti']
matplotlib.rcParams['axes.unicode_minus'] = False


# ============================================================
# 任务6-1: 绘制直播平台用户活跃度折线图
# ============================================================
def task1_live_stream_line_chart():
    """
    任务要求:
    (1) 读取直播热度指数的数据（使用模拟数据）
    (2) 绘制折线图，展示多日数据趋势
    """
    print("=" * 50)
    print("任务6-1: 绘制直播平台用户活跃度折线图")
    print("=" * 50)
    
    # 模拟直播热度指数数据
    # 假设有7天的数据
    dates = ['11-01', '11-02', '11-03', '11-04', '11-05', '11-06', '11-07']
    # 模拟两个直播间的活跃用户数
    viewers_room1 = np.array([12500, 13800, 15200, 14500, 16800, 17500, 18200])
    viewers_room2 = np.array([9800, 10200, 11500, 12800, 13500, 14200, 15800])
    
    # 创建画布
    fig, axes_obj = plt.subplots(figsize=(10, 6))
    
    # 绘制折线图，使用marker标记数据点
    line1, = axes_obj.plot(dates, viewers_room1, 
                            marker='s', linewidth=2, markersize=8,
                            color='#1E90FF', label='直播间1')
    line2, = axes_obj.plot(dates, viewers_room2, 
                            marker='*', linewidth=2, markersize=10,
                            color='#FF6347', label='直播间2')
    
    # 设置标题
    axes_obj.set_title('直播平台用户活跃度趋势', fontsize=16, fontweight='bold', pad=15)
    
    # 设置坐标轴标签
    axes_obj.set_xlabel('日期', fontsize=12)
    axes_obj.set_ylabel('活跃用户数', fontsize=12)
    
    # 添加网格线
    axes_obj.grid(True, linestyle='--', alpha=0.7)
    
    # 添加图例
    axes_obj.legend(loc='lower right')
    
    # 为数据点添加注释文本
    for x_temp, y1, y2 in zip(dates, viewers_room1, viewers_room2):
        axes_obj.text(x_temp, y1 + 300, str(y1), ha='center', fontsize=9)
        axes_obj.text(x_temp, y2 + 300, str(y2), ha='center', fontsize=9)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig('task1_live_stream_chart.png', dpi=150, bbox_inches='tight')
    print("图表已保存: task1_live_stream_chart.png")
    
    plt.show()
    print()


# ============================================================
# 任务6-2: 绘制旅游景点Top10的柱形图
# ============================================================
def task2_tourist_spot_bar_chart():
    """
    任务要求:
    (1) 总共有10个红色柱形，每个柱形代表旅游景点
    (2) 柱形上方显示注释文本，用于说明旅游景点的游客量
    (3) x轴的刻度标签为旅游景点名称
    (4) y轴标签位于左侧居中位置，内容是游客量(万人次)
    (5) 标题位于顶部居中位置，内容为"旅游景点Top10"
    """
    print("=" * 50)
    print("任务6-2: 绘制旅游景点Top10的柱形图")
    print("=" * 50)
    
    # 模拟旅游景点的游客量数据
    tourist_spots = [
        '故宫', '长城', '西湖', '黄山', '泰山',
        '张家界', '九寨沟', '漓江', '峨眉山', '鼓浪屿'
    ]
    visitors = [850, 720, 680, 550, 480, 420, 390, 350, 320, 280]  # 单位: 万人次
    
    # 创建画布
    fig, axes_obj = plt.subplots(figsize=(12, 7))
    
    # 绘制柱形图
    # x轴位置
    x_pos = np.arange(len(tourist_spots))
    # 柱形宽度
    bar_width = 0.6
    
    # 绘制红色柱形
    bars = axes_obj.bar(x_pos, visitors, 
                        width=bar_width, 
                        color='red',
                        edgecolor='darkred',
                        linewidth=1)
    
    # 设置x轴刻度标签
    axes_obj.set_xticks(x_pos)
    axes_obj.set_xticklabels(tourist_spots, rotation=45, ha='right')
    
    # 设置y轴标签
    axes_obj.set_ylabel('游客量(万人次)', fontsize=12)
    
    # 设置标题
    axes_obj.set_title('旅游景点Top10', fontsize=16, fontweight='bold', loc='center', pad=15)
    
    # 在柱形上方添加注释文本
    for bar, visitor_count in zip(bars, visitors):
        height = bar.get_height()
        axes_obj.text(bar.get_x() + bar.get_width() / 2, height + 15,
                     f'{visitor_count}',
                     ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # 添加网格线
    axes_obj.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig('task2_tourist_spot_bar_chart.png', dpi=150, bbox_inches='tight')
    print("图表已保存: task2_tourist_spot_bar_chart.png")
    
    plt.show()
    print()


# ============================================================
# 任务6-3: 绘制游客量占比的饼图
# ============================================================
def task3_visitors_pie_chart():
    """
    任务要求:
    (1) 每个扇区代表旅游景点，其大小对应该景点游客量占总游客量的百分比
    (2) 每个扇区中心位置显示了百分比，百分比保留两位小数
    (3) 饼图左下角显示了阴影
    (4) 图例位于右上角位置
    """
    print("=" * 50)
    print("任务6-3: 绘制游客量占比的饼图")
    print("=" * 50)
    
    # 模拟河北省旅游景点的游客量数据
    tourist_spots = [
        '秦皇岛', '承德避暑山庄', '白洋淀', '野三坡', 
        '西柏坡', '清东陵', '娲皇宫', '广府古城'
    ]
    visitors = [420, 380, 290, 220, 180, 150, 120, 100]  # 单位: 万人次
    
    # 设置饼图颜色
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
              '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
    
    # 创建画布
    fig, axes_obj = plt.subplots(figsize=(10, 8))
    
    # 绘制饼图
    wedges, texts, autotexts = axes_obj.pie(
        visitors,
        labels=None,  # 标签将通过图例显示
        autopct='%.2f%%',  # 百分比保留两位小数
        pctdistance=0.6,  # 百分比文本位置
        colors=colors,
        shadow=True,  # 添加阴影
        startangle=90,  # 起始角度
        explode=[0.05, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02]  # 突出第一块扇区
    )
    
    # 设置百分比文本样式
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
    
    # 设置图例，位于右上角
    axes_obj.legend(wedges, tourist_spots,
                    title="旅游景点",
                    loc="upper right",
                    bbox_to_anchor=(1.15, 1))
    
    # 设置标题
    axes_obj.set_title('河北省旅游景点游客量占比', fontsize=16, fontweight='bold', pad=20)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig('task3_visitors_pie_chart.png', dpi=150, bbox_inches='tight')
    print("图表已保存: task3_visitors_pie_chart.png")
    
    plt.show()
    print()


# ============================================================
# 主程序
# ============================================================
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("           Matplotlib可视化绘图库 - 实验3")
    print("=" * 60)
    print()
    
    # 执行三个任务
    task1_live_stream_line_chart()
    task2_tourist_spot_bar_chart()
    task3_visitors_pie_chart()
    
    print("=" * 60)
    print("所有任务完成！生成的图表文件:")
    print("  1. task1_live_stream_chart.png - 直播平台用户活跃度折线图")
    print("  2. task2_tourist_spot_bar_chart.png - 旅游景点Top10柱形图")
    print("  3. task3_visitors_pie_chart.png - 游客量占比饼图")
    print("=" * 60)
