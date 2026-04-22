"""
CSV工具测试模块（精简版）
测试不依赖pandas的模块: read_file, check_missing, check_duplicate

运行方式: python test_csv_tool.py
"""

import unittest
import os
import csv
import tempfile
import sys
import re
from io import StringIO
from datetime import datetime

# ==================== 模拟 check_type 模块中的函数 ====================

def is_strict_datetime(s: str) -> bool:
    """对于常见日期类型的数据进行识别"""
    s = s.strip()
    DATE_PATTERNS = [
        (re.compile(r"^\d{4}-\d{2}-\d{2}$"), "%Y-%m-%d"),
        (re.compile(r"^\d{4}/\d{2}/\d{2}$"), "%Y/%m/%d"),
        (re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"), "%Y-%m-%d %H:%M:%S"),
        (re.compile(r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$"), "%Y/%m/%d %H:%M:%S"),
        (re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"), "%Y-%m-%d %H:%M"),
        (re.compile(r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}$"), "%Y/%m/%d %H:%M"),
    ]
    for pattern, fmt in DATE_PATTERNS:
        if pattern.match(s):
            try:
                datetime.strptime(s, fmt)
                return True
            except ValueError:
                pass
    return False


def is_yyyymmdd(s: str) -> bool:
    """对于形如YYYYMMDD的日期类型的数据进行识别"""
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


# ==================== 手动实现测试函数（不依赖pandas）====================

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


# ==================== 导入被测试的模块 ====================

from read_file import is_valid_file, read_csv, count_rows_cols
from check_missing import is_missing, check_missing
from check_duplicate import check_duplicate


# ==================== 测试 read_file.py ====================

class TestIsValidFile(unittest.TestCase):
    """测试文件验证功能"""

    def test_file_not_exist(self):
        """测试文件不存在的情况"""
        with tempfile.TemporaryDirectory() as tmpdir:
            non_exist_file = os.path.join(tmpdir, "non_exist.csv")
            self.assertFalse(is_valid_file(non_exist_file))

    def test_not_csv_file(self):
        """测试非CSV文件"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"test")
            temp_path = f.name
        try:
            self.assertFalse(is_valid_file(temp_path))
        finally:
            os.unlink(temp_path)

    def test_empty_file(self):
        """测试空文件"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            pass
        try:
            self.assertFalse(is_valid_file(f.name))
        finally:
            os.unlink(f.name)

    def test_valid_csv_file(self):
        """测试有效的CSV文件"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'age'])
            writer.writerow(['Alice', '25'])
            temp_path = f.name
        try:
            self.assertTrue(is_valid_file(temp_path))
        finally:
            os.unlink(temp_path)


class TestLooksLikeNumber(unittest.TestCase):
    """测试数字识别功能"""

    def test_integer(self):
        self.assertTrue(looks_like_number("123"))
        self.assertTrue(looks_like_number("-123"))
        self.assertTrue(looks_like_number("+123"))

    def test_float(self):
        self.assertTrue(looks_like_number("123.45"))
        self.assertTrue(looks_like_number("-123.45"))

    def test_not_number(self):
        self.assertFalse(looks_like_number("abc"))
        self.assertFalse(looks_like_number("12.34.56"))
        self.assertFalse(looks_like_number(""))


class TestLooksLikeHeaderToken(unittest.TestCase):
    """测试表头token识别"""

    def test_valid_headers(self):
        self.assertTrue(looks_like_header_token("name"))
        self.assertTrue(looks_like_header_token("user_name"))
        self.assertTrue(looks_like_header_token("user name"))
        self.assertTrue(looks_like_header_token("Age"))

    def test_invalid_headers(self):
        self.assertFalse(looks_like_header_token("123"))
        self.assertFalse(looks_like_header_token(""))
        self.assertFalse(looks_like_header_token("2024-01-01"))


class TestDetectHeader(unittest.TestCase):
    """测试表头检测功能"""

    def test_has_header(self):
        """测试有表头的文件"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'age', 'city'])
            writer.writerow(['Alice', '25', 'Beijing'])
            writer.writerow(['Bob', '30', 'Shanghai'])
            temp_path = f.name
        try:
            self.assertTrue(detect_header(temp_path))
        finally:
            os.unlink(temp_path)

    def test_no_header(self):
        """测试无表头的文件"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['1', '2', '3'])
            writer.writerow(['4', '5', '6'])
            temp_path = f.name
        try:
            result = detect_header(temp_path)
            self.assertFalse(result)
        finally:
            os.unlink(temp_path)


class TestReadCsv(unittest.TestCase):
    """测试CSV读取功能"""

    def test_read_with_header(self):
        """测试读取有表头的CSV"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'age', 'city'])
            writer.writerow(['Alice', '25', 'Beijing'])
            temp_path = f.name
        try:
            header = read_csv(temp_path)
            self.assertEqual(header, ['name', 'age', 'city'])
        finally:
            os.unlink(temp_path)

    def test_read_empty_file(self):
        """测试读取空文件"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', newline='', encoding='utf-8') as f:
            pass
        try:
            header = read_csv(f.name)
            self.assertIsNone(header)
        finally:
            os.unlink(f.name)


class TestCountRowsCols(unittest.TestCase):
    """测试行列统计功能"""

    def test_count_rows_cols(self):
        """测试正确统计行数和列数"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'age', 'city'])
            writer.writerow(['Alice', '25', 'Beijing'])
            writer.writerow(['Bob', '30', 'Shanghai'])
            temp_path = f.name
        try:
            rows, cols = count_rows_cols(temp_path)
            self.assertEqual(rows, 2)
            self.assertEqual(cols, 3)
        finally:
            os.unlink(temp_path)


# ==================== 测试 check_missing.py ====================

class TestIsMissing(unittest.TestCase):
    """测试缺失值识别"""

    def test_missing_values(self):
        self.assertTrue(is_missing(None))
        self.assertTrue(is_missing(""))
        self.assertTrue(is_missing("null"))
        self.assertTrue(is_missing("NULL"))
        self.assertTrue(is_missing("nan"))
        self.assertTrue(is_missing("NaN"))
        self.assertTrue(is_missing("none"))
        self.assertTrue(is_missing("na"))
        self.assertTrue(is_missing("N/A"))
        self.assertTrue(is_missing("  null  "))

    def test_not_missing_values(self):
        self.assertFalse(is_missing("value"))
        self.assertFalse(is_missing("0"))
        self.assertFalse(is_missing("false"))


class TestCheckMissing(unittest.TestCase):
    """测试缺失值检查功能"""

    def test_check_missing(self):
        """测试检查缺失值"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'age'])
            writer.writerow(['Alice', '25'])
            writer.writerow(['', '30'])
            writer.writerow(['Bob', 'null'])
            temp_path = f.name
        try:
            result = check_missing(temp_path)
            self.assertIn('name', result)
            self.assertIn('age', result)
            self.assertEqual(result['name'], 1)
            self.assertEqual(result['age'], 1)
        finally:
            os.unlink(temp_path)

    def test_no_missing(self):
        """测试没有缺失值的情况"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'age'])
            writer.writerow(['Alice', '25'])
            writer.writerow(['Bob', '30'])
            temp_path = f.name
        try:
            result = check_missing(temp_path)
            self.assertIsInstance(result, dict)
        finally:
            os.unlink(temp_path)


# ==================== 测试 check_duplicate.py ====================

class TestCheckDuplicate(unittest.TestCase):
    """测试重复行检查功能"""

    def test_no_duplicates(self):
        """测试没有重复行"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'age'])
            writer.writerow(['Alice', '25'])
            writer.writerow(['Bob', '30'])
            temp_path = f.name
        try:
            result = check_duplicate(temp_path)
            self.assertEqual(result, 0)
        finally:
            os.unlink(temp_path)

    def test_with_duplicates(self):
        """测试有重复行"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'age'])
            writer.writerow(['Alice', '25'])
            writer.writerow(['Alice', '25'])
            writer.writerow(['Bob', '30'])
            temp_path = f.name
        try:
            result = check_duplicate(temp_path)
            self.assertEqual(result, 1)
        finally:
            os.unlink(temp_path)

    def test_multiple_duplicates(self):
        """测试多个重复行"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'age'])
            writer.writerow(['Alice', '25'])
            writer.writerow(['Alice', '25'])
            writer.writerow(['Alice', '25'])
            writer.writerow(['Bob', '30'])
            temp_path = f.name
        try:
            result = check_duplicate(temp_path)
            self.assertEqual(result, 2)
        finally:
            os.unlink(temp_path)


# ==================== 测试 check_type 模拟函数 ====================

class TestIsStrictDatetime(unittest.TestCase):
    """测试严格日期时间识别"""

    def test_valid_dates(self):
        self.assertTrue(is_strict_datetime("2024-01-15"))
        self.assertTrue(is_strict_datetime("2024/01/15"))
        self.assertTrue(is_strict_datetime("2024-01-15 10:30:00"))
        self.assertTrue(is_strict_datetime("2024/01/15 10:30"))

    def test_invalid_dates(self):
        self.assertFalse(is_strict_datetime("2024-13-15"))
        self.assertFalse(is_strict_datetime("not a date"))
        self.assertFalse(is_strict_datetime("20240115"))


class TestIsYyyymmdd(unittest.TestCase):
    """测试YYYYMMDD格式识别"""

    def test_valid_yyyymmdd(self):
        self.assertTrue(is_yyyymmdd("20240115"))
        self.assertTrue(is_yyyymmdd("19991231"))

    def test_invalid_yyyymmdd(self):
        self.assertFalse(is_yyyymmdd("20241315"))
        self.assertFalse(is_yyyymmdd("20240132"))
        self.assertFalse(is_yyyymmdd("2024-01-15"))
        self.assertFalse(is_yyyymmdd("not a date"))
        self.assertFalse(is_yyyymmdd("18990101"))


# ==================== 集成测试 ====================

class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_full_workflow(self):
        """测试完整的工作流程"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'age'])
            writer.writerow(['1', 'Alice', '25'])
            writer.writerow(['2', 'Bob', '30'])
            writer.writerow(['3', 'Charlie', '35'])
            temp_path = f.name
        try:
            self.assertTrue(is_valid_file(temp_path))

            header = read_csv(temp_path)
            self.assertEqual(header, ['id', 'name', 'age'])

            rows, cols = count_rows_cols(temp_path)
            self.assertEqual(rows, 3)
            self.assertEqual(cols, 3)

            missing = check_missing(temp_path)
            self.assertEqual(missing, {})

            duplicates = check_duplicate(temp_path)
            self.assertEqual(duplicates, 0)

        finally:
            os.unlink(temp_path)

    def test_complex_csv(self):
        """测试包含缺失值和重复行的复杂CSV"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'age'])
            writer.writerow(['1', 'Alice', '25'])
            writer.writerow(['2', '', '30'])
            writer.writerow(['3', 'Bob', 'null'])
            writer.writerow(['1', 'Alice', '25'])
            temp_path = f.name
        try:
            self.assertTrue(is_valid_file(temp_path))

            header = read_csv(temp_path)
            self.assertIsNotNone(header)

            rows, cols = count_rows_cols(temp_path)
            self.assertEqual(rows, 4)
            self.assertEqual(cols, 3)

            missing = check_missing(temp_path)
            self.assertGreaterEqual(missing.get('name', 0), 1)
            self.assertGreaterEqual(missing.get('age', 0), 1)

            duplicates = check_duplicate(temp_path)
            self.assertEqual(duplicates, 1)

        finally:
            os.unlink(temp_path)


# ==================== 主入口 ====================

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestIsValidFile,
        TestLooksLikeNumber,
        TestLooksLikeHeaderToken,
        TestDetectHeader,
        TestReadCsv,
        TestCountRowsCols,
        TestIsMissing,
        TestCheckMissing,
        TestCheckDuplicate,
        TestIsStrictDatetime,
        TestIsYyyymmdd,
        TestIntegration,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)
