"""
重构DID政策变量 - 2012/2017稳健性检验版本

核心修改:
- 将第一批试点城市从2010年改为2012年（人为推迟政策时间）
- 第二批保持2012年（实际上与第一批合并）
- 第三批保持2017年

目的: 稳健性检验 - 验证如果人为推迟第一批政策时间，结果是否发生变化

处理逻辑:
1. 第一批城市（原2010年）: 改为2012年
2. 第二批城市（原2013年）: 改为2012年（统一到2012）
3. 第三批城市（原2017年）: 保持2017年不变

结果: 只有两个政策断点：2012年和2017年
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import shutil

print("=" * 100)
print("低碳试点城市DID变量重构 - 2012/2017稳健性检验版本")
print("=" * 100)
print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 文件路径设置
BASE_DIR = Path(r"c:\Users\HP\Desktop\毕业论文")
NEW_FOLDER = BASE_DIR / "2012、2017回归"
INPUT_FILE = NEW_FOLDER / "总数据集_2007-2023_最终回归版.xlsx"
OUTPUT_FILE = NEW_FOLDER / "总数据集_2012-2017版本.xlsx"
PILOT_LIST_FILE = NEW_FOLDER / "试点城市名单_2012-2017版本.xlsx"

print(f"\n输入文件: {INPUT_FILE}")
print(f"输出文件: {OUTPUT_FILE}")

# 读取数据集
df = pd.read_excel(INPUT_FILE)
print(f"\n数据规模: {df.shape}")
print(f"  城市数: {df['city_name'].nunique()}")

# 删除旧的DID变量（如果存在）
cols_to_drop = ['treat', 'post', 'did', 'pilot_year']
for col in cols_to_drop:
    if col in df.columns:
        df = df.drop(columns=[col])
        print(f"  [INFO] 删除旧变量: {col}")

# ============ 定义2012/2017版本试点名单 ============

print("\n" + "=" * 100)
print("步骤1: 定义2012/2017版本试点名单")
print("=" * 100)

# 第一批（原2010年）-> 改为2012年
batch_1_provinces = [44, 21, 42, 61, 53]  # 省级代码前两位
batch_1_cities = [
    '天津市', '重庆市', '深圳市', '厦门市',
    '杭州市', '南昌市', '贵阳市', '保定市'
]

# 第二批（原2013年）-> 改为2012年
batch_2_province = [46]  # 海南
batch_2_cities = [
    '北京市', '上海市', '石家庄市', '秦皇岛市', '晋城市', '呼伦贝尔市',
    '吉林市', '大兴安岭地区', '苏州市', '淮安市', '镇江市', '宁波市',
    '温州市', '池州市', '南平市', '景德镇市', '赣州市', '青岛市',
    '济源市', '武汉市', '广州市', '桂林市', '广元市', '遵义市',
    '昆明市', '延安市', '金昌市', '乌鲁木齐市'
]

# 第三批（2017年）- 保持不变
batch_3_cities = [
    '乌海市', '沈阳市', '大连市', '朝阳市', '逊克县', '南京市', '常州市',
    '嘉兴市', '金华市', '衢州市', '合肥市', '淮北市', '黄山市', '六安市',
    '宣城市', '池州市', '三明市', '南平市', '吉安市', '抚州市', '共青城市',
    '济南市', '烟台市', '潍坊市', '济源市', '长沙市', '株洲市', '湘潭市',
    '郴州市', '中山市', '柳州市', '桂林市', '三亚市', '琼中黎族苗族自治县',
    '成都市', '广元市', '玉溪市', '延安市', '安康市', '兰州市', '金昌市',
    '敦煌市', '西宁市', '银川市', '吴忠市', '乌鲁木齐市', '昌吉市',
    '拉萨市', '伊宁市', '和田市'
]

print("\n[说明] 2012年试点（合并原第一批和第二批）:")
print(f"  试点省份（6个）: 广东、辽宁、湖北、陕西、云南、海南")
print(f"  试点城市（34个）: 原8个 + 原26个明确城市")

print("\n[说明] 2017年试点（保持不变）:")
print(f"  试点城市（{len(batch_3_cities)}个）")

# ============ 构建city_to_pilot_year映射 ============

print("\n" + "=" * 100)
print("步骤2: 构建城市→试点年份映射（2012/2017版本）")
print("=" * 100)

city_to_pilot_year = {}

# 提取所有城市的省级代码
df['province_code'] = df['city_code'].astype(str).str[:2].astype(int)

# 【核心修改】第一批和第二批统一改为2012年
print("\n[处理] 2012年试点城市（原第一批+第二批）...")

# 处理第一批明确城市（改为2012年）
for city_name in batch_1_cities:
    if city_name in df['city_name'].values:
        city_to_pilot_year[city_name] = 2012

print(f"  原第一批明确城市: {len([c for c in batch_1_cities if c in df['city_name'].values])}个 -> 改为2012年")

# 处理第二批明确城市（改为2012年）
for city_name in batch_2_cities:
    if city_name in df['city_name'].values:
        city_to_pilot_year[city_name] = 2012

print(f"  原第二批明确城市: {len([c for c in batch_2_cities if c in df['city_name'].values])}个 -> 改为2012年")

# 处理第三批明确城市（保持2017年）
for city_name in batch_3_cities:
    if city_name in df['city_name'].values:
        if city_name not in city_to_pilot_year:
            city_to_pilot_year[city_name] = 2017

print(f"  第三批明确城市: {len([c for c in batch_3_cities if c in df['city_name'].values])}个 -> 保持2017年")

print(f"\n  -> 明确名单处理后: {len(city_to_pilot_year)}个城市已赋值")

# 【省级试点覆盖】
print("\n[处理] 省级试点覆盖（2012年）...")

# 2012年省级试点（合并原第一批和第二批）
provinces_2012 = batch_1_provinces + batch_2_province
province_names_2012 = {
    44: '广东', 21: '辽宁', 42: '湖北', 61: '陕西', 53: '云南', 46: '海南'
}

for province_code in provinces_2012:
    cities_in_province = df[df['province_code'] == province_code]['city_name'].unique()
    count = 0
    for city_name in cities_in_province:
        if city_name not in city_to_pilot_year:
            city_to_pilot_year[city_name] = 2012
            count += 1

    province_name = province_names_2012[province_code]
    print(f"  {province_name}省（{province_code}）: 新增{count}个城市 -> 2012年")

print(f"\n试点城市总数: {len(city_to_pilot_year)}")

# ============ 验证关键城市是否正确 ============

print("\n[验证] 关键城市试点年份检查:")
test_cities = [
    ('天津市', 2012, '原第一批->2012'),
    ('武汉市', 2012, '原第二批->2012'),
    ('广州市', 2012, '原第二批->2012'),
    ('昆明市', 2012, '原第二批->2012'),
    ('北京市', 2012, '原第二批->2012'),
    ('上海市', 2012, '原第二批->2012'),
    ('拉萨市', 2017, '第三批->2017'),
    ('伊宁市', 2017, '第三批->2017'),
]
for city, expected, note in test_cities:
    if city in city_to_pilot_year:
        actual = city_to_pilot_year[city]
        status = "[OK]" if actual == expected else f"[ERROR] 期望{expected}"
        print(f"  {city}: {actual}年 ({note}) {status}")
    else:
        print(f"  {city}: 未找到 ({note}) [WARNING]")

# ============ 构建DID变量 ============

print("\n" + "=" * 100)
print("步骤3: 构建DID变量（2012/2017版本）")
print("=" * 100)

# 映射试点年份到数据集
df['pilot_year'] = df['city_name'].map(city_to_pilot_year)

# 创建treat变量
df['treat'] = df['pilot_year'].notna().astype(int)

# 创建post变量
df['post'] = (df['year'] >= df['pilot_year']).astype(int)

# 对于非试点城市，post应为0
df.loc[df['treat'] == 0, 'post'] = 0

# 创建DID变量
df['did'] = df['treat'] * df['post']

print(f"\n[INFO] DID变量构建完成")
print(f"  处理组城市数: {df['treat'].sum() / 17:.0f}个")
print(f"  对照组城市数: {len(df) / 17 - df['treat'].sum() / 17:.0f}个")
print(f"  DID=1观测数: {df['did'].sum()}个")

# ============ 验证DID变量 ============

print("\n" + "=" * 100)
print("步骤4: 验证DID变量")
print("=" * 100)

# 统计各批次试点城市数
batch_counts = df[df['treat'] == 1].groupby('pilot_year')['city_name'].nunique()
print("\n各批次试点城市数:")
for year in [2012, 2017]:
    count = batch_counts.get(year, 0)
    print(f"  {year}年试点: {count}个城市")

# 检查DID变量随时间的变化
print("\nDID=1的观测数随时间分布:")
did_by_year = df[df['did'] == 1].groupby('year').size()
for year in [2007, 2010, 2011, 2012, 2013, 2017, 2020, 2023]:
    if year in did_by_year.index:
        count = did_by_year[year]
        print(f"  {year}年: {count}个城市DID=1 ({count/df['city_name'].nunique()*100:.1f}%)")
    else:
        print(f"  {year}年: 0个城市DID=1 (0.0%)")

# 验证关键城市
print("\n[再次验证] 关键城市DID变量:")
critical_cities = [
    ('天津市', 2012), ('武汉市', 2012), ('广州市', 2012),
    ('北京市', 2012), ('上海市', 2012), ('拉萨市', 2017)
]
for city, expected_year in critical_cities:
    if city in df['city_name'].values:
        city_data = df[df['city_name'] == city].sort_values('year')
        pilot_year = city_data['pilot_year'].iloc[0]
        is_treat = city_data['treat'].iloc[0]
        did_1_count = (city_data['did'] == 1).sum()

        status = f"试点城市（{int(pilot_year)}年起）" if is_treat else "非试点城市"
        did_info = f"DID=1观测数: {did_1_count}"
        check = "[OK]" if pilot_year == expected_year else f"[ERROR] 期望{expected_year}"

        print(f"  {city:12s}: {status:25s} {did_info} {check}")

# 关键检查：第一批城市在2010和2011年的DID值
print("\n[关键检查] 原第一批城市在2010-2011年的DID值:")
batch_1_sample = ['天津市', '深圳市', '杭州市']
for city in batch_1_sample:
    if city in df['city_name'].values:
        city_data = df[df['city_name'] == city]
        did_2010 = city_data[city_data['year'] == 2010]['did'].values[0]
        did_2011 = city_data[city_data['year'] == 2011]['did'].values[0]
        did_2012 = city_data[city_data['year'] == 2012]['did'].values[0]

        status_2010 = "[OK]" if did_2010 == 0 else "[ERROR]"
        status_2011 = "[OK]" if did_2011 == 0 else "[ERROR]"
        status_2012 = "[OK]" if did_2012 == 1 else "[ERROR]"

        print(f"  {city}: 2010年={did_2010} {status_2010}, 2011年={did_2011} {status_2011}, 2012年={did_2012} {status_2012}")

# ============ 保存数据 ============

print("\n" + "=" * 100)
print("步骤5: 保存数据")
print("=" * 100)

# 删除临时变量
if 'province_code' in df.columns:
    df = df.drop(columns=['province_code'])

# 保存数据
df.to_excel(OUTPUT_FILE, index=False)
print(f"\n数据已保存到: {OUTPUT_FILE}")
print(f"文件大小: {OUTPUT_FILE.stat().st_size / 1024 / 1024:.2f} MB")

# 保存试点城市名单
df_pilot = pd.DataFrame([
    {'city_name': city, 'pilot_year': year, 'batch': '2012年试点' if year == 2012 else '2017年试点'}
    for city, year in sorted(city_to_pilot_year.items(), key=lambda x: (x[1], x[0]))
])
df_pilot.to_excel(PILOT_LIST_FILE, index=False)
print(f"试点城市名单已保存到: {PILOT_LIST_FILE}")

# ============ 总结 ============

print("\n" + "=" * 100)
print("DID变量重构总结（2012/2017版本）")
print("=" * 100)

print(f"""
数据集: {OUTPUT_FILE.name}
规模: {df.shape[0]}个观测 x {df.shape[1]}个变量
城市数: {df['city_name'].nunique()}个

核心修改:
1. [修改] 第一批试点年份
   - 原设定: 2010年
   - 新设定: 2012年（推迟2年）
   - 影响: 天津、深圳、杭州等第一批城市在2010-2011年的DID从1变为0

2. [修改] 第二批试点年份
   - 原设定: 2013年
   - 新设定: 2012年（提前1年）
   - 影响: 北京、上海、武汉、广州等城市从2013改为2012

3. [保持] 第三批试点年份
   - 设定: 2017年（不变）
   - 影响: 无变化

政策断点:
- 2012年试点: {batch_counts.get(2012, 0)}个城市（原第一批+第二批合并）
- 2017年试点: {batch_counts.get(2017, 0)}个城市（原第三批）
- 总计: {df[df['treat']==1]['city_name'].nunique()}个试点城市

处理组与对照组:
- 处理组: {df[df['treat']==1]['city_name'].nunique()}个城市
- 对照组: {df['city_name'].nunique() - df[df['treat']==1]['city_name'].nunique()}个城市

DID变量统计:
- DID=1的观测: {df['did'].sum()}个 ({df['did'].sum()/len(df)*100:.2f}%)
- DID=0的观测: {len(df) - df['did'].sum()}个 ({(1-df['did'].sum()/len(df))*100:.2f}%)

关键变化:
- 原第一批城市（天津等）在2010-2011年: DID从1变为0
- 这些年份现在被视为"政策前时期"
- 可以检验是否存在"政策预期效应"或"提前泄露"

下一步工作:
- 重新运行PSM匹配
- 重新运行平行趋势检验（重点检查2010-2011年系数）
- 重新运行PSM-DID回归
- 对比2012/2017版本与原版本的估计结果
""")

print("\n" + "=" * 100)
print("DID变量重构完成（2012/2017版本）！")
print("=" * 100)
