# CSV 概况分析 CLI

一个面向数据分析前置检查的命令行工具。  
输入一个 CSV 文件，输出表级与列级的概况分析结果，包括：

- 表头识别
- 行数、列数
- 重复行统计
- 列主类型推断
- 缺失值统计
- 问题样例定位
- 清洗建议

这个工具适合在正式使用 pandas、SQL 或可视化之前，先快速检查原始 CSV 的质量。

---

## 功能特性

### 表级分析
- 检查文件是否存在、是否可读、是否为空
- 尝试识别 CSV 是否包含表头
- 统计总行数、总列数
- 检查重复行数量

### 列级分析
- 统计缺失值数量与缺失率
- 推断列主类型：
  - `int`
  - `float`
  - `str`
  - `bool`
  - `date`
  - `date_time`
- 统计列中问题标记数量
- 提供正常样例与问题样例
- 自动生成清洗建议

### 单元格级分析
- 缺失值识别
- 布尔值识别
- 数值识别
- 日期 / 日期时间识别
- 问题标记（flags）检测

---

## 当前支持的问题标记

- `trimmed_whitespace`：前后有空格
- `missing_token`：缺失值标记，如 `null`、`nan`
- `placeholder_token`：占位值，如 `unknown`、`-`
- `number_with_comma`：数字中带千分位逗号
- `embedded_control_char`：包含换行、制表符等控制字符
- `empty_after_trim`：去空格后为空
- `leading_zero`：整数前导零
- `compact_date_format`：紧凑日期格式，如 `20240101`
- `ambiguous_date_format`：歧义日期格式，如 `03/04/2024`
- `non_standard_bool`：非标准布尔写法，如 `yes/no`

---

## 项目结构

```text
.
├── cli.py              # 命令行入口
├── main.py             # 主流程调度
├── config.py           # 共享常量与规则配置
├── value_analysis.py   # 单元格分析器
├── column_analysis.py  # 列分析器
├── table_analysis.py   # 表级分析器
├── display_report.py   # 终端报告输出
└── README.md
