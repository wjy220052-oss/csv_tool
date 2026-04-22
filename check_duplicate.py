import csv
from collections import Counter

# 检查重复行数量
def check_duplicate(file_path):
    with open(file_path, 'r',encoding='utf-8', newline='') as file:
        reader = csv.DictReader(file)
        filenames = reader.fieldnames or []
        data = list(reader)  # 直接读取所有行
        
        # 原来真的给每列生成一个唯一的标记了……
        row_counter = Counter()  # Counter是collections模块中的一个类，用于统计可哈希对象的个数，本质上是一个特殊的字典，键是元素，值是统计数值，默认是0
        for row in data:
            # 将整行转换为可哈希的元组
            row_tuple = tuple((col, row.get(col, '')) for col in filenames)
            row_counter[row_tuple] += 1
        
        # 计算重复行数量（出现次数>1的行，次数-1的总和）
        duplicate_count = sum(count - 1 for count in row_counter.values() if count > 1)
        
        return duplicate_count

if __name__ == '__main__':
    file_path = 'data.csv'
    duplicate_count = check_duplicate(file_path)
    print(f"重复行数量: {duplicate_count}")