from config import AUTO_CLEAN_FLAGS
def column_analysis(cells:list):
    """
    This function takes a dictionary of data and returns a dictionary of analysis results.
    """
    # Initialize the results dictionary
    basic_results = {
        "total_count": 0,
        "missing_count": 0,
        "non_missing_count": 0,
        "missing_rate": 0,
    }
    type_results = {
        "type":{
        "int": 0,
        "float": 0,
        "str": 0,
        "bool": 0,
        "date": 0,
        "date_time": 0,
        "numeric":0,
        },
        "inferred_type":None,
        "confidence":None
    }
    flags = {
        "trimmed_whitespace": 0,
        "missing_token": 0,
        "number_with_comma": 0,
        "embedded_control_char": 0,
        "empty_after_trim": 0,
        "placeholder_token": 0,
        "leading_zero": 0,
        "compact_date_format": 0,
        "ambiguous_date_format": 0,
        "non_standard_bool": 0,
    }
    examples = {
        "example":{
            "count": 0,
            "example": [],
        },
       "issue_samples": {
            key: {"count": 0, "example": []}
            for key in flags.keys()
        }
    }
    suggestions = []
    for cell in cells:
        if cell["is_missing"]:
            basic_results["missing_count"] += 1
        else:
            basic_results["non_missing_count"] += 1

        basic_results["total_count"] += 1

        if cell["type"] in type_results["type"]:
            type_results["type"][cell["type"]] += 1

        for item in cell["flags"]:
            flags[item] += 1

        if len(cell["flags"]) == 0:
            if len(examples["example"]["example"]) < 3:
                examples["example"]["count"] += 1
                examples["example"]["example"].append({
                    "row":cell["row"],
                    "value":cell["raw"]
                    })
            else:
                pass
        else:
            for ce in cell["flags"]:
                examples["issue_samples"][ce]["count"] += 1
                if len(examples["issue_samples"][ce]["example"]) < 5:
                    examples["issue_samples"][ce]["example"].append({
                        "row": cell["row"],
                        "value": cell["raw"],
                    })
    # 汇总
    basic_results["missing_rate"] = (
        basic_results["missing_count"] / basic_results["total_count"]
        if basic_results["total_count"] > 0 else 0
    )

    type_results["type"]["numeric"] = (
        type_results["type"]["int"] + type_results["type"]["float"]
    )

    infer_candidates = {
        k: v for k, v in type_results["type"].items()
        if k not in {"numeric", "missing"} and v > 0
    }

    if infer_candidates:
        inferred_type = max(infer_candidates, key=infer_candidates.get)
    else:
        inferred_type = "missing"

    type_results["inferred_type"] = inferred_type
    type_results["confidence"] = (
        f"{type_results['type'][inferred_type] / basic_results['non_missing_count']:.2f}"
        if basic_results["non_missing_count"] > 0 and inferred_type in type_results["type"]
        else "0.00"
    )

    if basic_results["missing_rate"] >= 0.3:
        suggestions.append("该列缺失率较高，分析前请先评估是否保留该列")

    if float(type_results["confidence"]) < 0.8 and inferred_type not in {"missing", "str"}:
        suggestions.append("该列数据类型推断置信度较低，请手动检查数据类型")

    for k, v in flags.items():
        if v > 0 and k in AUTO_CLEAN_FLAGS:
            suggestions.append(f"该列存在 {k} 问题，请{AUTO_CLEAN_FLAGS[k]}")

    return {
        "name": None,
        "basic_results": basic_results,
        "type_results": type_results,
        "flags": flags,
        "examples": examples,
        "suggestions": suggestions,
    }