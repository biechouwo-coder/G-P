"""
FDI数据完整处理脚本
功能：
1. 读取FDI原始数据
2. 清洗城市名称（添加"市"后缀，去除特殊字符）
3. 筛选研究时段（2007-2023）
4. 处理缺失值（剔除严重缺失城市，插值中间缺失）
5. 计算FDI开放度（FDI/GDP）
6. 合并到主数据集

作者：Claude Code
日期：2025-01-06
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("FDI数据完整处理流程")
print("=" * 80)
print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 文件路径
FDI_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据\1996-2023年地级市外商直接投资FDI.xlsx")
MAIN_DATA = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_修正FDI.xlsx")
OUTPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_完整版_无缺失FDI.xlsx")

# ================================
# 步骤1：读取FDI原始数据
# ================================
print("\n[步骤1/6] 读取FDI原始数据...")

try:
    df_fdi = pd.read_excel(FDI_FILE)
    print(f"[OK] 原始数据维度: {df_fdi.shape}")
    print(f"  列名: {list(df_fdi.columns)}")
    print(f"\n前5行数据预览:")
    print(df_fdi.head())
except FileNotFoundError:
    print(f"[ERROR] 找不到文件 {FDI_FILE}")
    exit(1)

# ================================
# 步骤2：清洗城市名称
# ================================
print("\n[步骤2/6] 清洗城市名称...")

# 数据结构是: [year, 城市, FDI数值, 单位, 数据来源]
# 按位置提取列
df_fdi = df_fdi.iloc[:, [0, 1, 2]]  # 只保留 year, 城市, FDI
df_fdi.columns = ['year', 'city_name', 'fdi']

print(f"提取后数据结构:")
print(df_fdi.head())

# 清洗城市名称
def clean_city_name(name):
    """清洗城市名称：添加"市"后缀，去除特殊字符，处理城市更名"""
    if pd.isna(name):
        return name

    name = str(name).strip()

    # 去除零宽空格等特殊字符
    name = name.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')
    name = name.replace('\xa0', ' ').strip()

    # 处理城市更名（统一使用新名称）
    city_rename_map = {
        '襄樊市': '襄阳市',  # 2010年更名
        '思茅市': '普洱市',   # 2007年更名
        '襄樊': '襄阳市',
        '思茅': '普洱市'
    }

    if name in city_rename_map:
        name = city_rename_map[name]

    # 如果不以"市"结尾，且不是特殊的地区类型，添加"市"
    if not name.endswith(('市', '地区', '自治区', '自治州', '盟')):
        # 排除直辖市（北京、上海、天津、重庆）—它们需要加"市"
        if name in ['北京', '上海', '天津', '重庆']:
            name = name + '市'
        elif not name.endswith('市'):  # 其他非直辖市也加"市"
            name = name + '市'

    return name

df_fdi['city_name'] = df_fdi['city_name'].apply(clean_city_name)

print(f"[OK] 清洗后城市名称示例（前10个）:")
print(df_fdi['city_name'].unique()[:10])

# ================================
# 步骤3：筛选研究时段
# ================================
print("\n[步骤3/6] 筛选研究时段（2007-2023）...")

# 确保year是数值类型
df_fdi['year'] = pd.to_numeric(df_fdi['year'], errors='coerce')

# 筛选2007-2023年
df_fdi = df_fdi[(df_fdi['year'] >= 2007) & (df_fdi['year'] <= 2023)]

print(f"[OK] 筛选后数据维度: {df_fdi.shape}")
print(f"  年份范围: {df_fdi['year'].min()} - {df_fdi['year'].max()}")
print(f"  城市数量: {df_fdi['city_name'].nunique()}")

# ================================
# 步骤4：诊断和处理缺失值
# ================================
print("\n[步骤4/6] 诊断和处理缺失值...")

# 计算每个城市的缺失率
city_missing_rate = df_fdi.groupby('city_name')['fdi'].apply(
    lambda x: x.isna().sum() / len(x)
).sort_values(ascending=False)

print("\n各城市FDI数据缺失率（最高的20个）:")
print(city_missing_rate.head(20))

# 识别严重缺失的城市（缺失率 > 50%）
severe_missing_cities = city_missing_rate[city_missing_rate > 0.5].index.tolist()
print(f"\n严重缺失城市数量（缺失率>50%）: {len(severe_missing_cities)}")
if severe_missing_cities:
    print(f"严重缺失城市列表: {severe_missing_cities[:10]}...")  # 只显示前10个

# 剔除严重缺失的城市
df_fdi_clean = df_fdi[~df_fdi['city_name'].isin(severe_missing_cities)].copy()

print(f"\n[OK] 剔除严重缺失城市后:")
print(f"  数据维度: {df_fdi_clean.shape}")
print(f"  剩余城市数量: {df_fdi_clean['city_name'].nunique()}")

# 对剩余数据进行线性插值（按城市分组）
df_fdi_clean = df_fdi_clean.sort_values(['city_name', 'year'])

def interpolate_fdi(group):
    """对单个城市的时间序列进行插值（包括端点）"""
    group = group.copy()

    # 步骤1: 线性插值中间缺失值
    group['fdi_interpolated'] = group['fdi'].interpolate(
        method='linear',
        limit_direction='both',
        limit=None
    )

    # 步骤2: 如果端点仍有缺失，使用前向/后向填充
    # 对于起始年份缺失，用后向填充
    # 对于结束年份缺失，用前向填充
    group['fdi_interpolated'] = group['fdi_interpolated'].fillna(method='bfill').fillna(method='ffill')

    return group

df_fdi_clean = df_fdi_clean.groupby('city_name').apply(interpolate_fdi).reset_index(drop=True)

# 统计插值情况
total_missing_before = df_fdi_clean['fdi'].isna().sum()
total_missing_after = df_fdi_clean['fdi_interpolated'].isna().sum()
interpolated_count = total_missing_before - total_missing_after

print(f"\n[OK] 插值统计:")
print(f"  插值前缺失值: {total_missing_before}")
print(f"  插值后缺失值: {total_missing_after}")
print(f"  插值填充数量: {interpolated_count}")

# 使用插值后的数据
df_fdi_clean['fdi'] = df_fdi_clean['fdi_interpolated']
df_fdi_clean = df_fdi_clean.drop(columns=['fdi_interpolated'])

# 检查是否仍有缺失值（应该为0，如果大于0说明整个城市都无数据）
final_missing_count = df_fdi_clean['fdi'].isna().sum()
final_missing_cities = df_fdi_clean[df_fdi_clean['fdi'].isna()]['city_name'].unique()

if final_missing_count > 0:
    print(f"\n[WARNING] 以下城市插值后仍有缺失值（完全无数据），将被剔除:")
    print(f"  城市数量: {len(final_missing_cities)}")
    print(f"  缺失观测数: {final_missing_count}")
    df_fdi_clean = df_fdi_clean[~df_fdi_clean['city_name'].isin(final_missing_cities)]

print(f"\n[OK] 最终FDI数据:")
print(f"  数据维度: {df_fdi_clean.shape}")
print(f"  城市数量: {df_fdi_clean['city_name'].nunique()}")
print(f"  年份范围: {df_fdi_clean['year'].min()} - {df_fdi_clean['year'].max()}")
print(f"  缺失值数量: {df_fdi_clean['fdi'].isna().sum()}")

# ================================
# 步骤5：读取GDP数据并计算FDI开放度
# ================================
print("\n[步骤5/6] 计算FDI开放度（FDI/GDP）...")

# 直接从原始GDP文件读取名义GDP（不再使用实际GDP×平减指数的方法）
GDP_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据\296个地级市GDP相关数据（以2000年为基期）.xlsx")
df_gdp_raw = pd.read_excel(GDP_FILE)

# GDP文件结构（按列位置）：
# 列0: 省份, 列1: 城市, 列2: 年份, 列3: 名义GDP, 列4: GDP指数, 列5: 实际GDP, 列6: GDP平减指数
df_gdp_nominal = df_gdp_raw.iloc[:, [1, 2, 3]].copy()
df_gdp_nominal.columns = ['city_name', 'year', 'gdp_nominal']
df_gdp_nominal['year'] = pd.to_numeric(df_gdp_nominal['year'], errors='coerce')

# 清洗城市名称（与FDI数据保持一致）
def clean_city_name_for_gdp(name):
    """清洗城市名称：添加"市"后缀，去除特殊字符，处理城市更名"""
    if pd.isna(name):
        return name

    name = str(name).strip()

    # 去除零宽空格等特殊字符
    name = name.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')
    name = name.replace('\xa0', ' ').strip()

    # 处理城市更名（统一使用新名称）
    city_rename_map = {
        '襄樊市': '襄阳市',  # 2010年更名
        '思茅市': '普洱市',   # 2007年更名
        '襄樊': '襄阳市',
        '思茅': '普洱市'
    }

    if name in city_rename_map:
        name = city_rename_map[name]

    # 如果不以"市"结尾，且不是特殊的地区类型，添加"市"
    if not name.endswith(('市', '地区', '自治区', '自治州', '盟')):
        # 排除直辖市（北京、上海、天津、重庆）—它们需要加"市"
        if name in ['北京', '上海', '天津', '重庆']:
            name = name + '市'
        elif not name.endswith('市'):  # 其他非直辖市也加"市"
            name = name + '市'

    return name

df_gdp_nominal['city_name'] = df_gdp_nominal['city_name'].apply(clean_city_name_for_gdp)

print(f"[OK] 名义GDP数据维度: {df_gdp_nominal.shape}")
print(f"  年份范围: {df_gdp_nominal['year'].min()} - {df_gdp_nominal['year'].max()}")
print(f"  城市数量: {df_gdp_nominal['city_name'].nunique()}")
print(f"  名义GDP范围: {df_gdp_nominal['gdp_nominal'].min():.2f} - {df_gdp_nominal['gdp_nominal'].max():.2f} 亿元")

# 合并FDI和名义GDP数据
df_merged = pd.merge(
    df_fdi_clean,
    df_gdp_nominal,
    on=['city_name', 'year'],
    how='inner'
)

print(f"\n[OK] 合并后数据维度: {df_merged.shape}")

# ================================
# 计算FDI开放度（修正版 - 直接使用名义GDP）
# ================================
# 年平均汇率字典（人民币/美元）
exchange_rates = {
    2007: 7.6040, 2008: 6.9451, 2009: 6.8310, 2010: 6.7695,
    2011: 6.4588, 2012: 6.3125, 2013: 6.1928, 2014: 6.1428,
    2015: 6.2284, 2016: 6.6423, 2017: 6.7518, 2018: 6.6174,
    2019: 6.8985, 2020: 6.8976, 2021: 6.4515, 2022: 6.7261,
    2023: 7.0467
}

# 为每个年份匹配对应汇率
df_merged['exchange_rate'] = df_merged['year'].map(exchange_rates)

# 名义GDP已直接从原始文件读取，无需计算
# 之前的错误做法：名义GDP = 实际GDP × GDP平减指数

# 计算FDI开放度
# FDI单位：百万美元
# GDP单位：亿元（名义值，直接从原始文件读取）
# 转换：百万美元 × 汇率 / 100 = 亿元
df_merged['fdi_rmb'] = df_merged['fdi'] * df_merged['exchange_rate'] / 100  # 百万美元 -> 亿元
df_merged['fdi_openness'] = df_merged['fdi_rmb'] / df_merged['gdp_nominal']  # 使用名义GDP

print(f"\n[OK] FDI开放度计算完成（直接使用名义GDP + 年度汇率）")
print(f"  汇率范围: {df_merged['exchange_rate'].min():.4f} - {df_merged['exchange_rate'].max():.4f}")
print(f"  名义GDP范围: {df_merged['gdp_nominal'].min():.2f} - {df_merged['gdp_nominal'].max():.2f} 亿元")
print(f"  说明: 名义GDP直接来源于GDP原始文件（列3），未使用实际GDP×平减指数计算")

print(f"\n[OK] FDI开放度统计:")
print(df_merged['fdi_openness'].describe())

# 检查异常值（FDI开放度通常不会超过1，即FDI不超过GDP）
abnormal_count = (df_merged['fdi_openness'] > 1).sum()
print(f"\n异常值检查:")
print(f"  FDI开放度 > 1 的观测数: {abnormal_count}")

if abnormal_count > 0:
    print(f"  最大值: {df_merged['fdi_openness'].max():.4f}")
    print(f"  建议剔除这些异常值")

# 保留合理的观测值
df_final = df_merged[df_merged['fdi_openness'] <= 1].copy()

print(f"\n[OK] 剔除异常值后:")
print(f"  数据维度: {df_final.shape}")
print(f"  城市数量: {df_final['city_name'].nunique()}")

# 选择最终变量
df_final = df_final[['city_name', 'year', 'fdi', 'fdi_openness']]

# ================================
# 步骤6：合并到主数据集
# ================================
print("\n[步骤6/6] 合并到主数据集...")

# 读取完整主数据集
df_main_full = pd.read_excel(MAIN_DATA)

# 删除旧的fdi和fdi_openness列（如果存在）
if 'fdi' in df_main_full.columns:
    df_main_full = df_main_full.drop(columns=['fdi'])
if 'fdi_openness' in df_main_full.columns:
    df_main_full = df_main_full.drop(columns=['fdi_openness'])

# 外合并（使用新的修正后的FDI数据）
df_main_with_fdi = pd.merge(
    df_main_full,
    df_final,
    on=['city_name', 'year'],
    how='outer'
)

print(f"\n[OK] 最终数据集:")
print(f"  数据维度: {df_main_with_fdi.shape}")
print(f"  列名: {list(df_main_with_fdi.columns)}")

# 检查FDI开放度的缺失情况
fdi_missing_rate = df_main_with_fdi['fdi_openness'].isna().sum() / len(df_main_with_fdi)
print(f"\nFDI开放度缺失率: {fdi_missing_rate:.2%}")

# 保存更新后的数据集
df_main_with_fdi.to_excel(OUTPUT_FILE, index=False)

print(f"\n[OK] 数据已保存到: {OUTPUT_FILE}")

# ================================
# 生成数据质量报告
# ================================
print("\n" + "=" * 80)
print("FDI数据处理总结")
print("=" * 80)

print(f"\n1. 原始数据:")
print(f"   - 观测值数量: {len(df_fdi)}")
print(f"   - 城市数量: {df_fdi['city_name'].nunique()}")

print(f"\n2. 城市清洗:")
print(f"   - 剔除严重缺失城市: {len(severe_missing_cities)}个")
if 'final_missing_cities' in locals():
    print(f"   - 剔除完全无数据城市: {len(final_missing_cities)}个")
else:
    print(f"   - 剔除完全无数据城市: 0个")
print(f"   - 插值填充: {interpolated_count}个观测值")

print(f"\n3. 最终数据:")
print(f"   - 观测值数量: {len(df_main_with_fdi)}")
print(f"   - 城市数量: {df_main_with_fdi['city_name'].nunique()}")
print(f"   - FDI开放度缺失率: {fdi_missing_rate:.2%}")

print(f"\n4. FDI开放度统计（描述性）:")
if not df_main_with_fdi['fdi_openness'].isna().all():
    stats = df_main_with_fdi['fdi_openness'].describe()
    print(f"   - 均值: {stats['mean']:.4f}")
    print(f"   - 标准差: {stats['std']:.4f}")
    print(f"   - 最小值: {stats['min']:.4f}")
    print(f"   - 中位数: {stats['50%']:.4f}")
    print(f"   - 最大值: {stats['max']:.4f}")

print("\n[OK] FDI数据处理完成！")
print("=" * 80)
