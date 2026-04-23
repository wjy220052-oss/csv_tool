import unicodedata

def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"

def _safe_confidence(col: dict) -> str:
    conf = col.get("type_results", {}).get("confidence", 0)
    try:
        return f"{float(conf):.2f}"
    except (TypeError, ValueError):
        return "0.00"

def _get_flag_counts(col: dict) -> dict:
    issue_samples = col.get("examples", {}).get("issue_samples", {})
    result = {}
    for flag, info in issue_samples.items():
        result[flag] = info.get("count", 0)
    return result

def print_table_summary(report: dict) -> None:
    print("=" * 72)
    print("CSV 概况分析报告")
    print("=" * 72)
    print(f"文件路径       : {report.get('file_path', '')}")
    print(f"总行数         : {report.get('row_count', 0)}")
    print(f"总列数         : {report.get('column_count', 0)}")
    print(f"重复行数量     : {report.get('duplicate_row_count', 0)}")

    header = report.get("header")
    if header:
        print(f"列名           : {', '.join(header)}")
    else:
        print("列名           : 未检测到表头或使用了自动列名")

    print()


def display_width(text: str) -> int:
    text = str(text)
    width = 0
    for ch in text:
        width += 2 if unicodedata.east_asian_width(ch) in {"F", "W"} else 1
    return width

def pad_display(text: str, width: int) -> str:
    text = str(text)
    return text + " " * max(0, width - display_width(text))

def print_column_overview(report: dict) -> None:
    print("-" * 72)
    print("列概览")
    print("-" * 72)

    columns = report.get("columns", {})
    headers = ["列名", "主类型", "置信度", "缺失值", "缺失率", "问题数"]
    rows = []

    for col_name, col in columns.items():
        basic = col.get("basic_results", {})
        type_result = col.get("type_results", {})
        flag_counts = _get_flag_counts(col)

        missing = basic.get("missing_count", 0)
        missing_rate = basic.get("missing_rate", 0)
        if isinstance(missing_rate, dict):
            missing_rate = list(missing_rate.values())[0] if missing_rate else 0

        issue_count = sum(v for v in flag_counts.values())

        rows.append([
            col_name,
            str(type_result.get("inferred_type", "")),
            _safe_confidence(col),
            str(missing),
            _pct(missing_rate if isinstance(missing_rate, (int, float)) else 0),
            str(issue_count),
        ])

    col_widths = [display_width(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], display_width(cell))

    col_widths = [w + 2 for w in col_widths]

    header_line = " | ".join(
        pad_display(headers[i], col_widths[i]) for i in range(len(headers))
    )
    sep_line = "-+-".join("-" * col_widths[i] for i in range(len(headers)))

    print(header_line)
    print(sep_line)

    for row in rows:
        print(" | ".join(
            pad_display(row[i], col_widths[i]) for i in range(len(row))
        ))
    print()

def print_column_detail(col: dict, max_issue_examples: int = 3) -> None:
    name = col.get("name", "")
    basic = col.get("basic_results", {})
    type_result = col.get("type_results", {})
    examples = col.get("examples", {})
    issue_samples = examples.get("issue_samples", {})
    suggestions = col.get("suggestions", [])

    total = basic.get("total_count", 0)
    missing = basic.get("missing_count", 0)
    missing_rate = basic.get("missing_rate", 0)
    if isinstance(missing_rate, dict):
        missing_rate = list(missing_rate.values())[0] if missing_rate else 0

    print(f"[{name}]")
    print(f"主类型         : {type_result.get('inferred_type', '')}")
    print(f"置信度         : {_safe_confidence(col)}")
    print(f"缺失值         : {missing}/{total} ({_pct(missing_rate if isinstance(missing_rate, (int, float)) else 0)})")

    type_counts = type_result.get("type", {})
    if type_counts:
        print("类型分布       :")
        for k, v in type_counts.items():
            if v:
                print(f"  - {k}: {v}")

    normal_examples = examples.get("example", {}).get("example", [])
    if normal_examples:
        print("正常样例       :")
        for item in normal_examples[:3]:
            if isinstance(item, dict):
                print(f"  - row {item.get('row')}: {item.get('value')}")
            else:
                print(f"  - {item}")

    has_issue = False
    for flag, info in issue_samples.items():
        count = info.get("count", 0)
        if count > 0:
            if not has_issue:
                print("问题样例       :")
                has_issue = True
            print(f"  - {flag}: {count}")
            for item in info.get("example", [])[:max_issue_examples]:
                print(f"      row {item.get('row')}: {item.get('value')}")

    if suggestions:
        print("建议           :")
        for s in suggestions:
            print(f"  - {s}")

    print()

def print_report(report: dict, show_all_columns: bool = False, max_issue_examples: int = 3) -> None:
    print_table_summary(report)
    print_column_overview(report)

    columns = report.get("columns", {})
    if not columns:
        return

    print("-" * 72)
    print("列详细信息")
    print("-" * 72)

    for _, col in columns.items():
        issue_samples = col.get("examples", {}).get("issue_samples", {})
        has_issue = any(info.get("count", 0) > 0 for info in issue_samples.values())

        if show_all_columns or has_issue:
            print_column_detail(col, max_issue_examples=max_issue_examples)

    table_suggestions = report.get("suggestions", [])
    if table_suggestions:
        print("-" * 72)
        print("表级建议")
        print("-" * 72)
        for s in table_suggestions:
            print(f"  - {s}")