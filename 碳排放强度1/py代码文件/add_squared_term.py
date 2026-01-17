"""
添加第三产业占比平方项 (tertiary_share_sq)
用于改进PSM匹配模型，捕捉产业结构的非线性效应
"""

import pandas as pd
import os

def add_tertiary_share_squared():
    """
    在数据集中添加 tertiary_share_sq 变量
    """
    # 读取最终回归版数据
    input_file = '总数据集_2007-2023_最终回归版.xlsx'
    print(f"[INFO] 正在读取数据文件: {input_file}")

    df = pd.read_excel(input_file)
    print(f"[OK] 数据读取成功，共 {len(df)} 条观测")

    # 检查 tertiary_share 列是否存在
    if 'tertiary_share' not in df.columns:
        print("[ERROR] 未找到 tertiary_share 列")
        print(f"[INFO] 可用列: {list(df.columns)}")
        return None

    # 构造平方项
    df['tertiary_share_sq'] = df['tertiary_share'] ** 2

    # 显示新变量的统计信息
    print("\n[SUCCESS] 成功构造 tertiary_share_sq 变量")
    print("\n tertiary_share 描述性统计:")
    print(df['tertiary_share'].describe())
    print("\ntertiaryary_share_sq 描述性统计:")
    print(df['tertiary_share_sq'].describe())

    # 保存更新后的数据集
    output_file = '总数据集_2007-2023_最终回归版_含平方项.xlsx'
    df.to_excel(output_file, index=False)
    print(f"\n[OK] 数据已保存到: {output_file}")

    # 覆盖原文件（用于后续PSM流程）
    df.to_excel(input_file, index=False)
    print(f"[OK] 已更新原文件: {input_file}")

    return df

if __name__ == "__main__":
    df = add_tertiary_share_squared()

    if df is not None:
        print("\n" + "="*60)
        print("[COMPLETE] 第三产业占比平方项构造完成")
        print("="*60)
        print(f"样本量: {len(df)}")
        print(f"变量数: {len(df.columns)}")
        print(f"新增变量: tertiaryary_share_sq")