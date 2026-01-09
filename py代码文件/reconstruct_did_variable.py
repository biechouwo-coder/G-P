"""
重构DID政策变量 - 修复版

核心改进:
1. 修复省市重叠导致的年份滞后问题（取最早年份原则）
2. 修正第二批试点启动年份（2012而非2013）
3. 补全第三批遗漏的西部城市（拉萨、伊宁、和田）
4. 正确处理区县级试点与地级市数据的匹配

三批低碳试点城市：
- 第一批（2010年）：5省 + 8市
- 第二批（2012年）：1省 + 26市（年份修正为2012）
- 第三批（2017年）：45+个城市/地区（补全遗漏）

处理原则：
1. **取最早年份原则**：如果城市多次出现，以最早年份为准
2. **优先处理省级试点**：省级试点优先赋值（2010年权重最高）
3. **后处理城市名单**：明确列出的城市只有在未赋值时才赋值
4. DID = 1 当且仅当 当前年份 >= 该城市的试点开始年份
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

print("=" * 100)
print("低碳试点城市DID变量重构 - 修复版")
print("=" * 100)
print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 读取最终数据集
INPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_最终回归版.xlsx")
OUTPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_最终回归版.xlsx")

df = pd.read_excel(INPUT_FILE)
print(f"\n数据规模: {df.shape}")
print(f"  城市数: {df['city_name'].nunique()}")

# 删除旧的DID变量（如果存在）
cols_to_drop = ['treat', 'post', 'did', 'pilot_year']
for col in cols_to_drop:
    if col in df.columns:
        df = df.drop(columns=[col])
        print(f"  [INFO] 删除旧变量: {col}")

# ============ 定义试点名单（修正版） ============

print("\n" + "=" * 100)
print("步骤1: 定义三批低碳试点名单（修正版）")
print("=" * 100)

# 第一批（2010年）- 7月启动
# 试点省份：广东(44)、辽宁(21)、湖北(42)、陕西(61)、云南(53)
# 试点城市：天津、重庆、深圳、厦门、杭州、南昌、贵阳、保定
batch_1_provinces = [44, 21, 42, 61, 53]  # 省级代码前两位
batch_1_cities = [
    '天津市', '重庆市', '深圳市', '厦门市',
    '杭州市', '南昌市', '贵阳市', '保定市'
]

# 第二批（2012年）- 4月启动（年份修正：2013 -> 2012）
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

# 第三批（2017年）- 补全遗漏城市
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
    # 河南 (1)
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
    '玉溪市', '普洱市',  # 修正：删除"思茅区"，保留地级市
    # 陕西 (2)
    '延安市', '安康市',
    # 甘肃 (3)
    '兰州市', '金昌市', '敦煌市',
    # 青海 (1)
    '西宁市',
    # 宁夏 (2)
    '银川市', '吴忠市',
    # 新疆 (5) - 补全遗漏城市
    '乌鲁木齐市', '昌吉市', '拉萨市', '伊宁市', '和田市'
]

print("\n[修正1] 第一批试点（2010年）:")
print(f"  试点省份（5个）: 广东、辽宁、湖北、陕西、云南")
print(f"  试点城市（8个）: {', '.join(batch_1_cities)}")

print("\n[修正2] 第二批试点（2012年，年份修正）:")
print(f"  试点省份（1个）: 海南")
print(f"  试点城市（26个）: {', '.join(batch_2_cities[:10])}...")

print("\n[修正3] 第三批试点（2017年，补全遗漏）:")
print(f"  试点城市（48个，含新增拉萨、伊宁、和田）: {', '.join(batch_3_cities[:10])}...")

# ============ 构建city_to_pilot_year映射（取最早年份原则） ============

print("\n" + "=" * 100)
print("步骤2: 构建城市→试点年份映射（取最早年份原则）")
print("=" * 100)

city_to_pilot_year = {}

# 提取所有城市的省级代码
df['province_code'] = df['city_code'].astype(str).str[:2].astype(int)

# 【关键修改】优先处理省级试点（确保2010年优先赋值）
print("\n[优先处理] 省级试点覆盖...")

# 第一批省级试点（2010年）
batch_1_province_names = {
    44: '广东', 21: '辽宁', 42: '湖北', 61: '陕西', 53: '云南'
}
for province_code in batch_1_provinces:
    cities_in_province = df[df['province_code'] == province_code]['city_name'].unique()
    for city_name in cities_in_province:
        # 【核心逻辑】直接赋值2010，不检查是否已存在
        # 因为省级优先处理，所以所有省会城市（武汉、广州、昆明等）都会正确标记为2010
        city_to_pilot_year[city_name] = 2010

    province_name = batch_1_province_names[province_code]
    print(f"  {province_name}省（{province_code}）: {len(cities_in_province)}个城市")

print(f"  -> 第一批省级试点后: {len(city_to_pilot_year)}个城市已赋值")

# 第二批省级试点（2012年）
for province_code in batch_2_province:
    cities_in_province = df[df['province_code'] == province_code]['city_name'].unique()
    for city_name in cities_in_province:
        # 【核心逻辑】只有未赋值的城市才赋2012
        # 这样避免覆盖第一批的2010年赋值
        if city_name not in city_to_pilot_year:
            city_to_pilot_year[city_name] = 2012

    print(f"  海南省（{province_code}）: {len(cities_in_province)}个城市")

print(f"  -> 第二批省级试点后: {len(city_to_pilot_year)}个城市已赋值")

# 【后处理】明确列出的城市名单
print("\n[后处理] 明确列出的试点城市...")

# 处理第一批明确城市（2010年）
for city_name in batch_1_cities:
    # 【核心逻辑】只赋值给未赋值的城市
    # 已被省级试点覆盖的城市（如广州、武汉）保持2010不变
    if city_name not in city_to_pilot_year:
        city_to_pilot_year[city_name] = 2010

print(f"  第一批城市名单后: {len(city_to_pilot_year)}个城市已赋值")

# 处理第二批明确城市（2012年）
for city_name in batch_2_cities:
    # 【核心逻辑】只赋值给未赋值的城市
    # 武汉、广州、昆明已在第一批省级试点中赋值2010，此处跳过
    if city_name not in city_to_pilot_year:
        city_to_pilot_year[city_name] = 2012

print(f"  第二批城市名单后: {len(city_to_pilot_year)}个城市已赋值")

# 处理第三批明确城市（2017年）
# 修正区县级名称
city_name_mapping = {
    '普洱市思茅区': '普洱市',  # 区县级 -> 地级市
    '琼中黎族苗族自治县': '琼中黎族苗族自治县',  # 保持不变（如果数据中存在）
    '大兴安岭地区': '大兴安岭地区',  # 保持不变
}

for city_name in batch_3_cities:
    # 处理名称映射
    mapped_name = city_name_mapping.get(city_name, city_name)

    # 【核心逻辑】只赋值给未赋值的城市
    if mapped_name not in city_to_pilot_year:
        city_to_pilot_year[mapped_name] = 2017

print(f"  第三批城市名单后: {len(city_to_pilot_year)}个城市已赋值")

print(f"\n试点城市总数: {len(city_to_pilot_year)}")

# ============ 验证关键城市是否正确 ============

print("\n[验证] 关键城市试点年份检查:")
test_cities = ['武汉市', '广州市', '昆明市', '北京市', '上海市', '拉萨市', '伊宁市', '和田市']
for city in test_cities:
    if city in city_to_pilot_year:
        print(f"  {city}: {city_to_pilot_year[city]}年")
    else:
        print(f"  {city}: 未找到")

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
print(f"  处理组城市数: {df[df['treat']==1]['city_name'].nunique()}")
print(f"  对照组城市数: {df['city_name'].nunique() - df[df['treat']==1]['city_name'].nunique()}")
print(f"  总观测数: {len(df)}")
print(f"  DID=1的观测数: {df['did'].sum()} ({df['did'].sum()/len(df)*100:.2f}%)")

# ============ 验证DID变量 ============

print("\n" + "=" * 100)
print("步骤4: 验证DID变量")
print("=" * 100)

# 统计各批次试点城市数
batch_counts = df[df['treat'] == 1].groupby('pilot_year')['city_name'].nunique()
print("\n各批次试点城市数:")
for year in [2010, 2012, 2017]:
    count = batch_counts.get(year, 0)
    if year == 2010:
        print(f"  第一批（2010年）: {count}个城市")
    elif year == 2012:
        print(f"  第二批（2012年，修正后）: {count}个城市")
    elif year == 2017:
        print(f"  第三批（2017年，补全后）: {count}个城市")

# 检查DID变量随时间的变化
print("\nDID=1的观测数随时间分布:")
did_by_year = df[df['did'] == 1].groupby('year').size()
for year in [2007, 2010, 2012, 2017, 2023]:
    if year in did_by_year.index:
        count = did_by_year[year]
        print(f"  {year}年: {count}个城市DID=1 ({count/df['city_name'].nunique()*100:.1f}%)")

# 验证关键城市
print("\n[再次验证] 关键城市DID变量:")
critical_cities = ['武汉市', '广州市', '昆明市', '北京市', '上海市', '拉萨市']
for city in critical_cities:
    if city in df['city_name'].values:
        city_data = df[df['city_name'] == city].sort_values('year')
        pilot_year = city_data['pilot_year'].iloc[0]
        is_treat = city_data['treat'].iloc[0]
        did_1_count = (city_data['did'] == 1).sum()

        status = f"试点城市（{int(pilot_year)}年起）" if is_treat else "非试点城市"
        did_info = f"DID=1观测数: {did_1_count}"

        print(f"  {city:12s}: {status:25s} {did_info}")

# 检查省市重叠问题是否解决
print("\n[检查] 省市重叠问题解决情况:")
overlap_cities = ['武汉市', '广州市', '昆明市']
for city in overlap_cities:
    if city in df['city_name'].values:
        pilot_year = df[df['city_name'] == city]['pilot_year'].iloc[0]
        expected = 2010
        status = "[OK]" if pilot_year == expected else "[ERROR]"
        print(f"  {city}: pilot_year={int(pilot_year)} (期望{expected}) {status}")

# ============ 保存数据 ============

print("\n" + "=" * 100)
print("步骤5: 保存数据")
print("=" * 100)

# 删除临时变量
df = df.drop(columns=['province_code'])

# 保存数据（覆盖原文件）
df.to_excel(OUTPUT_FILE, index=False)
print(f"\n数据已保存到: {OUTPUT_FILE}")
print(f"文件大小: {OUTPUT_FILE.stat().st_size / 1024 / 1024:.2f} MB")

# 保存试点城市名单
PILOT_LIST_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\试点城市名单.xlsx")
df_pilot = pd.DataFrame([
    {'city_name': city, 'pilot_year': year, 'batch': '第一批' if year == 2010 else '第二批' if year == 2012 else '第三批'}
    for city, year in sorted(city_to_pilot_year.items(), key=lambda x: (x[1], x[0]))
])
df_pilot.to_excel(PILOT_LIST_FILE, index=False)
print(f"试点城市名单已保存到: {PILOT_LIST_FILE}")

# ============ 修复总结 ============

print("\n" + "=" * 100)
print("DID变量重构总结")
print("=" * 100)

print(f"""
数据集: {OUTPUT_FILE.name}
规模: {df.shape[0]}个观测 x {df.shape[1]}个变量

核心修复:
1. [修复] 省市重叠导致的年份滞后
   - 武汉市: {df[df['city_name']=='武汉市']['pilot_year'].iloc[0]:.0f}年（原为2013年，现已修正为2010年）
   - 广州市: {df[df['city_name']=='广州市']['pilot_year'].iloc[0]:.0f}年（原为2013年，现已修正为2010年）
   - 昆明市: {df[df['city_name']=='昆明市']['pilot_year'].iloc[0]:.0f}年（原为2013年，现已修正为2010年）

2. [修正] 第二批试点启动年份
   - 原设定: 2013年
   - 修正后: 2012年（准确反映2012年4月启动时间）

3. [补全] 第三批遗漏的西部城市
   - 新增: 拉萨市、伊宁市、和田市

4. [修正] 区县级试点名称
   - 普洱市思茅区 -> 普洱市（地级市）

变量说明:
- treat: 是否为试点城市（1=是，0=否）
- pilot_year: 试点开始年份（非试点城市为NaN）
- post: 是否在政策实施期（1=是，0=否）
- did: DID政策变量 = treat x post

试点城市分布:
- 第一批（2010年）: {batch_counts.get(2010, 0)}个城市（含省级试点覆盖）
- 第二批（2012年）: {batch_counts.get(2012, 0)}个城市（含省级试点覆盖）
- 第三批（2017年）: {batch_counts.get(2017, 0)}个城市（补全后）
- 总计: {df[df['treat']==1]['city_name'].nunique()}个试点城市

处理组与对照组:
- 处理组: {df[df['treat']==1]['city_name'].nunique()}个城市
- 对照组: {df['city_name'].nunique() - df[df['treat']==1]['city_name'].nunique()}个城市

DID变量统计:
- DID=1的观测: {df['did'].sum()}个 ({df['did'].sum()/len(df)*100:.2f}%)
- DID=0的观测: {len(df) - df['did'].sum()}个 ({(1-df['did'].sum()/len(df))*100:.2f}%)

下一步工作:
- 重新运行PSM匹配（因DID变量变化，处理组可能变化）
- 重新运行PSM-DID回归
- 重新进行平行趋势检验
""")

print("\n" + "=" * 100)
print("DID变量重构完成！")
print("=" * 100)
