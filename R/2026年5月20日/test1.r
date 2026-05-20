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


# 1. 读取数据并查看数据摘要和结构
if(!require(dplyr)) install.packages('dplyr');
library(dplyr)

# 读取数据
house_data <- read.csv("F:/My-study/R/2026年5月20日/house.csv", stringsAsFactors = FALSE)

# 查看数据结构
cat("=== 数据结构 ===\n")
str(house_data)

# 查看数据摘要
cat("\n=== 数据摘要 ===\n")
summary(house_data)

# 查看前几行数据
cat("\n=== 前5行数据 ===\n")
print(head(house_data))


# 2. 将 location 转换为因子（factor）类型
house_data$location = factor(house_data$location)

# 验证转换结果
cat("\n=== location 转换为因子后的结构 ===\n")
str(house_data$location)


# 3. 建立多元线性回归模型
model = lm(price ~ area + bedrooms + age + location, data = house_data)

# 查看模型结果
cat("\n=== 多元线性回归模型结果 ===\n")
summary(model)


# 4. 生成回归诊断图
cat("\n=== 生成回归诊断图 ===\n")
par(mfrow = c(2, 2))
plot(model)
par(mfrow = c(1, 1))

# 诊断结果说明
cat("\n=== 回归诊断分析 ===\n")
cat("1. 残差与拟合值图：检查线性关系和方差齐性\n")
cat("   - 若点随机分布在0附近，说明线性关系假设成立\n")
cat("   - 若呈现漏斗形状，说明存在异方差\n")
cat("2. 正态Q-Q图：检查残差的正态性\n")
cat("   - 若点大致落在直线上，说明残差服从正态分布\n")
cat("3. 标准化残差绝对值与拟合值：进一步检查方差齐性\n")
cat("4. 残差与杠杆值：识别异常值和高杠杆点\n")


# 5. 解释 area 和 age 对 price 的影响
cat("\n=== 变量影响解释 ===\n")
coef_summary = summary(model)$coefficients
area_coef = coef_summary["area", "Estimate"]
age_coef = coef_summary["age", "Estimate"]

cat(sprintf("area（房屋面积）的系数为 %.4f\n", area_coef))
cat("解释：在其他变量不变的情况下，房屋面积每增加1平方米，房价平均增加", 
    sprintf("%.4f", area_coef), "万元\n")

cat(sprintf("\nage（房龄）的系数为 %.4f\n", age_coef))
cat("解释：在其他变量不变的情况下，房龄每增加1年，房价平均", 
    ifelse(age_coef > 0, "增加", "减少"), sprintf("%.4f", abs(age_coef)), "万元\n")


# 6. 使用 step() 函数进行逐步回归
cat("\n=== 逐步回归分析（方向 both） ===\n")
full_model = lm(price ~ area + bedrooms + age + location, data = house_data)
step_model = step(full_model, direction = "both")

# 查看最优模型结果
cat("\n=== 最优模型结果 ===\n")
summary(step_model)

# 比较原始模型和最优模型
cat("\n=== 模型比较 ===\n")
cat("原始模型变量：price ~ area + bedrooms + age + location\n")
cat("最优模型变量：", paste(deparse(step_model$call), collapse = " "), "\n")

# 比较R平方
cat(sprintf("\n原始模型 R-squared: %.4f\n", summary(model)$r.squared))
cat(sprintf("最优模型 R-squared: %.4f\n", summary(step_model)$r.squared))

# 比较AIC
cat(sprintf("\n原始模型 AIC: %.2f\n", AIC(model)))
cat(sprintf("最优模型 AIC: %.2f\n", AIC(step_model)))