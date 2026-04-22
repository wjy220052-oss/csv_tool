from datetime import datetime
import re
import pandas as pd



# 每列大概是什么类型
def is_strict_datetime(s:str)->bool:  # 对于常见日期类型的数据进行识别
    s = s.strip()
    DATE_PATTERNS = [
    (re.compile(r"^\d{4}-\d{2}-\d{2}$"), "%Y-%m-%d"),   # YYYY-MM-DD
    (re.compile(r"^\d{4}/\d{2}/\d{2}$"), "%Y/%m/%d"),   # YYYY/MM/DD
    (re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"), "%Y-%m-%d %H:%M:%S"),  # YYYY-MM-DD HH:MM:SS
    (re.compile(r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$"), "%Y/%m/%d %H:%M:%S"),  # YYYY/MM/DD HH:MM:SS
    (re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"), "%Y-%m-%d %H:%M"),     # YYYY-MM-DD HH:MM
    (re.compile(r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}$"), "%Y/%m/%d %H:%M"),     # YYYY/MM/DD HH:MM
]
    for pattern, format in DATE_PATTERNS:
        if pattern.match(s):
            try:
                datetime.strptime(s, format)
                return True
            except ValueError:
                pass
    return False
def is_yyyymmdd(s: str) -> bool:    # 对于形如YYYYMMDD的日期类型的数据进行识别
    s = s.strip()
    if not re.fullmatch(r"\d{8}", s):
        return False
    year = int(s[:4])
    if not (1900 <= year <= 2100):
        return False
    try:
        datetime.strptime(s, "%Y%m%d")
        return True
    except ValueError:
        return False
    

def infer_type(series):
    cleaned = series.dropna()  # 删除空值
    # 判断是否为空
    if cleaned.empty:
        return 'NA'
    bool_count = 0
    int_count = 0
    float_count = 0
    date_count = 0
    string_count = 0
    for item in cleaned:
        s = str(item).strip()
        if s == "":
            continue
        if s.lower() in ["true", "false"]:
            bool_count += 1
            continue
        try:
            int(s)
            int_count += 1
            continue
        except ValueError:
            pass
        try:
            float(s)
            float_count += 1
            continue
        except ValueError:
            pass
        try:
            if is_strict_datetime(s) or is_yyyymmdd(s):
                date_count += 1
                continue
        except Exception:
            pass
        string_count += 1
    total = bool_count + int_count + float_count + date_count + string_count
    if total == 0:
        return 'NA'
    if bool_count / total > 0.5:
        return {"type": "bool", "count": f"{bool_count/total:.2f}"}
    if int_count / total > 0.5:
        return {"type": "int", "count": f"{int_count/total:.2f}"}
    if float_count / total > 0.5:
        return {"type": "float", "count": f"{float_count/total:.2f}"}
    if date_count / total > 0.5:
        return {"type": "date", "count": f"{date_count/total:.2f}"}
    if string_count / total > 0.5:
        return {"type": "string", "count": f"{string_count/total:.2f}"}
    return {"type": "mixed", "count": f"{max(bool_count/total,int_count/total,float_count/total,float_count/total,date_count/total,string_count/total):.2f}"}
    

def check_type(file_path):
    df = pd.read_csv(file_path)
    result = {}
    for col in df.columns:
        result[col] = infer_type(df[col])
    return result

if __name__ == "__main__":
    file_path = "data.csv"
    print(check_type(file_path))