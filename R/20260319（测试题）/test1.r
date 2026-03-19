# 创建数据库sales date（7天），product （a，b，c，每天每种产品至少有一条记录）
# quantity（1-20随机）
# price（单价 a：10，b：15，c：20）
# 安装依赖包
if (!requireNamespace("dplyr", quietly = TRUE)) install.packages("dplyr")

# 加载dplyr包
library(dplyr)
# 使用rep和sample函数生成数据
sales = data.frame(
    data = as.Date(rep(c('2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05','2023-01-06', '2023-01-07'), each = 3)),
    product = rep(c('A', 'B', 'C'), times = 7),
    quantity = sample(1:20, 21, replace = TRUE),
    price = rep(c(10, 15, 20), times = 7)
)

# sales = data.frame(
#     date = as.Date(c('2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05','2023-01-06', '2023-01-07', '2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05','2023-01-06', '2023-01-07',
#                      '2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05','2023-01-06', '2023-01-07')),
#     product = c('A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'),
#     quantity = c(20,19,12,11,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18),
#     price = c(10, 15, 20, 10, 15, 20, 10, 15, 20, 10, 15, 20, 10, 15, 20, 10, 15, 20, 10, 15, 20)
# )
print(sales)

# (1) 添加一列revenue，计算每种产品的销售额（quantity * price）
sales1 = sales %>% mutate(revenue = quantity * price)
print(sales1)

#（2）计算每种产品在一周内的总销售额和总销售量，并按照总销售额度降序排序