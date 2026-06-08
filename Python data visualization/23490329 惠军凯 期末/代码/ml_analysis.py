# -*- coding: utf-8 -*-
"""
机器学习分析模块
包含回归、聚类、PCA等分析方法
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
    
    return corr_matrix
