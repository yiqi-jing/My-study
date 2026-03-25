# 创建两个数据框（数据自模拟，要求包含至少一个dept_id 在departments表中不存在的员工，以及一个dept_id为NA的员工）。
# （1）将employees和departments按照部门编号镜像左连接（left_join(数据框名称，by=连接的列)），得到一个完整的数据框emp_full，包含所有员工信息以及对应的部门名称，如果员工部门编号不存在与department中这dept_name显示为NA。
# 开始模拟数据
# employees包含 em_id(1-8),name,dept_id(101,102,103,NA),salary(3000-8000)

# departments包含 dept_id(101,102,103),dept_name("HR","Finance","IT")
# 加载必要的库
library(dplyr)
# 创建employees数据框
employees = data.frame(
  em_id = 1:8,
  name = c("Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi"),
  dept_id = c(101, 102, 103, NA, 101, 102, 104, NA), # 包含一个不存在的dept_id(104)和一个NA
  salary = c(3000, 4000, 5000, 6000, 7000, 8000, 3500, 4500)
)
# 创建departments数据框
departments = data.frame(
  dept_id = c(101, 102, 103),
  dept_name = c("HR", "Finance", "IT")
)
# 将employees和departments按照部门编号进行左连接
emp_full = left_join(employees, departments, by = "dept_id")
# 查看结果
print(emp_full)

# (2)将dept_name为NA的员工筛选出来，输出这些员工的姓名和部门编号，提示‘未匹配到部门’
# 筛选dept_name为NA的员工
unmatched_employees = emp_full %>%
  filter(is.na(dept_name)) %>%
  select(name, dept_id) %>%
  mutate(message = "未匹配到部门")
# 输出结果
print(unmatched_employees)