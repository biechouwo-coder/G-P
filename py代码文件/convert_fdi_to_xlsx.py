"""
将FDI的.xls文件转换为.xlsx格式（使用openpyxl）
"""

import pandas as pd
from pathlib import Path

# 先尝试读取.xls文件
FDI_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据\1996-2023年地级市外商直接投资FDI.xls")
OUTPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据\1996-2023年地级市外商直接投资FDI_converted.xlsx")

print("=" * 100)
print("FDI文件格式转换")
print("=" * 100)

# 尝试使用不同引擎读取
try:
    # 方法1: 使用openpyxl引擎
    print("\n尝试方法1: 直接读取.xls...")
    df_fdi = pd.read_excel(FDI_FILE, engine='xlrd')
    print(f"成功! 数据规模: {df_fdi.shape}")
except Exception as e:
    print(f"方法1失败: {e}")
    try:
        # 方法2: 先转换为CSV再读取
        print("\n尝试方法2: 使用其他方法...")
        # 暂时跳过，让用户手动转换或安装xlrd
        print("请手动在Excel中打开.xls文件并另存为.xlsx格式")
        print("或者运行: pip install xlrd")
        exit(1)
    except Exception as e2:
        print(f"方法2也失败: {e2}")
        exit(1)

# 查看数据结构
print(f"\n数据预览:")
print(df_fdi.head(5))

print(f"\n列名:")
for i, col in enumerate(df_fdi.columns):
    print(f"[{i:2d}] {col}")

# 保存为xlsx格式
df_fdi.to_excel(OUTPUT_FILE, index=False)
print(f"\n已转换为xlsx格式: {OUTPUT_FILE}")
print(f"文件大小: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
