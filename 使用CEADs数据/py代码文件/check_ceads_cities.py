"""
检查CEADs原始数据中是否包含吉林市、北京、上海
"""
import pandas as pd

df = pd.read_excel('1997-2019年290个中国城市碳排放清单 (1).xlsx', sheet_name='emission vector')

print(f"CEADs原始数据中的城市数量: {df['city'].nunique()}")

print("\n查找吉林市、北京、上海:")
cities_to_check = ['吉林市', '北京市', '上海市', '吉林', '北京', '上海',
                   '四川吉林', '吉林省吉林市']

for city in cities_to_check:
    if city in df['city'].values:
        print(f"  找到: {city}")
        # 显示该城市的数据
        city_data = df[df['city'] == city]
        print(f"    年份范围: {city_data['year'].min()} - {city_data['year'].max()}")
        print(f"    观测数: {len(city_data)}")
    else:
        print(f"  未找到: {city}")

# 列出所有包含"吉林"的城市
print("\n所有包含'吉林'的城市:")
all_cities = df['city'].unique()
jinlin_cities = [c for c in all_cities if '吉林' in str(c)]
for city in jinlin_cities:
    print(f"  - {city}")
