"""
产业结构数据转换脚本
将.xls格式转换为.xlsx格式，以便后续合并
"""

import sys
import os
from pathlib import Path
import pandas as pd

# 尝试读取.xls文件
input_file = r"c:\Users\HP\Desktop\毕业论文\原始数据\2000-2023地级市产业结构 - 面板.xls"
output_file = r"c:\Users\HP\Desktop\毕业论文\原始数据\2000-2023地级市产业结构 - 面板.xlsx"

print(f"Input file: {input_file}")
print(f"Output file: {output_file}")

# 方法1: 尝试使用xlrd引擎
try:
    print("\nTrying to read with xlrd engine...")
    df = pd.read_excel(input_file, engine='xlrd')
    print(f"Success! Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # 保存为.xlsx
    df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"\nSuccessfully converted to: {output_file}")
    sys.exit(0)

except Exception as e:
    print(f"xlrd failed: {e}")

    # 方法2: 尝试不指定引擎
    try:
        print("\nTrying to read without engine specification...")
        df = pd.read_excel(input_file)
        print(f"Success! Shape: {df.shape}")

        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"\nSuccessfully converted to: {output_file}")
        sys.exit(0)

    except Exception as e2:
        print(f"Failed: {e2}")
        print("\nPlease use one of these methods:")
        print("1. Open .xls file in Excel, Save As .xlsx format")
        print("2. Use online converter (zamzar.com, convertio.co)")
        print("3. Check if the .xls file is corrupted")
        sys.exit(1)
