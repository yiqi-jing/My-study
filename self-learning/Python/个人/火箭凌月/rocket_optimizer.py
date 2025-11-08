import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt
import ephem  # 用于天文坐标转换
from moon_calculator import MoonCalculator
from trajectory_loader import TrajectoryLoader

class RocketLunarTransitOptimizer:
    def __init__(self):
        self.rocket_trajectory = None  # 火箭轨迹（真实数据）
        self.moon_ephemeris = None     # 月球星历（真实数据）
        self.candidate_sites = []      # 候选拍摄点
        self.optimal_sites = []        # 最优拍摄点
        self.transit_time = None       # 真实凌月时刻（动态计算）

    def load_rocket_trajectory(self, trajectory_file="trajectory.csv"):
        """加载真实火箭轨迹数据"""
        loader = TrajectoryLoader()
        self.rocket_trajectory = loader.load_trajectory(trajectory_file)
        required_keys = ['time', 'lat', 'lon', 'alt']
        if not all(key in self.rocket_trajectory for key in required_keys):
            raise KeyError("轨迹数据缺少必要字段（time/lat/lon/alt）")
        return self.rocket_trajectory

    def calculate_moon_position(self, start_time, end_time, interval=1):
        """计算指定时间范围内的真实月球位置（1秒间隔确保精度）"""
        calculator = MoonCalculator()
        self.moon_ephemeris = calculator.calculate_moon_ephemeris(start_time, end_time, interval)
        required_keys = ['time', 'azimuth', 'altitude']
        if not all(key in self.moon_ephemeris for key in required_keys):
            raise KeyError("月球数据缺少必要字段（time/azimuth/altitude）")
        return self.moon_ephemeris

    def calculate_true_transit_time(self):
        """
        计算真实凌月时刻：火箭与月球在天球视角重合的时间点
        通过火箭位置（转换为天球坐标）与月球坐标的最小夹角确定
        """
        if not self.rocket_trajectory or not self.moon_ephemeris:
            raise RuntimeError("请先加载火箭轨迹和月球数据")
        
        # 转换火箭轨迹为天球坐标（方位角/高度角），以发射场为观测点
        observer = ephem.Observer()
        launch_lat = self.rocket_trajectory['lat'][0]
        launch_lon = self.rocket_trajectory['lon'][0]
        observer.lat = str(launch_lat)  # ephem需要字符串格式的度数
        observer.lon = str(launch_lon)
        
        min_angle = float('inf')
        transit_time = None
        
        for i, rocket_time in enumerate(self.rocket_trajectory['time']):
            # 火箭在天球上的坐标（从发射场观测）
            rocket_lat = self.rocket_trajectory['lat'][i]
            rocket_lon = self.rocket_trajectory['lon'][i]
            rocket_alt = self.rocket_trajectory['alt'][i] / 1000  # 转换为千米
            
            # 计算火箭方位角（简化为地表投影方位角）
            d_lon = rocket_lon - launch_lon
            d_lat = rocket_lat - launch_lat
            rocket_az = np.degrees(np.arctan2(d_lon, d_lat)) % 360
            # 计算火箭高度角（基于距离和高度的几何关系）
            distance_ground = np.hypot(
                d_lat * 111,  # 纬度每度约111km
                d_lon * 111 * np.cos(np.radians(launch_lat))  # 经度每度距离与纬度相关
            )
            rocket_alt_angle = np.degrees(np.arctan2(rocket_alt, distance_ground))
            
            # 查找同时刻的月球位置
            moon_idx = np.argmin(np.abs(np.array(self.moon_ephemeris['time']) - rocket_time))
            moon_az = self.moon_ephemeris['azimuth'][moon_idx]
            moon_alt = self.moon_ephemeris['altitude'][moon_idx]
            
            # 计算天球上的角度差（判断是否凌月）
            angle_diff = np.sqrt((rocket_az - moon_az)**2 + (rocket_alt_angle - moon_alt)** 2)
            if angle_diff < min_angle:
                min_angle = angle_diff
                transit_time = rocket_time
        
        if transit_time is None:
            raise RuntimeError("未找到有效的凌月时刻，请检查轨迹时间范围")
        
        self.transit_time = transit_time
        return transit_time

    def generate_candidate_sites(self, lat_range, lon_range, num_points=300):
        """生成候选拍摄点"""
        if len(lat_range) != 2 or len(lon_range) != 2:
            raise ValueError("经纬度范围必须是（min, max）元组")
        lats = np.random.uniform(lat_range[0], lat_range[1], num_points)
        lons = np.random.uniform(lon_range[0], lon_range[1], num_points)
        self.candidate_sites = [{'lat': lat, 'lon': lon, 'alt': 0} for lat, lon in zip(lats, lons)]
        return self.candidate_sites

    def evaluate_site(self, site):
        """基于真实凌月时刻评估拍摄点质量"""
        if not self.transit_time:
            raise RuntimeError("请先计算真实凌月时刻")
        
        score = 0.0
        # 1. 获取凌月时刻的月球位置
        moon_idx = np.argmin(np.abs(np.array(self.moon_ephemeris['time']) - self.transit_time))
        moon_alt = self.moon_ephemeris['altitude'][moon_idx]
        moon_az = self.moon_ephemeris['azimuth'][moon_idx]
        
        # 月球高度过滤（至少15°避免低空大气干扰）
        if moon_alt < 15:
            return 0.0
        score += moon_alt * 0.45  # 高度越高得分越高
        
        # 2. 火箭与月球的方位角一致性（拍摄点视角）
        rocket_idx = np.argmin(np.abs(np.array(self.rocket_trajectory['time']) - self.transit_time))
        rocket_lat = self.rocket_trajectory['lat'][rocket_idx]
        rocket_lon = self.rocket_trajectory['lon'][rocket_idx]
        
        # 计算拍摄点到火箭的方位角
        d_lon = rocket_lon - site['lon']
        d_lat = rocket_lat - site['lat']
        rocket_az = np.degrees(np.arctan2(d_lon, d_lat)) % 360
        
        # 方位角差异（最小圆周角）
        az_diff = min(np.abs(rocket_az - moon_az), 360 - np.abs(rocket_az - moon_az))
        score += max(0, 90 - az_diff) * 0.3  # 差异越小得分越高
        
        # 3. 距离惩罚（过远的点扣分）
        distance = np.hypot(
            (rocket_lat - site['lat']) * 111,
            (rocket_lon - site['lon']) * 111 * np.cos(np.radians(rocket_lat))
        )
        score -= min(distance / 10, 80)  # 每10km扣1分，最多扣80分
        
        return max(0, score)  # 确保得分非负

    def optimize_sites(self, top_n=3):
        """筛选最优拍摄点"""
        if not self.candidate_sites:
            raise ValueError("请先生成候选点")
        # 确保先计算凌月时刻
        if not self.transit_time:
            self.calculate_true_transit_time()
        scored_sites = [(site, self.evaluate_site(site)) for site in self.candidate_sites]
        scored_sites.sort(key=lambda x: x[1], reverse=True)
        self.optimal_sites = [site for site, score in scored_sites[:top_n] if score > 0]
        return self.optimal_sites

    def visualize_results(self):
        """可视化火箭轨迹、拍摄点及月球运动轨迹（增强时间标记）"""
        if not all([self.rocket_trajectory, self.moon_ephemeris, self.optimal_sites, self.transit_time]):
            raise ValueError("可视化前请完成所有计算步骤")
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 左图：地理轨迹与拍摄点
        ax1.scatter([s['lon'] for s in self.candidate_sites], 
                   [s['lat'] for s in self.candidate_sites], 
                   c='gray', alpha=0.3, label='候选点')
        ax1.scatter([s['lon'] for s in self.optimal_sites], 
                   [s['lat'] for s in self.optimal_sites], 
                   c='red', s=100, label='最优拍摄点')
        ax1.plot(self.rocket_trajectory['lon'], self.rocket_trajectory['lat'], 'b-', label='火箭轨迹')
        # 标记凌月时刻的火箭位置
        transit_idx = np.argmin(np.abs(np.array(self.rocket_trajectory['time']) - self.transit_time))
        ax1.scatter(self.rocket_trajectory['lon'][transit_idx], 
                   self.rocket_trajectory['lat'][transit_idx], 
                   c='orange', s=150, marker='*', label='凌月时刻火箭位置')
        ax1.set_xlabel('经度（度）')
        ax1.set_ylabel('纬度（度）')
        ax1.legend()
        ax1.set_title('神州二十一号火箭凌月预测点')
        
        # 右图：月球运动轨迹（天空视角）
        moon_az = self.moon_ephemeris['azimuth']
        moon_alt = self.moon_ephemeris['altitude']
        ax2.plot(moon_az, moon_alt, 'gold', linewidth=2, label='月球轨迹')
        # 标记关键时间点
        start_time = self.moon_ephemeris['time'][0].strftime("%H:%M:%S")
        ax2.scatter(moon_az[0], moon_alt[0], c='blue', s=80, label=f'起点 {start_time}')
        end_time = self.moon_ephemeris['time'][-1].strftime("%H:%M:%S")
        ax2.scatter(moon_az[-1], moon_alt[-1], c='purple', s=80, label=f'终点 {end_time}')
        # 凌月时刻月球位置
        moon_transit_idx = np.argmin(np.abs(np.array(self.moon_ephemeris['time']) - self.transit_time))
        transit_time_str = self.transit_time.strftime("%H:%M:%S")
        ax2.scatter(moon_az[moon_transit_idx], moon_alt[moon_transit_idx], 
                   c='red', s=100, marker='*', label=f'凌月时刻 {transit_time_str}')
        ax2.set_xlabel('方位角（度）')
        ax2.set_ylabel('高度角（度）')
        ax2.set_xlim(0, 360)
        ax2.set_ylim(0, 90)
        ax2.grid(True)
        ax2.legend()
        ax2.set_title('月球运动轨迹（天文数据）')
        
        plt.tight_layout()
        plt.show()