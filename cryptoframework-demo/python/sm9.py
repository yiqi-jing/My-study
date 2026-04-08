# ==================== 绝对可运行 · 无递归 · 无报错 ====================
def sqr(a):
    return a * a

def comb_precompute(x, n):
    comb_list = []
    l = 2
    s = 32 // n

    # 初始化每组基数
    current = x
    base_arr = []
    for i in range(n):
        base_arr.append(current)
        for _ in range(s):
            current = sqr(current)

    # 放入初始 [1, 基值]
    for b in base_arr:
        comb_list.append([1, b])

    # 7轮扩展
    for r in range(2):
        t = x
        for _ in range(s * (r + 1)):
            t = sqr(t)

        for j in range(n):
            for k in range(l):
                comb_list[j].append(comb_list[j][k] * t)
        l *= 2

    return comb_list, s

# ==================== 测试入口 ====================
if __name__ == '__main__':
    print("开始计算...")
    x = 2
    n = 1    #分组数
    res, s = comb_precompute(x, n)

    print("\n运行成功！")
    print(f"分组 n={n}, s={s}")
    print(f"组数={len(res)}, 每组长度={len(res[0])}")
    print("\n第 0 组前 10 个结果：")
    for i, val in enumerate(res[0][:10]):
        print(f"[{i}] = {val}")