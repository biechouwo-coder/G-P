"""
检查潜在的吉林市Bug
"""
import pandas as pd

# 读取原始CEADs数据
df = pd.read_excel('1997-2019年290个中国城市碳排放清单 (1).xlsx', sheet_name='emission vector')

# 检查包含"吉林"的城市
jilin_cities = df[df['city'].str.contains('吉林', na=False)]['city'].unique()
print("包含'吉林'的城市:")
for city in jilin_cities:
    print(f"  {city}")

print(f"\n总数: {len(jilin_cities)}")

# 检查包含"海南"的城市
hainan_cities = df[df['city'].str.contains('海南', na=False)]['city'].unique()
print("\n包含'海南'的城市:")
for city in hainan_cities:
    print(f"  {city}")

print(f"\n总数: {len(hainan_cities)}")

# 检查包含"省"的城市
province_suffix = df[df['city'].str.contains('省', na=False)]['city'].unique()
print(f"\n包含'省'的城市数量: {len(province_suffix)}")
if len(province_suffix) > 0:
    print("前10个示例:")
    for city in province_suffix[:10]:
        print(f"  {city}")
