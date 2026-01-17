"""
验证step2b_clean_ceads_fixed.py的修复是否有效
"""
import pandas as pd

print("=" * 80)
print("验证CEADs清洗结果")
print("=" * 80)

# 读取清洗后的数据
df = pd.read_excel('CEADs_2007-2019_清洗后_修正版.xlsx')

print(f"\n总观测数: {len(df)}")
print(f"唯一城市数: {df['city_name_ceads'].nunique()}")

# 检查空匹配键
empty_keys = df[df['match_key'] == '']
print(f"\n空匹配键数量: {len(empty_keys)}")

if len(empty_keys) > 0:
    print("[WARNING] 发现空匹配键的城市:")
    print(empty_keys['city_name_ceads'].unique())
else:
    print("[OK] 没有空匹配键!")

# 检查关键城市
key_cities = ['吉林市', '北京市', '上海市']
print("\n关键城市匹配结果:")
print(df[df['city_name_ceads'].isin(key_cities)][['city_name_ceads', 'match_key']].drop_duplicates())

# 统计匹配键分布
print("\n匹配键分布(前20个):")
match_key_counts = df['match_key'].value_counts().head(20)
print(match_key_counts)

print("\n=" * 80)
print("验证完成!")
print("=" * 80)
