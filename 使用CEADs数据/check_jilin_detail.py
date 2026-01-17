"""
详细检查吉林相关城市
"""
import pandas as pd

df = pd.read_excel('1997-2019年290个中国城市碳排放清单 (1).xlsx', sheet_name='emission vector')
jilin = df[df['city'].str.contains('吉林', na=False)]

print("包含'吉林'的详细城市（已排序）:")
for city in sorted(jilin['city'].unique()):
    print(f"  {city}")

# 测试当前逻辑对这些城市的影响
def create_match_key_from_ceads(city_name):
    """当前使用的匹配键函数"""
    if pd.isna(city_name):
        return None

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

    original_after_suffix = city_str  # 记录去后缀后的结果

    # 再去除省份前缀
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

print("\n测试当前逻辑:")
print("-" * 80)
for city in sorted(jilin['city'].unique()):
    match_key = create_match_key_from_ceads(city)
    print(f"  {city:20s} -> {match_key}")

# 检查是否有空字符串
print("\n检查是否有空的匹配键:")
empty_keys = []
for city in df['city'].unique():
    match_key = create_match_key_from_ceads(city)
    if match_key == '' or match_key is None:
        empty_keys.append(city)

if empty_keys:
    print(f"发现 {len(empty_keys)} 个空匹配键:")
    for city in empty_keys[:20]:
        print(f"  {city}")
else:
    print("[OK] 没有发现空匹配键")
