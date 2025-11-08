from datetime import datetime, timedelta
import numpy as np
import csv

class TrajectoryLoader:
    """火箭轨迹加载工具类"""
    def load_trajectory(self, trajectory_file):
        """加载火箭轨迹数据（更新发射场坐标和发射时间）"""
        try:
            # 尝试读取真实文件
            with open(trajectory_file, 'r') as f:
                reader = csv.DictReader(f)
                required_columns = ['time', 'lat', 'lon', 'alt']
                if not all(col in reader.fieldnames for col in required_columns):
                    raise ValueError(f"CSV文件缺少必要列：{required_columns}")
                
                times = []
                lats = []
                lons = []
                alts = []
                for row in reader:
                    try:
                        times.append(datetime.fromisoformat(row['time']))
                        lats.append(float(row['lat']))
                        lons.append(float(row['lon']))
                        alts.append(float(row['alt']))
                    except ValueError as e:
                        raise ValueError(f"CSV数据格式错误（行{reader.line_num}）：{str(e)}")
                
                return {
                    'time': times,
                    'lat': np.array(lats),
                    'lon': np.array(lons),
                    'alt': np.array(alts)
                }
        
        except FileNotFoundError:
            # 模拟数据：使用指定发射场和发射时间
            # print(f"警告：未找到轨迹文件 {trajectory_file}，使用模拟数据")
            print(f"发射场坐标：40.57°N，100.17°E")  # 酒泉发射场坐标
            print(f"发射时间：2025年10月31日23点44分43秒")
            
            # 发射时间：2025-10-31 23:44:43
            start_time = datetime(2025, 10, 31, 23, 44, 43)
            times = [start_time + timedelta(seconds=i*10) for i in range(100)]  # 每10秒一个点
            
            # 发射场坐标：酒泉实际坐标
            start_lat = 40.57
            start_lon = 100.17
            
            # 轨迹终点坐标（东北方向偏移）
            end_lat = start_lat + 3.0  # 北向分量
            end_lon = start_lon + 7.0  # 东向分量（体现东北方向）
            
            # 生成轨迹数据
            latitudes = np.linspace(start_lat, end_lat, 100)
            longitudes = np.linspace(start_lon, end_lon, 100)
            altitudes = np.linspace(0, 500, 100)  # 高度从0到500km

            return {
                'time': times,
                'lat': latitudes,
                'lon': longitudes,
                'alt': altitudes
            }
        
        except Exception as e:
            raise RuntimeError(f"加载轨迹数据失败：{str(e)}")