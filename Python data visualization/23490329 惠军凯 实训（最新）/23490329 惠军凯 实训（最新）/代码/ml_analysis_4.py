"""
机器学习分析模块
包含回归、聚类、PCA、趋势分析、周期分析、预测等分析方法
"""

import pandas as pd
import numpy as np

# 尝试导入sklearn（可选）
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.metrics import r2_score, mean_squared_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def correlation_analysis(df):
    """相关性分析"""
    print("\n(1) 皮尔逊相关系数分析")
    
    analysis_cols = ['GDP(亿元)', '人均GDP(元)', '总人口(万人)', '城镇化率(%)', 
                     '人均可支配收入(元)', '人均消费支出(元)', '能源消费(万吨标煤)']
    analysis_df = df[analysis_cols].dropna()
    
    corr_matrix = analysis_df.corr()
    print("\n相关系数矩阵:")
    print(corr_matrix.round(3).to_string())
    
    print("\n主要相关性发现:")
    print(f"  GDP与人均可支配收入: r = {corr_matrix.loc['GDP(亿元)', '人均可支配收入(元)']:.4f}")
    print(f"  城镇化率与人均GDP: r = {corr_matrix.loc['城镇化率(%)', '人均GDP(元)']:.4f}")
    print(f"  收入与消费: r = {corr_matrix.loc['人均可支配收入(元)', '人均消费支出(元)']:.4f}")
    
    return corr_matrix


def linear_regression_analysis(df):
    """线性回归分析"""
    print("\n(2) 线性回归分析 - GDP对居民收入的影响")
    
    if not SKLEARN_AVAILABLE:
        print("  (需要安装scikit-learn)")
        return None
    
    X = df[['GDP(亿元)']].dropna()
    y = df.loc[X.index, '人均可支配收入(元)']
    
    if len(X) > 2:
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        
        print(f"  回归方程: 人均可支配收入 = {model.coef_[0]:.4f} × GDP + {model.intercept_:.2f}")
        print(f"  R² 得分: {r2:.4f}")
        print(f"  模型解释: GDP每增加1万亿元，人均可支配收入增加约 {model.coef_[0]*10000:.2f} 元")
        
        return model
    return None


def multiple_regression_analysis(df):
    """多元回归分析"""
    print("\n(3) 多元回归分析 - 影响人均消费支出的因素")
    
    if not SKLEARN_AVAILABLE:
        print("  (需要安装scikit-learn)")
        return None
    
    features = ['人均可支配收入(元)', '城镇化率(%)', 'GDP增长率(%)']
    X_multi = df[features].dropna()
    y_multi = df.loc[X_multi.index, '人均消费支出(元)']
    
    if len(X_multi) > 3:
        model_multi = LinearRegression()
        model_multi.fit(X_multi, y_multi)
        y_pred_multi = model_multi.predict(X_multi)
        r2_multi = r2_score(y_multi, y_pred_multi)
        
        print(f"  特征重要性:")
        for i, feature in enumerate(features):
            print(f"    {feature}: {model_multi.coef_[i]:.4f}")
        print(f"  R² 得分: {r2_multi:.4f}")
        
        return model_multi
    return None


def kmeans_clustering(df):
    """K-means聚类分析"""
    print("\n(4) K-means聚类分析 - 年份经济发展阶段划分")
    
    if not SKLEARN_AVAILABLE:
        print("  (需要安装scikit-learn)")
        return None
    
    cluster_features = ['GDP(亿元)', '人均GDP(元)', '城镇化率(%)', '人均可支配收入(元)']
    X_cluster = df[cluster_features].dropna()
    
    if len(X_cluster) >= 3:
        # 标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_cluster)
        
        # K-means聚类
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        print("  聚类结果:")
        for i in range(3):
            years_in_cluster = df.loc[X_cluster.index, '年份'][clusters == i].values
            print(f"    类别{i+1}: {', '.join([str(int(y)) for y in years_in_cluster])} 年")
        
        return kmeans, clusters
    return None, None


def pca_analysis(df):
    """PCA主成分分析"""
    print("\n(5) PCA主成分分析 - 经济指标降维")
    
    if not SKLEARN_AVAILABLE:
        print("  (需要安装scikit-learn)")
        return None
    
    pca_features = ['GDP(亿元)', '人均GDP(元)', '总人口(万人)', '城镇化率(%)', 
                    '人均可支配收入(元)', '人均消费支出(元)']
    X_pca = df[pca_features].dropna()
    
    if len(X_pca) >= 2:
        scaler_pca = StandardScaler()
        X_pca_scaled = scaler_pca.fit_transform(X_pca)
        
        pca = PCA(n_components=2)
        X_pca_transformed = pca.fit_transform(X_pca_scaled)
        
        print(f"  第一主成分解释方差比: {pca.explained_variance_ratio_[0]:.4f}")
        print(f"  第二主成分解释方差比: {pca.explained_variance_ratio_[1]:.4f}")
        print(f"  累计解释方差比: {sum(pca.explained_variance_ratio_):.4f}")
        
        return pca
    return None


def trend_analysis(df):
    """
    趋势分析
    分析各指标的时间趋势特征，包括年均增长率、线性趋势等
    """
    print("\n(6) 趋势分析 - 经济指标时间趋势特征")

    if not SKLEARN_AVAILABLE:
        print("  (需要安装scikit-learn)")
        return None

    # 定义要分析的关键指标
    indicators = {
        'GDP(亿元)': 'GDP',
        '人均GDP(元)': '人均GDP',
        '人均可支配收入(元)': '人均可支配收入',
        '人均消费支出(元)': '人均消费支出',
        '城镇化率(%)': '城镇化率',
        '进出口总额(亿元)': '进出口总额'
    }

    print("\n  【年均增长率分析】")
    years = df['年份'].values
    n_years = len(years)

    growth_rates = {}
    for col, name in indicators.items():
        if col in df.columns:
            values = df[col].dropna().values
            if len(values) >= 2:
                # 计算复合年均增长率 (CAGR)
                start_value = values[0]
                end_value = values[-1]
                years_diff = len(values) - 1
                if start_value > 0 and years_diff > 0:
                    cagr = ((end_value / start_value) ** (1 / years_diff) - 1) * 100
                    growth_rates[name] = cagr
                    print(f"    {name}: {cagr:.2f}%/年")

    print("\n  【线性趋势分析】")
    for col, name in indicators.items():
        if col in df.columns:
            data = df[['年份', col]].dropna()
            if len(data) >= 3:
                X = data['年份'].values.reshape(-1, 1)
                y = data[col].values

                # 线性回归拟合
                model = LinearRegression()
                model.fit(X, y)

                # 计算趋势强度 (R²)
                y_pred = model.predict(X)
                r2 = r2_score(y, y_pred)

                # 判断趋势方向
                slope = model.coef_[0]
                if slope > 0:
                    trend = "上升"
                elif slope < 0:
                    trend = "下降"
                else:
                    trend = "稳定"

                print(f"    {name}: {trend}趋势 (斜率={slope:.2f}, R²={r2:.4f})")

    return growth_rates


def cycle_analysis(df):
    """
    周期分析
    分析经济周期特征，识别增长阶段和波动特征
    """
    print("\n(7) 周期分析 - 经济周期特征识别")

    # GDP增长率周期分析
    print("\n  【GDP增长率周期分析】")
    if 'GDP增长率(%)' in df.columns:
        growth_rate = df['GDP增长率(%)'].dropna().values
        years = df.loc[df['GDP增长率(%)'].notna(), '年份'].values

        if len(growth_rate) > 0:
            mean_growth = np.mean(growth_rate)
            std_growth = np.std(growth_rate)

            print(f"    平均增长率: {mean_growth:.2f}%")
            print(f"    增长率标准差: {std_growth:.2f}%")
            print(f"    波动系数: {(std_growth/mean_growth)*100:.2f}%")

            # 识别周期阶段
            print("\n    【增长阶段识别】")
            for i, (year, rate) in enumerate(zip(years, growth_rate)):
                if rate > mean_growth + std_growth:
                    phase = "高速增长期"
                elif rate < mean_growth - std_growth:
                    phase = "低速增长期"
                else:
                    phase = "平稳增长期"
                print(f"      {int(year)}年: {rate:.2f}% - {phase}")

    # 产业结构变化周期
    print("\n  【产业结构演变分析】")
    if all(col in df.columns for col in ['第一产业占比(%)', '第二产业占比(%)', '第三产业占比(%)']):
        industry_data = df[['年份', '第一产业占比(%)', '第二产业占比(%)', '第三产业占比(%)']].dropna()

        if len(industry_data) >= 2:
            first_year = industry_data.iloc[0]
            last_year = industry_data.iloc[-1]

            print(f"    产业结构变化 ({int(first_year['年份'])}年 → {int(last_year['年份'])}年):")
            print(f"      第一产业: {first_year['第一产业占比(%)']:.2f}% → {last_year['第一产业占比(%)']:.2f}%")
            print(f"      第二产业: {first_year['第二产业占比(%)']:.2f}% → {last_year['第二产业占比(%)']:.2f}%")
            print(f"      第三产业: {first_year['第三产业占比(%)']:.2f}% → {last_year['第三产业占比(%)']:.2f}%")

            # 判断产业结构升级趋势
            if last_year['第三产业占比(%)'] > first_year['第三产业占比(%)']:
                print("    产业结构升级趋势: 明显 (第三产业占比上升)")

    # 人口周期分析
    print("\n  【人口周期分析】")
    if '出生率(‰)' in df.columns and '死亡率(‰)' in df.columns:
        birth_rate = df['出生率(‰)'].dropna().values
        death_rate = df['死亡率(‰)'].dropna().values
        years_pop = df.loc[df['出生率(‰)'].notna(), '年份'].values

        if len(birth_rate) > 0:
            print(f"    出生率变化: {birth_rate[0]:.2f}‰ → {birth_rate[-1]:.2f}‰")
            print(f"    死亡率变化: {death_rate[0]:.2f}‰ → {death_rate[-1]:.2f}‰")
            print(f"    出生率年均变化: {(birth_rate[-1] - birth_rate[0]) / len(birth_rate):.2f}‰/年")

    return None


def simple_forecast(df, forecast_years=3):
    """
    简单预测
    使用线性回归和移动平均对未来几年的经济指标进行预测

    参数:
        df: 数据框
        forecast_years: 预测年数，默认3年
    """
    print(f"\n(8) 简单预测 - 未来{forecast_years}年经济指标预测")

    if not SKLEARN_AVAILABLE:
        print("  (需要安装scikit-learn)")
        return None

    # 获取最后一年
    last_year = int(df['年份'].max())
    future_years = np.array([last_year + i for i in range(1, forecast_years + 1)]).reshape(-1, 1)

    # 定义要预测的指标
    forecast_indicators = {
        'GDP(亿元)': 'GDP',
        '人均GDP(元)': '人均GDP',
        '人均可支配收入(元)': '人均可支配收入',
        '人均消费支出(元)': '人均消费支出',
        '城镇化率(%)': '城镇化率'
    }

    print("\n  【线性回归预测】")
    forecasts = {}

    for col, name in forecast_indicators.items():
        if col in df.columns:
            data = df[['年份', col]].dropna()

            if len(data) >= 3:
                X = data['年份'].values.reshape(-1, 1)
                y = data[col].values

                # 训练模型
                model = LinearRegression()
                model.fit(X, y)

                # 预测未来值
                future_values = model.predict(future_years)

                # 计算模型性能
                y_pred_train = model.predict(X)
                r2 = r2_score(y, y_pred_train)
                rmse = np.sqrt(mean_squared_error(y, y_pred_train))

                print(f"\n    {name}预测:")
                print(f"      模型性能: R²={r2:.4f}, RMSE={rmse:.2f}")
                print(f"      预测结果:")

                for year, value in zip(future_years.flatten(), future_values):
                    print(f"        {int(year)}年: {value:.2f}")

                forecasts[name] = {
                    'years': future_years.flatten(),
                    'values': future_values,
                    'r2': r2,
                    'model': model
                }

    # 移动平均预测
    print("\n  【移动平均预测】(3年移动平均)")
    for col, name in forecast_indicators.items():
        if col in df.columns:
            data = df[col].dropna()
            if len(data) >= 3:
                # 计算3年移动平均
                ma_values = data.rolling(window=3, min_periods=1).mean().values
                last_ma = ma_values[-1]

                # 简单预测：使用最近的移动平均趋势
                if len(ma_values) >= 2:
                    trend = ma_values[-1] - ma_values[-2]
                    future_ma = [last_ma + trend * (i + 1) for i in range(forecast_years)]

                    print(f"\n    {name}移动平均预测:")
                    for year, value in zip(future_years.flatten(), future_ma):
                        print(f"      {int(year)}年: {value:.2f}")

    # 预测可靠性评估
    print("\n  【预测可靠性评估】")
    print("    注意事项:")
    print("    1. 线性回归假设指标呈线性增长，实际经济变化可能非线性")
    print("    2. 移动平均法适用于短期预测，长期预测误差会累积")
    print("    3. 预测结果仅供参考，实际经济发展受多种因素影响")
    print("    4. 建议结合政策环境、国际形势等定性分析")

    return forecasts


def run_all_ml_analysis(df):
    """运行所有机器学习分析"""
    print("\n【4.4 关联分析（机器学习方法）】")

    # 相关性分析
    corr_matrix = correlation_analysis(df)

    # 回归分析
    linear_regression_analysis(df)
    multiple_regression_analysis(df)

    # 聚类分析
    kmeans_clustering(df)

    # PCA分析
    pca_analysis(df)

    # 趋势分析
    trend_analysis(df)

    # 周期分析
    cycle_analysis(df)

    # 简单预测
    simple_forecast(df)

    return corr_matrix
