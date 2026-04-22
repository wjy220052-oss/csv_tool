# CSV Tool - CSV数据分析工具

一个用于CSV文件数据分析的Python工具集，提供文件验证、类型推断、缺失值检测、重复行检测等功能。

## 功能特性

- **文件验证** (`read_file.py`) - 检查文件是否存在、格式正确、非空且可读
- **表头检测** (`read_file.py`) - 智能检测CSV文件是否包含表头行
- **行列统计** (`read_file.py`) - 统计CSV文件的行数和列数
- **缺失值检测** (`check_missing.py`) - 检测空值、NULL、NaN、N/A等缺失数据
- **重复行检测** (`check_duplicate.py`) - 检测并统计完全重复的数据行
- **类型推断** (`check_type.py`) - 自动推断每列的数据类型（布尔、整数、浮点、日期、字符串）
- **综合分析** (`csv_tool.py`) - 整合所有功能的命令行入口

## 安装依赖

```bash
pip install -r requirements.txt
```

依赖项：
- pandas >= 1.3.0
- python-dateutil >= 2.8.0

## 使用方法

### 命令行方式

```bash
python csv_tool.py <csv文件路径>
```

示例：
```bash
python csv_tool.py production.csv
```

### 作为模块导入

```python
from read_file import is_valid_file, read_csv, count_rows_cols
from check_missing import check_missing
from check_duplicate import check_duplicate
from check_type import check_type

# 验证文件
if is_valid_file('data.csv'):
    # 读取表头
    header = read_csv('data.csv')
    print(f"列名: {header}")
    
    # 统计行列
    rows, cols = count_rows_cols('data.csv')
    print(f"行数: {rows}, 列数: {cols}")
    
    # 检查缺失值
    missing = check_missing('data.csv')
    print(f"缺失值统计: {missing}")
    
    # 检查重复行
    duplicates = check_duplicate('data.csv')
    print(f"重复行数: {duplicates}")
    
    # 类型推断
    types = check_type('data.csv')
    print(f"列类型: {types}")
```

## 文件说明

| 文件 | 功能描述 |
|------|---------|
| `csv_tool.py` | 主入口程序，整合所有功能的命令行工具 |
| `read_file.py` | CSV文件读取、验证、表头检测、行列统计 |
| `check_type.py` | 数据类型推断（布尔、整数、浮点、日期、字符串） |
| `check_duplicate.py` | 重复行检测与统计 |
| `check_missing.py` | 缺失值检测（支持空值、NULL、NaN、N/A等） |
| `test_csv_tool.py` | 单元测试和集成测试 |
| `production.csv` | 示例数据文件 |

## 测试

运行测试：

```bash
python test_csv_tool.py
```

测试覆盖：
- 文件验证功能
- 数字和表头识别
- 表头检测算法
- CSV读取功能
- 行列统计
- 缺失值识别
- 重复行检测
- 日期格式识别
- 集成测试

## 支持的日期格式

- `YYYY-MM-DD` (如: 2024-01-15)
- `YYYY/MM/DD` (如: 2024/01/15)
- `YYYY-MM-DD HH:MM:SS` (如: 2024-01-15 10:30:00)
- `YYYY/MM/DD HH:MM:SS` (如: 2024/01/15 10:30:00)
- `YYYY-MM-DD HH:MM` (如: 2024-01-15 10:30)
- `YYYY/MM/DD HH:MM` (如: 2024/01/15 10:30)
- `YYYYMMDD` (如: 20240115)

## 支持的缺失值格式

- 空值/空字符串
- `null` / `NULL`
- `nan` / `NaN`
- `none` / `NONE`
- `na` / `NA` / `N/A`

## 示例输出

```
文件分析结果：
文件名：production.csv
行数：11
列数：10
缺失值：{'age': 1, 'salary': 1, 'last_login': 1, 'city': 1, 'score': 1, 'remark': 4}
重复行数：1
类型：{'user_id': {'type': 'int', 'count': '1.00'}, 'username': {'type': 'string', 'count': '1.00'}, ...}
样例值：
   user_id username  age  salary  is_active  ...
0     1001    Alice   25  5500.5       True  ...
1     1002      Bob  NaN  6200.0      False  ...
2     1003  Charlie   30     NaN       True  ...
```

## License

MIT License
