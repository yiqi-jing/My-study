import pandas as pd
import os
import re  # 新增：用于正则表达式匹配提取数字


def clean_product_excel(input_path, output_path):
    # 1. 读取Excel文件
    print(f"正在读取文件: {input_path}")
    df = pd.read_excel(input_path)

    # 2. 步骤1：删除指定冗余列
    columns_to_drop = ['图片地址', '商品id', '当前页面网址', '当前时间', '页码', '商品链接']

    # 检查并筛选存在的列
    existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]
    missing_columns = [col for col in columns_to_drop if col not in df.columns]

    # 输出列删除前信息
    print(f"\n=== 列清理阶段 ===")
    print(f"清理前 - 数据维度: {df.shape} (行 x 列)")
    print(f"清理前 - 所有列名: {list(df.columns)}")

    if missing_columns:
        print(f"提示: 以下列不存在，无需删除: {missing_columns}")

    # 执行列删除
    if existing_columns_to_drop:
        df_cleaned = df.drop(columns=existing_columns_to_drop)
        print(f"已删除的列: {existing_columns_to_drop}")
    else:
        df_cleaned = df.copy()
        print("没有需要删除的列，进入数据格式标准化阶段")

    # 3. 步骤2：数据格式标准化
    print(f"\n=== 数据格式标准化阶段 ===")

    # 3.1 处理产品价格列：去除¥符号，转为数字
    if '产品价格' in df_cleaned.columns:
        # 方法：先移除¥符号，再尝试转为浮点数（处理可能的异常值）
        df_cleaned['产品价格'] = df_cleaned['产品价格'].astype(str).str.replace('¥', '', regex=False)
        # 尝试转为数字，无法转换的保持原文本
        df_cleaned['产品价格'] = pd.to_numeric(df_cleaned['产品价格'], errors='coerce')
        print(" 产品价格列：已移除¥符号，格式标准化完成")
    else:
        print("  产品价格列不存在，跳过价格格式处理")

    # 3.2 处理付款人数列：去除"付款"，保留数字
    if '付款人数' in df_cleaned.columns:
        # 方法1：直接替换"付款"文字
        df_cleaned['付款人数'] = df_cleaned['付款人数'].astype(str).str.replace('付款', '', regex=False)
        # 方法2：用正则提取所有数字
        df_cleaned['付款人数'] = df_cleaned['付款人数'].apply(
            lambda x: re.sub(r'[^\d]', '', x) if pd.notna(x) else x
        )
        # 转为数字类型（空值保持为NaN）
        df_cleaned['付款人数'] = pd.to_numeric(df_cleaned['付款人数'], errors='coerce')
        print(" 付款人数列：已移除'付款'文字，格式标准化完成")
    else:
        print("  付款人数列不存在，跳过人数字段处理")

    # 4. 输出最终清理结果信息
    print(f"\n=== 最终清理结果 ===")
    print(f"清理后 - 数据维度: {df_cleaned.shape} (行 x 列)")
    print(f"清理后 - 剩余列名: {list(df_cleaned.columns)}")

    # 5. 保存清理后的数据
    df_cleaned.to_excel(output_path, index=False)
    print(f"\n 所有清理步骤完成！文件已保存到: {output_path}")

    # 6. 返回清理后的数据预览
    return df_cleaned.head()


# 执行清理操作
input_file = 'F:\Data Analysis\OriginalProductListData.xlsx'
output_file = 'F:\Data Analysis\CleanedProductListData.xlsx'

# 调用函数并显示预览
cleaned_preview = clean_product_excel(input_file, output_file)

# 显示清理后的数据预览（重点展示格式变化）
print("\n=== 清理后数据预览（前5行）===")
print(cleaned_preview[['产品名称', '产品价格', '付款人数']])