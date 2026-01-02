"""
检查人口数据文件结构
"""
import pandas as pd

# 读取人口数据文件
df_pop_raw = pd.read_excel(r'c:\Users\HP\Desktop\毕业论文\原始数据\298个地级市人口密度1998-2024年无缺失.xlsx')

print("人口数据文件结构:")
print(f"Shape: {df_pop_raw.shape}")
print(f"\n列名:")
for i, col in enumerate(df_pop_raw.columns):
    print(f'  [{i}] {col}')

print(f"\n前3行数据:")
print(df_pop_raw.head(3))
