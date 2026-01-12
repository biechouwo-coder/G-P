"""
检查鄂尔多斯碳排放强度数据异常
"""
import pandas as pd

# 读取原始碳排放数据
print("[OK] 读取碳排放数据...")
df_carbon = pd.read_excel('原始数据/地级市碳排放强度.xlsx', sheet_name=0)

print(f"数据形状: {df_carbon.shape}")
print("\n列名:")
for i, col in enumerate(df_carbon.columns):
    print(f"  {i}: {col}")

# 查找鄂尔多斯 (city_code = 150600)
print("\n查找鄂尔多斯数据...")
ordos_carbon = df_carbon[df_carbon.iloc[:, 1] == 150600]

if len(ordos_carbon) > 0:
    print(f"\n找到 {len(ordos_carbon)} 条鄂尔多斯记录")
    print("\n鄂尔多斯碳排放数据 (2019-2023):")
    print(ordos_carbon.iloc[:, [0, 1, 2, 5, 6, 7, 8]].to_string(index=False))
else:
    print("未找到鄂尔多斯数据")

# 读取GDP数据检查
print("\n" + "="*80)
print("[OK] 读取GDP数据...")
df_gdp = pd.read_excel('原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx', sheet_name=0)

print(f"\n数据形状: {df_gdp.shape}")
print("\n列名:")
for i, col in enumerate(df_gdp.columns):
    print(f"  {i}: {col}")

# 查找鄂尔多斯
print("\n查找鄂尔多斯GDP数据...")
ordos_gdp = df_gdp[df_gdp.iloc[:, 1] == 150600]

if len(ordos_gdp) > 0:
    print(f"\n找到 {len(ordos_gdp)} 条鄂尔多斯记录")
    print("\n鄂尔多斯GDP数据 (2019-2023):")
    # 显示年份、城市代码、城市名、实际GDP、名义GDP、平减指数
    display_cols = [0, 1, 2, 3, 4, 5]  # 根据实际列调整
    print(ordos_gdp.iloc[:, display_cols].to_string(index=False))
else:
    print("未找到鄂尔多斯GDP数据")

# 检查最终数据集中的鄂尔多斯数据
print("\n" + "="*80)
print("[OK] 读取最终数据集...")
df_final = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI.xlsx')

ordos_final = df_final[df_final['city_code'] == 150600]

if len(ordos_final) > 0:
    print(f"\n找到 {len(ordos_final)} 条鄂尔多斯记录")
    print("\n鄂尔多斯最终数据 (2020-2023):")
    print(ordos_final[ordos_final['year'].isin([2020, 2021, 2022, 2023])][
        ['year', 'city_name', 'gdp_real', 'carbon_intensity']
    ].to_string(index=False))

    # 检查2022年异常
    ordos_2022 = ordos_final[ordos_final['year'] == 2022]
    if len(ordos_2022) > 0:
        print("\n[WARNING] 2022年鄂尔多斯数据:")
        print(f"  实际GDP: {ordos_2022.iloc[0]['gdp_real']:.2f} 亿元")
        print(f"  碳排放强度: {ordos_2022.iloc[0]['carbon_intensity']:.4f}")

        # 与前后年份对比
        ordos_2021 = ordos_final[ordos_final['year'] == 2021]
        ordos_2023 = ordos_final[ordos_final['year'] == 2023]

        if len(ordos_2021) > 0 and len(ordos_2023) > 0:
            gdp_2021 = ordos_2021.iloc[0]['gdp_real']
            gdp_2022 = ordos_2022.iloc[0]['gdp_real']
            gdp_2023 = ordos_2023.iloc[0]['gdp_real']

            print(f"\nGDP对比:")
            print(f"  2021年: {gdp_2021:.2f} 亿元")
            print(f"  2022年: {gdp_2022:.2f} 亿元 (变化: {(gdp_2022/gdp_2021-1)*100:.1f}%)")
            print(f"  2023年: {gdp_2023:.2f} 亿元 (变化: {(gdp_2023/gdp_2022-1)*100:.1f}%)")

            if gdp_2022 > gdp_2021 * 3:
                print(f"\n[CRITICAL] 2022年GDP异常偏高，是2021年的 {gdp_2022/gdp_2021:.1f} 倍！")
else:
    print("最终数据集中未找到鄂尔多斯")
