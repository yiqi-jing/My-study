import numpy as np
import ephem
from datetime import datetime, timedelta

class MoonCalculator:
    """月球位置计算工具类"""
    
    def calculate_moon_ephemeris(self, start_time, end_time, interval=1):
        """
        计算指定时间范围内的月球位置（方位角和高度角）
        
        参数:
            start_time: 开始时间 (datetime)
            end_time: 结束时间 (datetime)
            interval: 时间间隔（秒）
        
        返回:
            包含时间、方位角和高度角的字典
        """
        if not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
            raise TypeError("开始时间和结束时间必须是datetime对象")
        
        if start_time >= end_time:
            raise ValueError("开始时间必须早于结束时间")
        
        # 创建观测者（使用轨迹起点作为观测点）
        observer = ephem.Observer()
        # 这里使用默认值，实际应用中应根据需要设置具体经纬度
        observer.lat = '0'  # 纬度（度）
        observer.lon = '0'  # 经度（度）
        observer.elevation = 0  # 海拔高度（米）
        
        moon = ephem.Moon()
        
        times = []
        azimuths = []
        altitudes = []
        
        current_time = start_time
        while current_time <= end_time:
            observer.date = current_time.strftime('%Y/%m/%d %H:%M:%S')
            moon.compute(observer)
            
            # 转换为度并存储
            times.append(current_time)
            azimuths.append(np.degrees(moon.az))  # 方位角（度）
            altitudes.append(np.degrees(moon.alt))  # 高度角（度）
            
            current_time += timedelta(seconds=interval)
        
        return {
            'time': times,
            'azimuth': np.array(azimuths),
            'altitude': np.array(altitudes)
        }