"""
第一步和第二步：CEADs数据清洗与实际GDP数据准备（修正版）
"""
import pandas as pd
import numpy as np

print("=" * 80)
print("第一步：清洗CEADs数据（修正版）")
print("=" * 80)

# 1. 读取CEADs数据
ceads_file = '1997-2019年290个中国城市碳排放清单 (1).xlsx'
df_ceads = pd.read_excel(ceads_file, sheet_name='emission vector')

print(f"\n原始CEADs数据: {df_ceads.shape[0]} 行观测")
print(f"年份范围: {df_ceads['year'].min()} - {df_ceads['year'].max()}")
print(f"城市数量: {df_ceads['city'].nunique()}")

# 2. 提取核心列并重命名
df_ceads_clean = df_ceads[['city', 'year', 'emission']].copy()
df_ceads_clean.columns = ['city_name_ceads', 'year', 'emission_million_tons']

# 3. 时间截断：保留2007-2019年
df_ceads_clean = df_ceads_clean[
    (df_ceads_clean['year'] >= 2007) &
    (df_ceads_clean['year'] <= 2019)
].copy()

print(f"\n截断至2007-2019年后: {df_ceads_clean.shape[0]} 行观测")
print(f"年份范围: {df_ceads_clean['year'].min()} - {df_ceads_clean['year'].max()}")

# 4. 构造匹配键（去除省份前缀和后缀）
def create_match_key_from_ceads(city_name):
    """
    从CEADs城市名中提取匹配键
    例如："四川成都" -> "成都", "北京市" -> "北京"
    """
    if pd.isna(city_name):
        return np.nan

    city_str = str(city_name).strip()

    # 先去除后缀
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

    # 再去除省份前缀
    # 常见省份名
    provinces = ['北京', '天津', '上海', '重庆',
                 '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江',
                 '江苏', '浙江', '安徽', '福建', '江西', '山东',
                 '河南', '湖北', '湖南', '广东', '广西', '海南',
                 '四川', '贵州', '云南', '西藏', '陕西', '甘肃',
                 '青海', '宁夏', '新疆',
                 '黑龙江', '香港', '澳门', '台湾']

    for province in sorted(provinces, key=len, reverse=True):
        if city_str.startswith(province):
            city_str = city_str[len(province):]
            break

    return city_str

df_ceads_clean['match_key'] = df_ceads_clean['city_name_ceads'].apply(create_match_key_from_ceads)

print("\nCEADs城市名示例（前30个）:")
print(df_ceads_clean[['city_name_ceads', 'match_key']].drop_duplicates().head(30))

# 5. 保存清洗后的CEADs数据
ceads_output = 'CEADs_2007-2019_清洗后_修正版.xlsx'
df_ceads_clean.to_excel(ceads_output, index=False)
print(f"\n[OK] CEADs清洗后数据已保存: {ceads_output}")

print("\n" + "=" * 80)
print("第二步：准备实际GDP数据")
print("=" * 80)

# 1. 读取实际GDP数据
gdp_file = '../原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx'
df_gdp_raw = pd.read_excel(gdp_file)

print(f"\n原始GDP数据形状: {df_gdp_raw.shape}")

# 2. 根据列位置提取数据
df_gdp = df_gdp_raw.iloc[:, [2, 1, 3, 5]].copy()
df_gdp.columns = ['year', 'city_name_gdp', 'real_gdp_100m_yuan', 'gdp_deflator']

# 3. 转换数据类型
df_gdp['year'] = pd.to_numeric(df_gdp['year'], errors='coerce')
df_gdp['real_gdp_100m_yuan'] = pd.to_numeric(df_gdp['real_gdp_100m_yuan'], errors='coerce')
df_gdp['gdp_deflator'] = pd.to_numeric(df_gdp['gdp_deflator'], errors='coerce')

# 4. 时间截断：保留2007-2019年
df_gdp = df_gdp[
    (df_gdp['year'] >= 2007) &
    (df_gdp['year'] <= 2019)
].copy()

print(f"截断至2007-2019年后: {df_gdp.shape[0]} 行观测")
print(f"年份范围: {df_gdp['year'].min()} - {df_gdp['year'].max()}")

# 5. 构造匹配键（去除后缀）
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

df_gdp['match_key'] = df_gdp['city_name_gdp'].apply(create_match_key_simple)

print("\nGDP城市名示例（前20个）:")
print(df_gdp[['city_name_gdp', 'match_key']].drop_duplicates().head(20))

# 6. 保存清洗后的GDP数据
gdp_output = '实际GDP_2007-2019_清洗后_修正版.xlsx'
df_gdp.to_excel(gdp_output, index=False)
print(f"\n[OK] 实际GDP清洗后数据已保存: {gdp_output}")

print("\n" + "=" * 80)
print("数据清洗完成！")
print("=" * 80)
