"""
准备二产占比模型数据集

操作：
1. 读取PSM匹配后数据集（二产替代三产版本）
2. 删除三产占比变量（tertiary_share, tertiary_share_sq）
3. 保留二产占比变量（secondary_share, secondary_share_sq）
4. 保存到新文件夹

作者: Claude Code
日期: 2026-01-09
"""

import pandas as pd
import os
from pathlib import Path

print("=" * 100)
print("准备二产占比模型数据集")
print("=" * 100)

# 读取匹配后的数据集
INPUT_FILE = "倾向得分匹配_匹配后数据集_二产替代三产.xlsx"
OUTPUT_DIR = Path("二产占比模型_分析结果")
OUTPUT_FILE = OUTPUT_DIR / "PSM匹配后数据集_仅二产占比.xlsx"

# 创建输出目录
OUTPUT_DIR.mkdir(exist_ok=True)

df = pd.read_excel(INPUT_FILE)
print(f"\n数据集加载成功: {df.shape[0]} 个观测 × {df.shape[1]} 个变量")

# 显示原始变量
print(f"\n原始变量列表 ({len(df.columns)} 个):")
for i, var in enumerate(df.columns, 1):
    print(f"  {i:2d}. {var}")

# 删除三产占比变量
cols_to_drop = ['tertiary_share', 'tertiary_share_sq']
print(f"\n删除三产占比变量:")
for col in cols_to_drop:
    if col in df.columns:
        df = df.drop(columns=[col])
        print(f"  [删除] {col}")
    else:
        print(f"  [不存在] {col}")

# 保留二产占比变量
print(f"\n保留二产占比变量:")
secondary_vars = ['secondary_share', 'secondary_share_sq']
for var in secondary_vars:
    if var in df.columns:
        print(f"  [保留] {var}")
    else:
        print(f"  [警告] {var} 不存在")

# 显示最终变量列表
print(f"\n最终变量列表 ({len(df.columns)} 个):")
for i, var in enumerate(df.columns, 1):
    print(f"  {i:2d}. {var}")

# 保存数据集
df.to_excel(OUTPUT_FILE, index=False)
print(f"\n[OK] 数据集已保存到: {OUTPUT_FILE}")
print(f"文件大小: {OUTPUT_FILE.stat().st_size / 1024:.2f} KB")

# 生成变量说明
print("\n" + "=" * 100)
print("变量说明")
print("=" * 100)

print("""
核心变量：
- ln_carbon_intensity: 碳排放强度对数（因变量）
- did: DID政策变量（核心自变量）
- treat: 处理组标识
- post: 政策实施期标识
- pilot_year: 试点开始年份

协变量（二产占比模型）：
1. ln_pgdp: 人均GDP对数
2. ln_pop_density: 人口密度对数
3. secondary_share: 第二产业占比【核心变量】
4. secondary_share_sq: 第二产业占比平方【核心变量】
5. ln_fdi: 外商直接投资对数
6. ln_road_area: 道路面积对数

固定效应：
- city_name: 城市名称（用于城市固定效应）
- year: 年份（用于年份固定效应）

与三产占比模型差异：
- 删除: tertiary_share, tertiary_share_sq
- 保留: secondary_share, secondary_share_sq
- 其他变量保持不变
""")

print("=" * 100)
print("[OK] 数据准备完成!")
print("=" * 100)
