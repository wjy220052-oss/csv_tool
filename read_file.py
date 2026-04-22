import os
import csv
import re
from check_type import is_strict_datetime, is_yyyymmdd

# 判断文件是否是合法文件
def is_valid_file(file_path):
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print("文件不存在")
        return False
    # 检查文件是否为csv文件
    if not file_path.endswith('.csv'):
        print("请输入一个csv文件")
        return False
    # 检查文件是否为空
    if os.path.getsize(file_path) == 0:
        print("文件为空")
        return False
    # 检查文件是否可读
    if not os.access(file_path, os.R_OK):
        print("文件不可读")
        return False
    return True

# 读取文件，返回列名

def looks_like_number(s: str) -> bool:
    return bool(re.fullmatch(r"[+-]?\d+(\.\d+)?", s.strip()))

def looks_like_header_token(s: str) -> bool:
    s = s.strip()
    if not s:
        return False
    if looks_like_number(s):
        return False
    if is_strict_datetime(s) or is_yyyymmdd(s):
        return False
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ ]*", s))

def detect_header(file_path, sample_rows=5):
    with open(file_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = []
        for i, row in enumerate(reader):
            if row:
                rows.append(row)
            if len(rows) >= sample_rows + 1:
                break

    if len(rows) < 2:
        return False

    first_row = rows[0]
    data_rows = rows[1:]

    score = 0

    # 规则1：Sniffer 给一点权重
    with open(file_path, "r", encoding="utf-8", newline="") as f:
        sample = f.read(2048)
        try:
            if csv.Sniffer().has_header(sample):
                score += 2
        except csv.Error:
            pass

    # 规则2：第一行 token 更像字段名
    header_like_count = sum(looks_like_header_token(x) for x in first_row)
    if header_like_count >= max(1, len(first_row) * 0.6):
        score += 2

    # 规则3：第一行几乎不含数字，而后面行含数字较多
    first_numeric = sum(looks_like_number(x) for x in first_row)
    other_numeric = 0
    other_total = 0
    for row in data_rows:
        for x in row:
            other_total += 1
            if looks_like_number(x):
                other_numeric += 1

    if first_numeric == 0 and other_total > 0 and other_numeric / other_total > 0.3:
        score += 2

    # 规则4：第一行值唯一
    if len(set(first_row)) == len(first_row):
        score += 1

    return score >= 4


def read_csv(file_path):
    with open(file_path, 'r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        first_row = next(reader, None)

    if first_row is None:
        print("文件为空")
        return None

    if detect_header(file_path):
        return first_row
    else:
        print(f"文件可能没有列名，第一行是{first_row}")
        return None

# 统计行数与列数
def count_rows_cols(file_path):
    with open(file_path, 'r',encoding='utf-8', newline='') as file:
        reader = csv.DictReader(file)
        header = reader.fieldnames or []
        data = [row for row in reader]
        return len(data), len(header)

if __name__ == '__main__':
    file_path = 'data.csv'
    if is_valid_file(file_path):
        header = read_csv(file_path)
        if header:
            print(f"列名：{header}")
        rows, cols = count_rows_cols(file_path)
        print(f"行数：{rows}，列数：{cols}")