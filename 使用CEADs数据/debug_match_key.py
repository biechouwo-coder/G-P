"""
检查CEADs中是否有深圳
"""
import pandas as pd

df_ceads = pd.read_excel('CEADs_2007-2019_清洗后.xlsx')

# 查找包含"深"字的城市
shenzhen_cities = df_ceads[df_ceads['city_name_ceads'].str.contains('深', na=False)]
print("包含'深'字的城市:")
print(shenzhen_cities[['city_name_ceads', 'match_key']].drop_duplicates())

# 查找包含"深圳"的城市
print("\n包含'深圳'的城市:")
shenzhen_cities2 = df_ceads[df_ceads['match_key'] == '深圳']
print(shenzhen_cities2[['city_name_ceads', 'match_key']].drop_duplicates())

# 检查所有城市中是否有类似深圳的
print("\n所有以'深'开头的match_key:")
all_shen = df_ceads[df_ceads['match_key'].str.startswith('深', na=False)]
print(all_shen[['city_name_ceads', 'match_key']].drop_duplicates())

# 统计CEADs中有多少个不同的城市
print(f"\nCEADs总共有 {df_ceads['city_name_ceads'].nunique()} 个不同的城市")
print(f"CEADs总共有 {df_ceads['match_key'].nunique()} 个不同的匹配键")
