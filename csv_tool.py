# 导入一个csv文件，读取每列的列名
import csv
import pandas as pd
import argparse
import os
from collections import Counter
from dateutil.parser import parse
from datetime import datetime
import re

from check_type import is_strict_datetime,is_yyyymmdd,infer_type,check_type

from check_duplicate import check_duplicate

from check_missing import check_missing,is_missing

from read_file import is_valid_file,read_csv,count_rows_cols


    
# 保留少量样例值，比如每列保留前三个
def sample(file_path):
    df = pd.read_csv(file_path)
    return df.head(3)

# 显示结果
def show_result(file_path):
    # 判断文件是否合法
    if not is_valid_file(file_path):
        return
    # 读取文件，返回列名
    header = read_csv(file_path)
    if header is None:
        return
    # 统计行数与列数
    rows, cols = count_rows_cols(file_path)
    # 检查每列的缺失是多少，缺失包括空值和空字符串
    missing_count = check_missing(file_path)
    # 检查重复行数量
    duplicate_count = check_duplicate(file_path)
    # 每列大概是什么类型
    type_result = check_type(file_path)
    # 保留少量样例值，比如每列保留前三个
    sample_result = sample(file_path)
    # 显示结果
    print ("文件分析结果：")
    print(f"文件名：{file_path}")
    print(f"行数：{rows}")
    print(f"列数：{cols}")
    print(f"缺失值：{missing_count}")
    print(f"重复行数：{duplicate_count}")
    print(f"类型：{type_result}")
    print(f"样例值：\n{sample_result}")
    return

# 主函数
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CSV文件分析工具')
    parser.add_argument('file', type=str, help='要分析的CSV文件路径')
    args = parser.parse_args()
    show_result(args.file)