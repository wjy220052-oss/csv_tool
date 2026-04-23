import argparse
from main import main
from display_report import print_report

def build_parser():
    parser = argparse.ArgumentParser(
        description="CSV 概况分析 CLI：输出列名、缺失值、重复行、类型推断、问题样例和建议"
    )
    parser.add_argument(
        "csv_file",
        help="要分析的 CSV 文件路径"
    )
    parser.add_argument(
        "--show-all-columns",
        action="store_true",
        help="显示所有列的详细信息；默认只显示存在问题的列"
    )
    parser.add_argument(
        "--max-issue-examples",
        type=int,
        default=3,
        help="每种问题最多显示多少个样例，默认 3"
    )
    return parser

def cli_main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        report = main(args.csv_file)
        print_report(
            report,
            show_all_columns=args.show_all_columns,
            max_issue_examples=args.max_issue_examples,
        )
    except Exception as e:
        print(f"错误: {e}")
        raise SystemExit(1)

if __name__ == "__main__":
    cli_main()