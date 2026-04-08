library(ggplot2)
library(dplyr)

a = head(mtcars)
# print(a)

# 画图
b = ggplot(mtcars, aes(x = wt, y = mpg)) + 
  geom_point(size = 3, color = "steelblue") +
  labs(title = "汽车重量与油耗关系",
       x = "车重（1000磅）",
       y = "油耗（英里/加仑）") +
  theme_minimal()

print(b)

# (1) 对mpg（英里/加仑）变量，计算均值、中位数、标准差、四分数
mtcars %>% summarise(
    mean_mpg = mean(mpg),
    median_mpg = median(mpg),
    std_mpg = sd(mpg),
    q1_mpg = quantile(mpg, 0.25),
    q3_mpg = quantile(mpg, 0.75)
)%>%
    print()

# (2)绘制mpg的直方图，设置合适的组数，添加密度曲线
c = ggplot(mtcars, aes(x = mpg)) +
  geom_histogram(
    aes(y = after_stat(density)),
    bins = 10,
    fill = 'lightblue',
    col = 'black'
  ) + 
  geom_density(col = 'red', linewidth = 1) +
  labs(
    title = 'mpg的直方图',
    x = 'Miles per Gallon',
    y = 'Density'
  )

print(c)

# (3)绘制mpg的箱线图，观察离群点
d = ggplot(mtcars ,aes(y = mpg)) +
        geom_boxplot(fill = 'orange') +
        labs(title = 'mpg的箱线图', y = 'mpg')
print(d)

# (4)按气缸数 cyl(4,6,8)分组，绘制mpg的箱线图

e = ggplot(mtcars,aes(x = factor(cyl),y = mpg, fill = factor(cyl))) +
        geom_boxplot() + 
        labs(title = '不同气缸数的mpg的箱线图', x = 'Cylinders' ,y = 'mpg') +
        theme_minimal()
print(e)

