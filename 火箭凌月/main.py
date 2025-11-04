from rocket_optimizer import RocketLunarTransitOptimizer
from datetime import timedelta

def main():
    try:
        optimizer = RocketLunarTransitOptimizer()
        print("===== 火箭凌月拍摄点优化系统 =====")
        
        # 1. 加载火箭轨迹数据
        print("\n1. 加载火箭轨迹数据...")
        optimizer.load_rocket_trajectory()
        ignition_time = optimizer.rocket_trajectory['time'][0]
        print(f"火箭点火时间: {ignition_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 2. 计算月球位置
        print("\n2. 计算月球位置数据...")

        transit_window_start = ignition_time + timedelta(seconds=20)
        transit_window_end = transit_window_start + timedelta(seconds=5)
        moon_start = transit_window_start - timedelta(seconds=30)
        moon_end = transit_window_end + timedelta(seconds=30)
        optimizer.calculate_moon_position(moon_start, moon_end, interval=1)
        
        # 3. 计算精确凌月时刻
        print("\n3. 计算凌月时刻...")
        transit_time = optimizer.calculate_true_transit_time()
        print(f"精确凌月时刻: {transit_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 4. 生成候选拍摄点
        print("\n4. 生成候选拍摄点...")
        # 基于火箭轨迹范围生成候选点
        lat_min, lat_max = min(optimizer.rocket_trajectory['lat']), max(optimizer.rocket_trajectory['lat'])
        lon_min, lon_max = min(optimizer.rocket_trajectory['lon']), max(optimizer.rocket_trajectory['lon'])
        lat_range = (lat_min - 1, lat_max + 1)
        lon_range = (lon_min - 1, lon_max + 1)
        optimizer.generate_candidate_sites(lat_range, lon_range, num_points=300)
        
        # 5. 筛选最优拍摄点
        print("\n5. 筛选最优拍摄点...")
        top_sites = optimizer.optimize_sites(top_n=3)
        
        # 6. 输出结果（包含凌月时间）
        print("\n===== 优化结果 =====")
        print(f"观测窗口期: {transit_window_start.strftime('%H:%M:%S')} - {transit_window_end.strftime('%H:%M:%S')}")
        print(f"最佳拍摄时间点: {transit_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n最优拍摄点:")
        for i, site in enumerate(top_sites, 1):
            print(f"  第{i}名: 纬度 {site['lat']:.4f}°, 经度 {site['lon']:.4f}°")
        
        # 7. 可视化结果
        print("\n6. 生成可视化图表...")
        optimizer.visualize_results()
        
        print("\n===== 处理完成 =====")
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
    finally:
        print("\n程序结束")

if __name__ == "__main__":
    main()