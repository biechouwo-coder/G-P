"""
构建DID政策变量

三批低碳试点城市：
- 第一批（2010年）：5省 + 8市
- 第二批（2013年）：1省 + 26市
- 第三批（2017年）：45个城市/地区

处理原则：
1. 如果城市多次出现，以最早年份为准
2. 省级试点：该省所有地级市都算试点城市
3. DID = 1 当且仅当 当前年份 >= 该城市的试点开始年份
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

print("=" * 100)
print("低碳试点城市DID变量构建")
print("=" * 100)
print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 读取最终数据集
INPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_最终版.xlsx")
OUTPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_最终版_含DID.xlsx")

df = pd.read_excel(INPUT_FILE)
print(f"\n数据规模: {df.shape}")
print(f"  城市数: {df['city_name'].nunique()}")

# ============ 定义试点名单 ============

print("\n" + "=" * 100)
print("步骤1: 定义三批低碳试点名单")
print("=" * 100)

# 第一批（2010年）
# 试点省份：广东(44)、辽宁(21)、湖北(42)、陕西(61)、云南(53)
# 试点城市：天津、重庆、深圳、厦门、杭州、南昌、贵阳、保定
batch_1_provinces = [44, 21, 42, 61, 53]  # 省级代码前两位
batch_1_cities = [
    '天津市', '重庆市', '深圳市', '厦门市',
    '杭州市', '南昌市', '贵阳市', '保定市'
]

# 第二批（2013年）
# 试点省份：海南(46)
# 试点城市列表
batch_2_province = [46]  # 海南
batch_2_cities = [
    '北京市', '上海市', '石家庄市', '秦皇岛市', '晋城市', '呼伦贝尔市',
    '吉林市', '大兴安岭地区', '苏州市', '淮安市', '镇江市', '宁波市',
    '温州市', '池州市', '南平市', '景德镇市', '赣州市', '青岛市',
    '济源市', '武汉市', '广州市', '桂林市', '广元市', '遵义市',
    '昆明市', '延安市', '金昌市', '乌鲁木齐市'
]

# 第三批（2017年）
# 仅城市，无省级试点
batch_3_cities = [
    # 内蒙古 (1)
    '乌海市',
    # 辽宁 (3)
    '沈阳市', '大连市', '朝阳市',
    # 黑龙江 (1)
    '逊克县',
    # 江苏 (3)
    '南京市', '常州市', '镇江市',
    # 浙江 (3)
    '嘉兴市', '金华市', '衢州市',
    # 安徽 (6)
    '合肥市', '淮北市', '黄山市', '六安市', '宣城市', '池州市',
    # 福建 (2)
    '三明市', '南平市',
    # 江西 (3)
    '吉安市', '抚州市', '共青城市',
    # 山东 (3)
    '济南市', '烟台市', '潍坊市',
    # 播南 (1)
    '济源市',
    # 湖南 (4)
    '长沙市', '株洲市', '湘潭市', '郴州市',
    # 广东 (1)
    '中山市',
    # 广西 (2)
    '柳州市', '桂林市',
    # 海南 (2)
    '三亚市', '琼中黎族苗族自治县',
    # 四川 (2)
    '成都市', '广元市',
    # 云南 (2)
    '玉溪市', '普洱市思茅区',
    # 陕西 (2)
    '延安市', '安康市',
    # 甘肃 (3)
    '兰州市', '金昌市', '敦煌市',
    # 青海 (1)
    '西宁市',
    # 宁夏 (2)
    '银川市', '吴忠市',
    # 新疆 (2)
    '乌鲁木齐市', '昌吉市'
]

print("\n第一批试点（2010年）:")
print(f"  试点省份（5个）: 广东、辽宁、湖北、陕西、云南")
print(f"  试点城市（8个）: {', '.join(batch_1_cities)}")

print("\n第二批试点（2013年）:")
print(f"  试点省份（1个）: 海南")
print(f"  试点城市（26个）: {', '.join(batch_2_cities[:10])}...")

print("\n第三批试点（2017年）:")
print(f"  试点城市（45个）: {', '.join(batch_3_cities[:10])}...")

# ============ 构建city_to_pilot_year映射 ============

print("\n" + "=" * 100)
print("步骤2: 构建城市→试点年份映射")
print("=" * 100)

city_to_pilot_year = {}

# 处理第一批（2010年）
for city_name in batch_1_cities:
    if city_name not in city_to_pilot_year:
        city_to_pilot_year[city_name] = 2010

# 处理第二批（2013年）
for city_name in batch_2_cities:
    if city_name not in city_to_pilot_year:
        city_to_pilot_year[city_name] = 2013

# 处理第三批（2017年）
for city_name in batch_3_cities:
    if city_name not in city_to_pilot_year:
        city_to_pilot_year[city_name] = 2017

print(f"\n明确列出的试点城市数: {len(city_to_pilot_year)}")

# 处理省级试点（该省所有地级市）
print("\n处理省级试点覆盖...")

# 提取所有城市的省级代码
df['province_code'] = df['city_code'].astype(str).str[:2].astype(int)

# 第一批省级试点（2010年）
for province_code in batch_1_provinces:
    cities_in_province = df[df['province_code'] == province_code]['city_name'].unique()
    for city_name in cities_in_province:
        # 仅当城市还未被列在明确名单中时，才添加省级试点
        if city_name not in city_to_pilot_year:
            city_to_pilot_year[city_name] = 2010

    province_name = {
        44: '广东', 21: '辽宁', 42: '湖北', 61: '陕西', 53: '云南'
    }[province_code]
    print(f"  {province_name}省（{province_code}）: {len(cities_in_province)}个城市")

# 第二批省级试点（2013年）
for province_code in batch_2_province:
    cities_in_province = df[df['province_code'] == province_code]['city_name'].unique()
    for city_name in cities_in_province:
        if city_name not in city_to_pilot_year:
            city_to_pilot_year[city_name] = 2013

    print(f"  海南省（{province_code}）: {len(cities_in_province)}个城市")

print(f"\n试点城市总数（含省级试点覆盖）: {len(city_to_pilot_year)}")

# ============ 构建DID变量 ============

print("\n" + "=" * 100)
print("步骤3: 构建DID变量")
print("=" * 100)

# 映射试点年份到数据集
df['pilot_year'] = df['city_name'].map(city_to_pilot_year)

# 构建treat变量（是否为试点城市）
df['treat'] = df['pilot_year'].notna().astype(int)

# 构建post变量（是否在政策实施期）
df['post'] = df['year'] >= df['pilot_year']
df['post'] = df['post'].fillna(False).astype(int)

# 构建DID变量
df['did'] = df['treat'] * df['post']

print("\nDID变量构建完成:")
print(f"  处理组城市数: {df['treat'].sum() / df['year'].nunique():.0f}")
print(f"  对照组城市数: {df['treat'].nunique() - df['treat'].sum() / df['year'].nunique():.0f}")
print(f"  总观测数: {len(df)}")
print(f"  DID=1的观测数: {df['did'].sum()} ({df['did'].sum()/len(df)*100:.2f}%)")

# ============ 验证DID变量 ============

print("\n" + "=" * 100)
print("步骤4: 验证DID变量")
print("=" * 100)

# 统计各批次试点城市数
batch_counts = df[df['treat'] == 1].groupby('pilot_year')['city_name'].nunique()
print("\n各批次试点城市数:")
for year, count in batch_counts.items():
    if year == 2010:
        print(f"  第一批（2010年）: {count}个城市")
    elif year == 2013:
        print(f"  第二批（2013年）: {count}个城市")
    elif year == 2017:
        print(f"  第三批（2017年）: {count}个城市")

# 检查DID变量随时间的变化
print("\nDID=1的观测数随时间分布:")
did_by_year = df[df['did'] == 1].groupby('year').size()
for year, count in did_by_year.items():
    print(f"  {year}年: {count}个城市DID=1 ({count/df['city_name'].nunique()*100:.1f}%)")

# 随机抽样验证
print("\n随机抽样验证（10个城市）:")
sample_cities = df['city_name'].unique()[:10]
for city in sample_cities:
    city_data = df[df['city_name'] == city].sort_values('year')
    pilot_year = city_data['pilot_year'].iloc[0]
    is_treat = city_data['treat'].iloc[0]
    did_1_years = city_data[city_data['did'] == 1]['year'].tolist()

    status = f"试点城市（{int(pilot_year)}年起）" if is_treat else "非试点城市"
    did_info = f"DID=1年份: {did_1_years[:5]}" if len(did_1_years) > 0 else "DID始终为0"
    if len(did_1_years) > 5:
        did_info += "..."

    print(f"  {city:12s}: {status:20s} {did_info}")

# ============ 保存数据 ============

print("\n" + "=" * 100)
print("步骤5: 保存数据")
print("=" * 100)

# 删除临时变量
df = df.drop(columns=['province_code'])

# 保存数据
df.to_excel(OUTPUT_FILE, index=False)
print(f"\n数据已保存到: {OUTPUT_FILE}")
print(f"文件大小: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")

# 保存试点城市名单
PILOT_LIST_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\试点城市名单.xlsx")
df_pilot = pd.DataFrame([
    {'city_name': city, 'pilot_year': year}
    for city, year in sorted(city_to_pilot_year.items(), key=lambda x: x[1])
])
df_pilot.to_excel(PILOT_LIST_FILE, index=False)
print(f"试点城市名单已保存到: {PILOT_LIST_FILE}")

# ============ 总结 ============

print("\n" + "=" * 100)
print("DID变量构建总结")
print("=" * 100)

print(f"""
数据集: {OUTPUT_FILE.name}
规模: {df.shape[0]}个观测 x {df.shape[1]}个变量

变量说明:
- treat: 是否为试点城市（1=是，0=否）
- pilot_year: 试点开始年份（非试点城市为NaN）
- post: 是否在政策实施期（1=是，0=否）
- did: DID政策变量 = treat x post

试点城市分布:
- 第一批（2010年）: {batch_counts.get(2010, 0)}个城市（含省级试点覆盖）
- 第二批（2013年）: {batch_counts.get(2013, 0)}个城市（含省级试点覆盖）
- 第三批（2017年）: {batch_counts.get(2017, 0)}个城市
- 总计: {df['treat'].sum() / df['year'].nunique():.0f}个试点城市

处理组与对照组:
- 处理组: {df['treat'].sum() / df['year'].nunique():.0f}个城市
- 对照组: {df['treat'].nunique() - df['treat'].sum() / df['year'].nunique():.0f}个城市

DID变量统计:
- DID=1的观测: {df['did'].sum()}个 ({df['did'].sum()/len(df)*100:.2f}%)
- DID=0的观测: {len(df) - df['did'].sum()}个 ({(1-df['did'].sum()/len(df))*100:.2f}%)

下一步工作:
- 基准回归: CEI_it = α₀ + β₁·DID_it + β₂·ln(pop_den) + 控制变量 + 城市FE + 年份FE + ε_it
- 稳健性检验: 平行趋势、PSM-DID、安慰剂检验
""")

print("\n" + "=" * 100)
print("DID变量构建完成！")
print("=" * 100)
