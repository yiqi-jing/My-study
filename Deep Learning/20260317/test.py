import torch

# 第一部分：熟悉PyTorch API，理解device和dtype
print("第一部分：熟悉PyTorch API，理解device和dtype")
print("=" * 60)

# 任务1：创建一个形状为 (3, 4, 5) 的随机整数张量（范围 0-10），数据类型为 torch.float32
tensor = torch.randint(0, 11, (3, 4, 5), dtype=torch.float32)
print("任务1：创建随机整数张量")
print(f"张量形状: {tensor.shape}")
print(f"数据类型: {tensor.dtype}")
print(f"设备: {tensor.device}")
print(f"维度: {tensor.ndim}")
print(f"元素个数: {tensor.numel()}")
print(f"张量内容:\n{tensor}")
print()

# 思考：.size() 和 .shape 有什么区别？
print("思考：.size() 和 .shape 的区别")
print(f".size(): {tensor.size()}")
print(f".shape: {tensor.shape}")
print("区别：.size() 返回的是torch.Size对象，.shape 返回的是元组，但两者内容相同")
print()

# 任务2：将上述张量转换为 torch.int64，再转回 float
print("任务2：类型转换")
tensor_int64 = tensor.to(torch.int64)
tensor_float32 = tensor_int64.to(torch.float32)
print(f"转换为int64后:\n{tensor_int64}")
print(f"转换回float32后:\n{tensor_float32}")
print(f"是否有精度变化: {not torch.allclose(tensor, tensor_float32)}")
print()

# 第二部分：掌握类似NumPy的切片，重点理解视图（View）与拷贝（Clone）的区别
print("第二部分：掌握类似NumPy的切片，理解视图与拷贝的区别")
print("=" * 60)

# 任务1：给定张量 x = torch.arange(12).reshape(3, 4)
x = torch.arange(12).reshape(3, 4)
print("任务1：切片操作")
print(f"原始张量 x:\n{x}")
print()

# （1）取出第 2 行
row_2 = x[1, :]
print("（1）取出第 2 行:", row_2)

# （2）取出最后两列
last_two_cols = x[:, -2:]
print("（2）取出最后两列:\n", last_two_cols)

# （3）取出第 0 行和第 2 行的第 1 列元素
elements = x[[0, 2], 1]
print("（3）取出第 0 行和第 2 行的第 1 列元素:", elements)

# （4）使用负数索引取出右下角 2 x 2 的子矩阵
bottom_right = x[-2:, -2:]
print("（4）取出右下角 2 x 2 的子矩阵:\n", bottom_right)

# （5）在 x 中找出所有大于 5 的元素，并将它们替换为 -1
x_copy = x.clone()
x_copy[x_copy > 5] = -1
print("（5）替换大于 5 的元素为 -1:\n", x_copy)

# （6）统计大于 5 的元素个数
count = torch.sum(x > 5)
print("（6）大于 5 的元素个数:", count)
print()

# 任务2：观察视图与拷贝的区别
print("任务2：视图与拷贝的区别")
a = torch.arange(6)
b = a[:3]      # 这是一个视图 (View)
c = a[:3].clone() # 这是一个拷贝 (Clone)
b[0] = 999
c[0] = 888
print(f"原始张量 a: {a}")
print(f"视图 b: {b}")
print(f"拷贝 c: {c}")
print("问题：为什么修改 b 会影响 a，而修改 c 不会？")
print("答案：因为视图是张量的一个引用，共享内存，而拷贝是创建了一个新的张量，拥有独立的内存")
print()

# 任务3：使用 .reshape() 和 .view() 改变形状
print("任务3：reshape() 和 view() 的使用")
t = torch.arange(12)
print(f"原始张量: {t}")

# 使用 reshape 改变形状
t_reshaped = t.reshape(3, 4)
print(f"使用 reshape 后的形状: {t_reshaped.shape}")

# 使用 view 改变形状
t_viewed = t.view(3, 4)
print(f"使用 view 后的形状: {t_viewed.shape}")

# 尝试对非连续张量使用 .view() 观察报错
print("\n尝试对非连续张量使用 .view():")
t_non_contiguous = t_reshaped[:, ::2]  # 创建一个非连续张量
print(f"非连续张量形状: {t_non_contiguous.shape}")
print(f"是否连续: {t_non_contiguous.is_contiguous()}")

# 尝试直接使用 view
# t_viewed_non_contiguous = t_non_contiguous.view(2, 3)  # 这会报错

# 使用 contiguous() 后再 view
t_contiguous = t_non_contiguous.contiguous()
print(f"使用 contiguous() 后是否连续: {t_contiguous.is_contiguous()}")
t_viewed_contiguous = t_contiguous.view(2, 3)
print(f"使用 contiguous() 后 view 的结果形状: {t_viewed_contiguous.shape}")
print()

# 第三部分：理解"自动扩展维度"的规则，学会用广播代替 for 循环
print("第三部分：理解广播机制")
print("=" * 60)

# 广播规则：从后向前对齐维度，维度大小为 1 或缺失的维度可以自动扩展
print("广播规则练习：")

# （1）形状为(3, 1) 和 (1, 4) 的张量相加
t1 = torch.ones(3, 1)
t2 = torch.ones(1, 4)
result1 = t1 + t2
print("（1）形状为(3, 1) 和 (1, 4) 的张量相加")
print(f"结果形状: {result1.shape}")
print(f"结果:\n{result1}")
print()

# （2）形状为(2, 3, 4) 和 (4,) 的张量相加
t3 = torch.ones(2, 3, 4)
t4 = torch.ones(4)
result2 = t3 + t4
print("（2）形状为(2, 3, 4) 和 (4,) 的张量相加")
print(f"结果形状: {result2.shape}")
print()

# （3）形状为 (2, 3, 4) 和 (2, 1, 4) 的张量相加
t5 = torch.ones(2, 3, 4)
t6 = torch.ones(2, 1, 4)
result3 = t5 + t6
print("（3）形状为 (2, 3, 4) 和 (2, 1, 4) 的张量相加")
print(f"结果形状: {result3.shape}")
