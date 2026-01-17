# CEADs数据处理 - Python脚本文件夹

本文件夹包含所有用于处理CEADs碳排放数据的Python脚本。

## 脚本列表

### 1. 数据探索
- **step1_explore_ceads.py** - 探索CEADs原始数据结构
- **check_ceads_cities.py** - 检查CEADs城市列表
- **test_merge.py** - 测试数据合并

### 2. 数据清洗
- **step2_clean_ceads.py** - 初始清洗脚本
- **step2b_clean_ceads_fixed.py** - 修正版清洗脚本 (修复吉林市bug)
- **step2c_clean_ceads_fixed_v2.py** - **最终V2版** (修复城市名称清洗问题)

### 3. 数据合并
- **step3_merge_data.py** - 初始合并脚本
- **step3b_merge_data_fixed.py** - 修正版合并脚本
- **step3c_merge_data_fixed_v2.py** - **最终V2版**合并脚本

### 4. 碳强度计算
- **step4_calculate_carbon_intensity.py** - 初始碳强度计算
- **step4b_calculate_carbon_intensity_v2.py** - **最终V2版**碳强度计算

### 5. 描述性统计
- **step5_descriptive_statistics.py** - 初始描述性统计
- **step5b_descriptive_statistics_v2.py** - **最终V2版**描述性统计

### 6. PSM分析
- **psm_ceads_five_controls_imputed.py** - CEADs数据PSM分析 (5个控制变量，缺失值插值)

### 7. Bug调试与验证
- **check_jilin_bug.py** - 检查吉林市bug
- **check_jilin_detail.py** - 详细检查吉林市问题
- **debug_match_key.py** - 调试匹配键问题
- **verify_fix.py** - 验证修复结果

### 8. 样本选择偏差分析
- **analyze_selection_bias.py** - 分析样本选择偏差
- **quick_selection_bias_check.py** - 快速检查样本选择偏差

## 脚本使用说明

### 推荐工作流程 (V2版本)

```bash
cd "使用CEADs数据/py代码文件"

# Step 1: 清洗CEADs数据 (V2 - 修复城市名称bug)
py step2c_clean_ceads_fixed_v2.py

# Step 2: 合并数据 (V2)
py step3c_merge_data_fixed_v2.py

# Step 3: 计算碳强度 (V2)
py step4b_calculate_carbon_intensity_v2.py

# Step 4: 生成描述性统计 (V2)
py step5b_descriptive_statistics_v2.py

# Step 5: 运行PSM (可选)
py psm_ceads_five_controls_imputed.py
```

### 关键文件路径

所有脚本应该从项目根目录运行，或者使用绝对路径：
```python
# 示例路径
ceads_file = r'c:\Users\HP\Desktop\毕业论文\使用CEADs数据\1997-2019年290个中国城市碳排放清单 (1).xlsx'
output_file = r'c:\Users\HP\Desktop\毕业论文\使用CEADs数据\CEADs_2007-2019_清洗后_修正版V2.xlsx'
```

## 版本说明

### V1版本 (已弃用)
- step2_clean_ceads.py
- step3_merge_data.py
- step4_calculate_carbon_intensity.py
- step5_descriptive_statistics.py

### V2版本 (推荐)
- **step2c_clean_ceads_fixed_v2.py** - 修复城市名称清洗bug
  - Bug: "吉林市", "北京市", "上海市" 被转换为空字符串
  - 修复: 添加安全检查 `if remaining and len(remaining) > 0`
  - 结果: 恢复52个观测，4个城市

- **step3c_merge_data_fixed_v2.py** - V2数据合并
- **step4b_calculate_carbon_intensity_v2.py** - V2碳强度计算
- **step5b_descriptive_statistics_v2.py** - V2描述性统计

## PSM分析

### 控制变量
CEADs PSM使用5个控制变量：
1. ln_pgdp - 人均GDP (对数)
2. ln_pop_density - 人口密度 (对数)
3. industrial_advanced - 产业高级化 (三产/二产)
4. fdi_openness - FDI开放度 (FDI/GDP)
5. financial_development - 金融发展水平

### PSM结果
- 匹配后样本: 1,152观测 (576对)
- 匹配率: 75.0%
- 城市: 144个 (65处理组 + 79对照组)
- 平衡性: 4/5变量通过

## 已知问题与修复

### Bug 1: 城市名称清洗问题 (已修复)
- **问题**: V1版本将"吉林市"转为空字符串
- **影响**: 损失52观测，4个城市
- **修复**: V2版本添加安全检查
- **详情**: 参见 `../Bug报告_城市名称清洗问题.md`

### Bug 2: pop_density异常值 (已修复)
- **问题**: merge_final.py提取了错误的列
- **影响**: 上海和东莞数据异常
- **修复**: 使用column 8而非column 9
- **详情**: 参见根目录 `数据质量问题_pop_density异常值修复.md`

## 输出文件

所有输出文件保存在上级目录 `使用CEADs数据/`：
- `CEADs_最终数据集_2007-2019_V2.xlsx` - 最终数据集 (2,323观测)
- `CEADs_PSM_匹配后数据集_五个控制变量_插值版.xlsx` - PSM匹配后数据
- `CEADs_PSM_平衡性检验结果_五个控制变量_插值版.xlsx` - 平衡性检验
- `CEADs_PSM分析报告_五个控制变量.md` - PSM分析报告
- `CEADs_描述性统计表_V2.xlsx` - 描述性统计

## 数据质量

- 城市数: 216个 (2007-2019)
- 观测数: 2,323个
- 与原始数据相关性: 0.7668
- 处理组CEI比对照组低54.50% (p<0.001)

## 依赖包

```
pandas
numpy
openpyxl
scipy
sklearn
```

## 作者

Claude Code
日期: 2025-01-17

## 更新日志

- 2025-01-17: 创建py代码文件文件夹，整理所有脚本
- 2025-01-17: 修复城市名称清洗bug (V2版本)
- 2025-01-14: 完成CEADs数据PSM分析
