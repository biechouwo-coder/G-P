"""
第三步：数据合并（修正版）
"""
import pandas as pd
import numpy as np

print("=" * 80)
print("第三步：合并主数据集与CEADs、GDP数据（修正版）")
print("=" * 80)

def create_match_key_simple(city_name):
    """从城市名中提取匹配键（只去后缀）"""
    if pd.isna(city_name):
        return np.nan
    city_str = str(city_name).strip()
    suffixes = ['市', '盟', '地区', '特区',
                '哈萨克自治州', '蒙古自治州', '藏族自治州',
                '彝族自治州', '白族自治州', '傣族自治州',
                '壮族自治州', '苗族侗族自治州', '侗族自治州',
                '土家族苗族自治州', '朝鲜族自治州', '回族自治州',
                '维吾尔自治州', '自治州', '州']
    for suffix in sorted(suffixes, key=len, reverse=True):
        if city_str.endswith(suffix):
            city_str = city_str[:-len(suffix)]
            break
    return city_str

# 1. 读取主数据集（仅保留2007-2019年）
df_master = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI_修正pop_density_添加金融发展水平.xlsx')
print(f"\n原始主数据集: {df_master.shape[0]} 行观测")

# 截断至2007-2019年
df_master = df_master[
    (df_master['year'] >= 2007) &
    (df_master['year'] <= 2019)
].copy()
print(f"截断后主数据集: {df_master.shape[0]} 行观测")
print(f"年份范围: {df_master['year'].min()} - {df_master['year'].max()}")
print(f"城市数量: {df_master['city_name'].nunique()}")

# 构造匹配键
df_master['match_key'] = df_master['city_name'].apply(create_match_key_simple)

# 2. 读取清洗后的CEADs数据（修正版）
df_ceads = pd.read_excel('CEADs_2007-2019_清洗后_修正版.xlsx')
print(f"\nCEADs数据: {df_ceads.shape[0]} 行观测")
print(f"年份范围: {df_ceads['year'].min()} - {df_ceads['year'].max()}")
print(f"城市数量: {df_ceads['city_name_ceads'].nunique()}")

# 3. 读取清洗后的GDP数据（修正版）
df_gdp = pd.read_excel('实际GDP_2007-2019_清洗后_修正版.xlsx')
print(f"\n实际GDP数据: {df_gdp.shape[0]} 行观测")
print(f"年份范围: {df_gdp['year'].min()} - {df_gdp['year'].max()}")
print(f"城市数量: {df_gdp['city_name_gdp'].nunique()}")

# 4. 检查匹配键交集
print("\n" + "=" * 80)
print("匹配键交集检查")
print("=" * 80)

master_keys = set(df_master['match_key'].dropna().unique())
ceads_keys = set(df_ceads['match_key'].dropna().unique())

print(f"\n主数据集匹配键数量: {len(master_keys)}")
print(f"CEADs匹配键数量: {len(ceads_keys)}")
print(f"交集数量: {len(master_keys & ceads_keys)}")
print(f"交集比例: {len(master_keys & ceads_keys) / len(master_keys) * 100:.2f}%")

# 5. 第一次合并：主数据集 + CEADs
print("\n" + "-" * 80)
print("第一次合并：主数据集 + CEADs")
print("-" * 80)

df_merged = pd.merge(
    df_master,
    df_ceads[['year', 'match_key', 'emission_million_tons']],
    on=['year', 'match_key'],
    how='left'
)

print(f"合并后观测数: {df_merged.shape[0]}")
print(f"碳排放数据缺失数: {df_merged['emission_million_tons'].isnull().sum()}")
print(f"碳排放数据匹配率: {(1 - df_merged['emission_million_tons'].isnull().sum() / len(df_merged)) * 100:.2f}%")

# 6. 第二次合并：合并后的数据 + 实际GDP
print("\n" + "-" * 80)
print("第二次合并：合并后的数据 + 实际GDP")
print("-" * 80)

df_merged = pd.merge(
    df_merged,
    df_gdp[['year', 'match_key', 'real_gdp_100m_yuan']],
    on=['year', 'match_key'],
    how='left'
)

print(f"合并后观测数: {df_merged.shape[0]}")
print(f"实际GDP数据缺失数: {df_merged['real_gdp_100m_yuan'].isnull().sum()}")
print(f"实际GDP数据匹配率: {(1 - df_merged['real_gdp_100m_yuan'].isnull().sum() / len(df_merged)) * 100:.2f}%")

# 7. 检查匹配情况
print("\n" + "=" * 80)
print("匹配情况总结")
print("=" * 80)

# 检查两个核心变量都有值的观测数
valid_obs = df_merged[
    df_merged['emission_million_tons'].notnull() &
    df_merged['real_gdp_100m_yuan'].notnull()
]

print(f"\n同时有碳排放和GDP数据的观测数: {len(valid_obs)}")
print(f"占总观测数的比例: {len(valid_obs) / len(df_merged) * 100:.2f}%")
print(f"涉及城市数量: {valid_obs['city_name'].nunique()}")

# 检查未匹配的城市
print("\n未匹配碳排放的城市数量:", df_merged[df_merged['emission_million_tons'].isnull()]['city_name'].nunique())
print("未匹配GDP的城市数量:", df_merged[df_merged['real_gdp_100m_yuan'].isnull()]['city_name'].nunique())

# 8. 保存合并后的数据
output_file = '合并后数据集_2007-2019_修正版.xlsx'
df_merged.to_excel(output_file, index=False)
print(f"\n[OK] 合并后的数据已保存: {output_file}")

print("\n" + "=" * 80)
print("数据合并完成！")
print("=" * 80)
