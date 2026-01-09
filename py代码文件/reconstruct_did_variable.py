"""
重构DID政策变量 - 最终版

核心改进:
1. 剔除普洱市（既非纯粹处理组也非纯粹控制组）
2. 第二批试点时间改回2013年（恢复原设定）
3. 明确名单优先于省级试点（名单中的城市以名单年份为准）
4. 补全第三批遗漏的西部城市（拉萨、伊宁、和田）

三批低碳试点城市：
- 第一批（2010年）：5省 + 8市
- 第二批（2013年）：1省 + 26市
- 第三批（2017年）：45+个城市/地区

处理原则：
1. **剔除普洱市**：完全从样本中删除（云南省级试点但第三批又有思茅区）
2. **明确名单优先原则**：若城市在具体名单中，以名单年份为准（覆盖省级试点）
3. **第二批年份恢复**：2012改回2013（与原始设定一致）
4. DID = 1 当且仅当 当前年份 >= 该城市的试点开始年份
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

print("=" * 100)
print("低碳试点城市DID变量重构 - 最终版")
print("=" * 100)
print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 读取最终数据集
INPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_最终回归版.xlsx")
OUTPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_最终回归版.xlsx")

df = pd.read_excel(INPUT_FILE)
print(f"\n数据规模: {df.shape}")
print(f"  城市数: {df['city_name'].nunique()}")

# 【关键修改】剔除普洱市
print("\n[剔除] 删除普洱市（既非纯粹处理组也非纯粹控制组）")
initial_count = len(df)
df = df[df['city_name'] != '普洱市'].copy()
final_count = len(df)
print(f"  删除前: {initial_count}个观测")
print(f"  删除后: {final_count}个观测")
print(f"  删除: {initial_count - final_count}个观测（{(initial_count - final_count) / 17:.0f}个城市 × 17年）")

# 删除旧的DID变量（如果存在）
cols_to_drop = ['treat', 'post', 'did', 'pilot_year']
for col in cols_to_drop:
    if col in df.columns:
        df = df.drop(columns=[col])
        print(f"  [INFO] 删除旧变量: {col}")

# ============ 定义试点名单（最终版） ============

print("\n" + "=" * 100)
print("步骤1: 定义三批低碳试点名单（最终版）")
print("=" * 100)

# 第一批（2010年）- 7月启动
# 试点省份：广东(44)、辽宁(21)、湖北(42)、陕西(61)、云南(53)
# 试点城市：天津、重庆、深圳、厦门、杭州、南昌、贵阳、保定
batch_1_provinces = [44, 21, 42, 61, 53]  # 省级代码前两位
batch_1_cities = [
    '天津市', '重庆市', '深圳市', '厦门市',
    '杭州市', '南昌市', '贵阳市', '保定市'
]

# 第二批（2013年）- 【年份恢复】2012改回2013
# 试点省份：海南(46)
# 试点城市列表（包含武汉、广州、昆明等，将覆盖省级试点）
batch_2_province = [46]  # 海南
batch_2_cities = [
    '北京市', '上海市', '石家庄市', '秦皇岛市', '晋城市', '呼伦贝尔市',
    '吉林市', '大兴安岭地区', '苏州市', '淮安市', '镇江市', '宁波市',
    '温州市', '池州市', '南平市', '景德镇市', '赣州市', '青岛市',
    '济源市', '武汉市', '广州市', '桂林市', '广元市', '遵义市',
    '昆明市', '延安市', '金昌市', '乌鲁木齐市'
]

# 第三批（2017年）- 补全遗漏城市（剔除普洱市）
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
    # 云南 (1) - 【删除普洱市】
    '玉溪市',
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

print("\n[说明] 第一批试点（2010年）:")
print(f"  试点省份（5个）: 广东、辽宁、湖北、陕西、云南")
print(f"  试点城市（8个）: {', '.join(batch_1_cities)}")
print(f"  [注意] 云南已剔除普洱市")

print("\n[说明] 第二批试点（2013年，年份恢复原设定）:")
print(f"  试点省份（1个）: 海南")
print(f"  试点城市（26个，含武汉、广州、昆明等明确名单城市）")
print(f"  [注意] 明确名单优先于省级试点")

print("\n[说明] 第三批试点（2017年，补全遗漏）:")
print(f"  试点城市（47个，含新增拉萨、伊宁、和田，已剔除普洱市）")

# ============ 构建city_to_pilot_year映射（明确名单优先原则） ============

print("\n" + "=" * 100)
print("步骤2: 构建城市→试点年份映射（明确名单优先原则）")
print("=" * 100)

city_to_pilot_year = {}

# 提取所有城市的省级代码
df['province_code'] = df['city_code'].astype(str).str[:2].astype(int)

# 【核心修改】先处理明确列出的城市名单（优先级最高）
print("\n[优先处理] 明确列出的试点城市名单...")

# 处理第一批明确城市（2010年）
for city_name in batch_1_cities:
    if city_name in df['city_name'].values:
        city_to_pilot_year[city_name] = 2010

print(f"  第一批明确城市: {len([c for c in batch_1_cities if c in df['city_name'].values])}个")

# 处理第二批明确城市（2013年）- 【年份恢复】
for city_name in batch_2_cities:
    if city_name in df['city_name'].values:
        # 【关键】明确名单优先，直接覆盖省级试点赋值
        city_to_pilot_year[city_name] = 2013

print(f"  第二批明确城市: {len([c for c in batch_2_cities if c in df['city_name'].values])}个")
print(f"  [注意] 武汉、广州、昆明等将设为2013年（覆盖省级试点）")

# 处理第三批明确城市（2017年）
for city_name in batch_3_cities:
    if city_name in df['city_name'].values:
        city_to_pilot_year[city_name] = 2017

print(f"  第三批明确城市: {len([c for c in batch_3_cities if c in df['city_name'].values])}个")

print(f"\n  -> 明确名单处理后: {len(city_to_pilot_year)}个城市已赋值")

# 【后处理】省级试点覆盖（只赋值给未赋值的城市）
print("\n[后处理] 省级试点覆盖...")

# 第一批省级试点（2010年）
batch_1_province_names = {
    44: '广东', 21: '辽宁', 42: '湖北', 61: '陕西', 53: '云南'
}
for province_code in batch_1_provinces:
    cities_in_province = df[df['province_code'] == province_code]['city_name'].unique()
    count = 0
    for city_name in cities_in_province:
        # 【核心逻辑】只赋值给未赋值的城市（明确名单优先）
        if city_name not in city_to_pilot_year:
            city_to_pilot_year[city_name] = 2010
            count += 1

    province_name = batch_1_province_names[province_code]
    print(f"  {province_name}省（{province_code}）: 新增{count}个城市")

print(f"  -> 第一批省级试点后: {len(city_to_pilot_year)}个城市已赋值")

# 第二批省级试点（2013年）
for province_code in batch_2_province:
    cities_in_province = df[df['province_code'] == province_code]['city_name'].unique()
    count = 0
    for city_name in cities_in_province:
        if city_name not in city_to_pilot_year:
            city_to_pilot_year[city_name] = 2013
            count += 1

    print(f"  海南省（{province_code}）: 新增{count}个城市")

print(f"  -> 第二批省级试点后: {len(city_to_pilot_year)}个城市已赋值")

print(f"\n试点城市总数: {len(city_to_pilot_year)}")

# ============ 验证关键城市是否正确 ============

print("\n[验证] 关键城市试点年份检查:")
test_cities = [
    ('武汉市', 2013, '第二批明确名单'),  # 期望2013
    ('广州市', 2013, '第二批明确名单'),  # 期望2013
    ('昆明市', 2013, '第二批明确名单'),  # 期望2013
    ('北京市', 2013, '第二批'),
    ('上海市', 2013, '第二批'),
    ('拉萨市', 2017, '第三批新增'),
    ('伊宁市', 2017, '第三批新增'),
    ('和田市', 2017, '第三批新增'),
    ('普洱市', None, '已剔除'),
]
for city, expected, note in test_cities:
    if city in city_to_pilot_year:
        actual = city_to_pilot_year[city]
        status = "[OK]" if actual == expected else f"[ERROR] 期望{expected}"
        print(f"  {city}: {actual}年 ({note}) {status}")
    elif expected is None:
        print(f"  {city}: 已正确剔除 ({note}) [OK]")
    else:
        print(f"  {city}: 未找到 ({note}) [WARNING]")

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
for year in [2010, 2013, 2017]:
    count = batch_counts.get(year, 0)
    if year == 2010:
        print(f"  第一批（2010年）: {count}个城市")
    elif year == 2013:
        print(f"  第二批（2013年，明确名单优先）: {count}个城市")
    elif year == 2017:
        print(f"  第三批（2017年，补全后）: {count}个城市")

# 检查DID变量随时间的变化
print("\nDID=1的观测数随时间分布:")
did_by_year = df[df['did'] == 1].groupby('year').size()
for year in [2007, 2010, 2013, 2017, 2023]:
    if year in did_by_year.index:
        count = did_by_year[year]
        print(f"  {year}年: {count}个城市DID=1 ({count/df['city_name'].nunique()*100:.1f}%)")

# 验证关键城市
print("\n[再次验证] 关键城市DID变量:")
critical_cities = [
    ('武汉市', 2013), ('广州市', 2013), ('昆明市', 2013),
    ('北京市', 2013), ('上海市', 2013), ('拉萨市', 2017)
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

# 检查普洱市是否已剔除
print("\n[检查] 普洱市剔除情况:")
if '普洱市' not in df['city_name'].values:
    print(f"  普洱市: 已正确剔除 [OK]")
else:
    print(f"  普洱市: 仍在数据中 [ERROR] {df[df['city_name']=='普洱市'].shape[0]}个观测")

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
    {'city_name': city, 'pilot_year': year, 'batch': '第一批' if year == 2010 else '第二批' if year == 2013 else '第三批'}
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
城市数: {df['city_name'].nunique()}个（已剔除普洱市）

最终修正:
1. [剔除] 普洱市
   - 原因: 既非纯粹处理组（云南省级试点2010），也非纯粹控制组（第三批思茅区）
   - 处理: 完全从样本中删除

2. [恢复] 第二批试点年份
   - 年份: 2012年 → 2013年（恢复原设定）
   - 影响: 北京、上海等城市年份延后1年

3. [修正] 明确名单优先原则
   - 原则: 若城市在具体名单中，以名单年份为准（覆盖省级试点）
   - 影响: 武汉、广州、昆明从2010改为2013
   - 理由: 明确名单更准确地反映了政策实施时间

4. [补全] 第三批遗漏城市
   - 新增: 拉萨市、伊宁市、和田市

变量说明:
- treat: 是否为试点城市（1=是，0=否）
- pilot_year: 试点开始年份（非试点城市为NaN）
- post: 是否在政策实施期（1=是，0=否）
- did: DID政策变量 = treat x post

试点城市分布:
- 第一批（2010年）: {batch_counts.get(2010, 0)}个城市（省级试点覆盖）
- 第二批（2013年）: {batch_counts.get(2013, 0)}个城市（明确名单优先）
- 第三批（2017年）: {batch_counts.get(2017, 0)}个城市（补全后）
- 总计: {df[df['treat']==1]['city_name'].nunique()}个试点城市

处理组与对照组:
- 处理组: {df[df['treat']==1]['city_name'].nunique()}个城市
- 对照组: {df['city_name'].nunique() - df[df['treat']==1]['city_name'].nunique()}个城市

DID变量统计:
- DID=1的观测: {df['did'].sum()}个 ({df['did'].sum()/len(df)*100:.2f}%)
- DID=0的观测: {len(df) - df['did'].sum()}个 ({(1-df['did'].sum()/len(df))*100:.2f}%)

关键城市验证:
- 武汉市: {df[df['city_name']=='武汉市']['pilot_year'].iloc[0]:.0f}年（第二批明确名单）
- 广州市: {df[df['city_name']=='广州市']['pilot_year'].iloc[0]:.0f}年（第二批明确名单）
- 昆明市: {df[df['city_name']=='昆明市']['pilot_year'].iloc[0]:.0f}年（第二批明确名单）
- 普洱市: 已剔除

下一步工作:
- 重新运行PSM匹配（因DID变量变化，处理组可能变化）
- 重新运行PSM-DID回归
- 重新进行平行趋势检验
""")

print("\n" + "=" * 100)
print("DID变量重构完成！")
print("=" * 100)
