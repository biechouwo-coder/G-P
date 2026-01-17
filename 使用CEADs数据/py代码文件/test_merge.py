"""
测试合并逻辑
"""
import pandas as pd

def create_match_key(city_name):
    """从城市名中提取匹配键"""
    if pd.isna(city_name):
        return None
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

# 读取数据
df_master = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI_修正pop_density_添加金融发展水平.xlsx')
df_master = df_master[(df_master['year'] >= 2007) & (df_master['year'] <= 2019)].copy()
df_master['match_key'] = df_master['city_name'].apply(create_match_key)

df_ceads = pd.read_excel('CEADs_2007-2019_清洗后.xlsx')

print("=" * 80)
print("检查匹配键交集")
print("=" * 80)

master_keys = set(df_master['match_key'].dropna().unique())
ceads_keys = set(df_ceads['match_key'].dropna().unique())

print(f"\n主数据集匹配键数量: {len(master_keys)}")
print(f"CEADs匹配键数量: {len(ceads_keys)}")
print(f"交集数量: {len(master_keys & ceads_keys)}")

print(f"\n交集（前30个）:")
common_keys = list(master_keys & ceads_keys)[:30]
for key in common_keys:
    # 找到对应的城市名
    master_city = df_master[df_master['match_key'] == key]['city_name'].values[0]
    ceads_city = df_ceads[df_ceads['match_key'] == key]['city_name_ceads'].values[0]
    print(f"  {key:20s} <- 主:{master_city}, CEADs:{ceads_city}")

print(f"\n仅在主数据集中的匹配键（前20个）:")
only_master = list(master_keys - ceads_keys)[:20]
for key in only_master:
    master_city = df_master[df_master['match_key'] == key]['city_name'].values[0]
    print(f"  {key:20s} <- {master_city}")

print(f"\n仅在CEADs中的匹配键（前20个）:")
only_ceads = list(ceads_keys - master_keys)[:20]
for key in only_ceads:
    ceads_city = df_ceads[df_ceads['match_key'] == key]['city_name_ceads'].values[0]
    print(f"  {key:20s} <- {ceads_city}")

# 测试合并
print("\n" + "=" * 80)
print("测试合并")
print("=" * 80)

df_test = pd.merge(
    df_master[['year', 'city_name', 'match_key']],
    df_ceads[['year', 'match_key', 'emission_million_tons']],
    on=['year', 'match_key'],
    how='left'
)

matched_count = df_test['emission_million_tons'].notnull().sum()
print(f"\n合并后，有碳排放数据的观测数: {matched_count}")
print(f"总观测数: {len(df_test)}")
print(f"匹配率: {matched_count / len(df_test) * 100:.2f}%")

# 检查哪些匹配键在交集但合并失败
print("\n检查交集匹配键的合并情况:")
for key in list(master_keys & ceads_keys)[:10]:
    master_rows = df_master[df_master['match_key'] == key]
    ceads_rows = df_ceads[df_ceads['match_key'] == key]
    test_rows = df_test[df_test['match_key'] == key]

    master_city = master_rows['city_name'].values[0]
    merged_count = test_rows['emission_million_tons'].notnull().sum()
    print(f"  {key:15s} 主:{len(master_rows)}行, CEADs:{len(ceads_rows)}行, 合并成功:{merged_count}行, 城市名:{master_city}")
