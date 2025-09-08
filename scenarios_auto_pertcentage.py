import os
import re
from datetime import datetime

# Paths
FEATURES_DIR = r"C:\my_work\firmware_repo\features"
MANUAL_TESTS_DIR = os.path.join(FEATURES_DIR, "manual_tests")
REPORT_DIR = os.path.join(os.getcwd(), "reports")

# Regex patterns
SCENARIO_PATTERN = re.compile(r'^\s*Scenario(?::| Outline:)', re.IGNORECASE)
EXAMPLES_PATTERN = re.compile(r'^\s*Examples:', re.IGNORECASE)
EXAMPLE_ROW_PATTERN = re.compile(r'^\s*\|.*\|')

def count_scenarios_in_file(file_path):
    count = 0
    in_examples = False
    skip_header = False

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            if SCENARIO_PATTERN.match(line):
                in_examples = False
                skip_header = False
                count += 1

            elif EXAMPLES_PATTERN.match(line):
                in_examples = True
                skip_header = True
                count -= 1  # remove initial Scenario Outline count

            elif in_examples and EXAMPLE_ROW_PATTERN.match(line):
                if skip_header:
                    skip_header = False
                    continue
                count += 1

            elif in_examples and line == '':
                in_examples = False

    return count

def count_scenarios_in_folder(folder_path):
    total = 0
    file_counts = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".feature"):
                file_path = os.path.join(root, file)
                file_count = count_scenarios_in_file(file_path)
                file_counts[file_path] = file_count
                total += file_count
    return total, file_counts

# Count total and manual scenarios
total_scenarios, total_file_counts = count_scenarios_in_folder(FEATURES_DIR)
manual_scenarios, manual_file_counts = count_scenarios_in_folder(MANUAL_TESTS_DIR)
automated_scenarios = total_scenarios - manual_scenarios
automation_percentage = (automated_scenarios / total_scenarios) * 100 if total_scenarios > 0 else 0

# Timestamp
report_time = datetime.now()
#timestamp_str = report_time.strftime("%Y-%m-%d_%H-%M-%S")
timestamp_str = report_time.strftime("%m-%d-%Y_%H-%M-%S")

# Ensure reports directory exists
os.makedirs(REPORT_DIR, exist_ok=True)

# Generate timestamped filename
REPORT_FILE = os.path.join(REPORT_DIR, f"automation_report_{timestamp_str}.html")

# Generate HTML report
html_content = f"""
<html>
<head>
    <title>Scenarios Automation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2F4F4F; }}
        table {{ border-collapse: collapse; width: 80%; margin-bottom: 30px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:hover {{ background-color: #f9f9f9; }}
        .timestamp {{ font-size: 0.9em; color: #555; margin-bottom: 20px; }}
        .automation-percentage {{ font-weight: bold; color: blue; }}
    </style>
</head>
<body>
    <h1>Test Automation Report</h1>
    <div class="timestamp">Report generated on: {report_time.strftime("%Y-%m-%d %H:%M:%S")}</div>

    <h4>Author: Bang Thien Nguyen</h4>
    
    <h2>Summary</h2>
    <table>
        <tr><th>Metric</th><th>Count</th></tr>
        <tr><td>Total Scenarios (including Examples rows)</td><td>{total_scenarios}</td></tr>
        <tr><td>Manual Scenarios (including Examples rows)</td><td>{manual_scenarios}</td></tr>
        <tr><td>Automated Scenarios</td><td>{automated_scenarios}</td></tr>
        <tr><td>Automation Percentage</td><td class="automation-percentage">{automation_percentage:.2f}%</td></tr>
    </table>
    
    <h2>Scenarios by Feature File</h2>
    <table>
        <tr><th>Feature File</th><th>Total Scenarios</th><th>Manual Scenarios</th><th>Automated Scenarios</th></tr>
"""

# Add per-file counts
all_files = set(total_file_counts.keys()).union(manual_file_counts.keys())
for file_path in sorted(all_files):
    total_count = total_file_counts.get(file_path, 0)
    manual_count = manual_file_counts.get(file_path, 0)
    automated_count = total_count - manual_count
    html_content += f"<tr><td>{file_path}</td><td>{total_count}</td><td>{manual_count}</td><td>{automated_count}</td></tr>\n"

html_content += """
    </table>
</body>
</html>
"""

# Write HTML report
with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ Automation Coverage Report Generated At: {REPORT_FILE}")
