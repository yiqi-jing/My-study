### 案例题1：房价预测与线性回归建模

## 背景
# 你获得了一份关于某城市房价的数据集 house.csv，包含以下变量：
# price：房价（万元，连续变量）
# area：房屋面积（平方米）
# bedrooms：卧室数量
# age：房龄（年）
# location：位置等级（A、B、C三个等级，分类变量）

## 任务要求：
# 1.读取数据（假设文件在当前目录），并查看数据摘要和结构。
# 2.将 location 转换为因子（factor）类型。
# 3.建立多元线性回归模型，以 price 为因变量，其他所有变量为自变量。
# 4.使用 plot() 函数生成回归诊断图，并简要判断模型是否满足线性回归的基本假设。
# 5.根据模型输出，解释 area 和 age 对 price 的影响。
# 6.使用 step() 函数进行逐步回归（方向 both），找出最优模型，并与原始模型比较。


# 1.导入包
if(!require(dplyr)) install.packages('dplyr');
library(dplyr)

# 读取数据
house_data = read.csv('F:/My-study/R/2026年5月20日/house.csv', stringsAsFactors = FALSE)

# 查看数据结构和摘要
cat('====数据结构====\n')
str(house_data)

# 查看前几行数据
cat('\n====前5行数据=====\n')
print(head(house_data,5))

# 2. 将location 转换为因子(factor)类型
house_data$location = factor(house_data$location)

# 验证转换结果
cat("\n=====转换为因子后的结构=====\n")
str(house_data$location)
