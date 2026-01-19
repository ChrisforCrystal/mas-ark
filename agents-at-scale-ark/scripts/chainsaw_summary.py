import json
import os
import sys
import argparse
import subprocess

def summarize_chainsaw_report(report_path):
    if not os.path.exists(report_path):
        print(f"Report file not found: {report_path}")
        return

    with open(report_path) as f:
        data = json.load(f)

    print(f"{'Test Name':40} | {'Result'}")
    print("-" * 55)
    for test in data.get("tests", []):
        test_name = test.get("name", "Unknown")
        failed = False
        for step in test.get("steps", []):
            for op in step.get("operations", []):
                if op.get("type") == "error":
                    failed = True
        result = "✅ Passed" if not failed else "❌ Failed"
        print(f"{test_name:40} | {result}")

def print_evaluations_table():
    try:
        # Compose the full jq command for the desired table
        jq_cmd = (
            '.items[] | select(.status.evaluations != null) | '
            '([.metadata.name] + (.status.evaluations[] | [.score // "N/A", .evaluatorName // "N/A"])) | @tsv'
        )
        result = subprocess.run(
            ["kubectl", "get", "queries", "-A",  "-o", "json"],
            capture_output=True, text=True, check=True
        )
        evals = subprocess.run(
            ["jq", "-r", jq_cmd],
            input=result.stdout, capture_output=True, text=True, check=True
        )
        lines = evals.stdout.strip().split('\n')
        print("\nEvaluation                | Score     | Evaluator")
        print("-" * 50)
        for line in lines:
            if not line.strip():
                continue
            parts = line.split('\t')
            # Defensive: pad if missing
            while len(parts) < 3:
                parts.append("N/A")
            print(f"{parts[0]:25} | {parts[1]:8} | {parts[2]}")
    except Exception as e:
        print(f"Error fetching evaluations: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize Chainsaw test results and optionally append evaluation info from Queries.")
    parser.add_argument("report_path", nargs="?", default="/tmp/coverage-reports/chainsaw-report.json", help="Path to Chainsaw JSON report")
    parser.add_argument("--append-evals", action="store_true", help="Append evaluation summary table from Queries")
    args = parser.parse_args()

    summarize_chainsaw_report(args.report_path)

    if args.append_evals:
        print("\n")
        print_evaluations_table() 