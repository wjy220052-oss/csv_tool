from value_analysis import is_date_datetime
import os,csv,re
# 基础信息

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
    if is_date_datetime(s):
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

def load_rows(file_path):
    if detect_header(file_path):
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            rows = []

            for row_idx, row in enumerate(reader, start=2):
                row_dict = {name: row.get(name, "") for name in fieldnames}
                rows.append((row_idx, row_dict))

            return fieldnames, rows

    else:
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            raw_rows = list(reader)

        if not raw_rows:
            return [], []

        fieldnames = [f"column_{i}" for i in range(1, len(raw_rows[0]) + 1)]
        rows = []

        for row_idx, row in enumerate(raw_rows, start=1):
            row_dict = {
                fieldnames[i]: row[i] if i < len(row) else ""
                for i in range(len(fieldnames))
            }
            rows.append((row_idx, row_dict))

        return fieldnames, rows
def count_rows_cols(file_path):
    fieldnames, rows = load_rows(file_path)
    return [len(rows), len(fieldnames)]
def check_duplicate(file_path):
    fieldnames, rows = load_rows(file_path)

    row_counter = {}
    for row_idx, row in rows:
        row_tuple = tuple((col, row.get(col, "")) for col in fieldnames)

        if row_tuple in row_counter:
            row_counter[row_tuple]["count"] += 1
            row_counter[row_tuple]["list"].append(row_idx)
        else:
            row_counter[row_tuple] = {
                "count": 1,
                "list": [row_idx],
            }

    result = {}
    duplicate_count = 0

    for k, v in row_counter.items():
        if v["count"] > 1:
            result[k] = v
            duplicate_count += v["count"] - 1

    return [duplicate_count, result]
def check_table(file_path,col):
    result = {
        "file_path": file_path,
        "row_count": count_rows_cols(file_path)[0],
        "column_count": count_rows_cols(file_path)[1],
        "header": read_csv(file_path),
        "duplicate_row_count": check_duplicate(file_path)[0],
        "columns":col,
        "suggestions" : []
    }
    return result

