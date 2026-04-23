from value_analysis import value_analysis
from table_analysis import count_rows_cols,check_duplicate,check_table,is_valid_file,load_rows,read_csv
from column_analysis import column_analysis


def main(file_path):
    DATA = {}
    print("正在尝试读取文件...")
    if not is_valid_file(file_path):
        raise ValueError("文件无效")

    print("读取文件中...")
    header = read_csv(file_path)

    print("正在检查表...")
    row_count = count_rows_cols(file_path)[0]
    col_count = count_rows_cols(file_path)[1]
    duplicate = check_duplicate(file_path)

    fieldnames,rows = load_rows(file_path)
    columns = {name:[] for name in fieldnames}

    # 行转列
    for row_idx, row_dict in rows:
        for name in fieldnames:
            columns[name].append({
                "row": row_idx,
                "raw": row_dict.get(name, ""),
            })

    for col_name, items in columns.items():
        print("正在分析列：", col_name)
        cells = []

        for item in items:
            unit = value_analysis(item)
            cells.append(unit)

        column = column_analysis(cells)
        column["name"] = col_name
        DATA[col_name] = column
        print(f"分析 {col_name} 完成")

    print("分析完成")
    result = check_table(file_path, DATA)
    return result
    