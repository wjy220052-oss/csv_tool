import re

DATE = [
    (re.compile(r"^\d{4}-\d{2}-\d{2}$"), "%Y-%m-%d","date_ymd_dash"),   # YYYY-MM-DD
    (re.compile(r"^\d{4}/\d{2}/\d{2}$"), "%Y/%m/%d","date_ymd_slash"),   # YYYY/MM/DD
    (re.compile(r"^\d{2}/\d{2}/\d{4}$"), "%m/%d/%Y","date_mdy_slash"),  # MM/DD/YYYY
    (re.compile(r"^\d{2}/\d{2}/\d{4}$"), "%d/%m/%Y","date_dmy_slash"),  # DD/MM/YYYY
    (re.compile(r"^\d{4}\d{2}\d{2}$"), "%Y%m%d","date_ymd_compact"),  # YYYYMMDD
]

DATETIME = [
    (re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"), "%Y-%m-%d %H:%M:%S","datetime_ymd_dash_hms"),  # YYYY-MM-DD HH:MM:SS
    (re.compile(r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$"), "%Y/%m/%d %H:%M:%S","datetime_ymd_slash_hms"),  # YYYY/MM/DD HH:MM:SS
    (re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"), "%Y-%m-%d %H:%M","datetime_ymd_dash_hm"),     # YYYY-MM-DD HH:MM
    (re.compile(r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}$"), "%Y/%m/%d %H:%M","datetime_ymd_slash_hm"),     # YYYY/MM/DD HH:MM
    #(re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}$"), "%Y-%m-%d %H:%M:%S.%f"),  # YYYY-MM-DD HH:MM:SS.SSS
    #(re.compile(r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d{3}$"), "%Y/%m/%d %H:%M:%S.%f"),  # YYYY/MM/DD HH:MM:SS.SSS
    ]
MISSING = ["", " ", "nan", "null","none","n/a"]
BOOLEN = ["true", "false","yes","no","y","n","t","f","1","0","on","off","enabled","disabled","active","inactive"]
AUTO_CLEAN_FLAGS = {
    "trimmed_whitespace": "去掉首尾空格",
    "missing_token": "统一缺失值标记",
    "placeholder_token": "检查占位词是否应转化为空值",
    "number_with_comma": "去掉千分位逗号后再转为空值",
    "embedded_control_char": "清理换行符、制表符等控制字符",
    "empty_after_trim":"建议去掉空值",
    "leading_zero": "检查是否需要去掉前导零",
    "compact_date_format": "检查是否需要转换为标准日期格式",
    "ambiguous_date_format": "检查是否需要转换为标准日期格式",
    "non_standard_bool": "检查是否需要转换为标准布尔值",
}
PLACEHOLDER_TOKENS = {"unknown", "tbd", "-", "?"}
CONTROL_CHAR = {"\n","\t","\r"}