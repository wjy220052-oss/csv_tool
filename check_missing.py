import csv

# 检查每列的缺失是多少，缺失包括空值和空字符串 
def is_missing(val):
    if val is None:
        return True
    s = str(val).strip().lower()
    return s in ["", "null", "nan", "none", "na","n/a"]

def check_missing(file_path):
    with open(file_path, 'r',encoding='utf-8', newline='') as file:
        reader = csv.DictReader(file)
        header = reader.fieldnames or []
        data = [row for row in reader]
        missing_count = {}
        for row in data:
            for col in header:
                if is_missing(row.get(col)):      # 有可能row中不存在col这个键
                    if col in missing_count:
                        missing_count[col] += 1
                    else:
                        missing_count[col] = 1
        return missing_count
    
if __name__ == '__main__':
    file_path = 'data/2023-11-16-2023-11-17.csv'
    missing_count = check_missing(file_path)
    print(missing_count)