import re
from datetime import datetime
from dataclasses import dataclass,field
from config import DATE, DATETIME, BOOLEN, MISSING, PLACEHOLDER_TOKENS

# 判断是否是date类型
def is_date_datetime(s:str)->bool:
    s = s.strip()
    for pattern, fmt,format_name in DATE:
        if pattern.match(s):
            try:
                datetime.strptime(s, fmt)
                return {
                    "type":"date",
                    "format":format_name
                }
            except ValueError:
                pass
    
    for pattern, fmt,format_name in DATETIME:
        if pattern.match(s):
            try:
                datetime.strptime(s, fmt)
                return {
                    "type":"date_time",
                    "format":format_name
                }
            except ValueError:
                pass
    return {}


# 判断是什么类型
def check_type(s):
    if s.lower() in BOOLEN:
        return "bool"
    if is_date_datetime(s):
        return is_date_datetime(s).get("type")
    try:
        int(s)
        return "int"
    except ValueError:
        pass
    try:
        float(s)
        return "float"
    except ValueError:
        pass
    return "str"

def detect_flags(raw: str, normalized: str, check_text: str, basic_type: str) -> list[str]:
    flags = []

    if raw != normalized:
        flags.append("trimmed_whitespace")

    if raw != "" and normalized == "":
        flags.append("empty_after_trim")

    if check_text in MISSING:
        flags.append("missing_token")

    if check_text in PLACEHOLDER_TOKENS:
        flags.append("placeholder_token")

    if "\n" in raw or "\t" in raw or "\r" in raw:
        flags.append("embedded_control_char")

    if re.fullmatch(r"[+-]?\d{1,3}(,\d{3})+(\.\d+)?", normalized):
        flags.append("number_with_comma")

    if basic_type == "int" and re.fullmatch(r"[+-]?0\d+", normalized):
        flags.append("leading_zero")

    if basic_type == "date" and re.fullmatch(r"\d{8}", normalized):
        flags.append("compact_date_format")

    if re.fullmatch(r"\d{2}/\d{2}/\d{4}", normalized):
        month = int(normalized[:2])
        day = int(normalized[3:5])
        if 1 <= month <= 12 and 1 <= day <= 12:
            flags.append("ambiguous_date_format")

    if check_text in {"yes","no","y","n","t","f","1","0","on","off","enabled","disabled","active","inactive"}:
        flags.append("non_standard_bool")

    return flags


# 单元格分析器
def value_analysis(f):
    raw = f["raw"]
    row = f["row"]
    normalized= raw.strip()
    check_text = normalized.lower()
    is_missing = check_text in MISSING
    if is_missing:
        basic_type = "missing"
        format_name = None
    else:
        basic_type = check_type(raw)
        dt_info = is_date_datetime(raw)
        format_name = dt_info.get("format") if dt_info else None
    flags = detect_flags(raw, normalized, check_text, basic_type)
    unit = {
        "raw":raw,
        "row":row,
        "normalized":normalized,
        "check_text":check_text,
        "is_missing":is_missing,
        "type":basic_type,
        "format_name":format_name,
        "flags":flags,
    }
    return unit
    
    

