# automation_rate.py
# Author: Bang Thien Nguyen
# Purpose: Build a dynamica Automation Rate Report based on Behave scenarios (automated vs manual) under features directory

import os
import re
import sys
from datetime import datetime

# Paths
# REPORT_DIR is still hardcoded as it is a constant output location
REPORT_DIR = os.path.join(os.getcwd(), "reports")

# Regex patterns
SCENARIO_PATTERN = re.compile(r'^\s*Scenario(?::| Outline:)', re.IGNORECASE)
EXAMPLES_PATTERN = re.compile(r'^\s*Examples:', re.IGNORECASE)
EXAMPLE_ROW_PATTERN = re.compile(r'^\s*\|.*\|')

def count_scenarios_in_file(file_path):
    count = 0
    in_examples = False
    skip_header = False

    try:
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

                elif in_examples and not line and not in_examples:
                    in_examples = False
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred while reading file {file_path}: {e}")
    return count

def main():
    # Improved error handling for command-line arguments
    if len(sys.argv) != 2:
        print("❌ Usage: python automation_rate.py <features_dir>")
        sys.exit(1)

    features_dir = sys.argv[1]
    
    if not os.path.exists(features_dir) or not os.path.isdir(features_dir):
        print(f"❌ Error: The '{features_dir}' directory was not found or is not a directory. Please provide a valid path.")
        sys.exit(1)
        
    # Create the reports directory if it doesn't exist
    os.makedirs(REPORT_DIR, exist_ok=True)

    total_scenarios = 0
    manual_scenarios = 0
    total_file_counts = {}
    manual_file_counts = {}

    # Iterate through all feature files in the features directory
    for root, _, files in os.walk(features_dir):
        for file_name in files:
            if file_name.endswith('.feature'):
                file_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(file_path, features_dir)

                # Count total scenarios
                total_count = count_scenarios_in_file(file_path)
                total_scenarios += total_count
                total_file_counts[relative_path] = total_count

                # Check if it's a manual test
                if "manual_tests" in file_path.lower() or "manual" in file_name.lower():
                    manual_count = total_count
                    manual_scenarios += manual_count
                    manual_file_counts[relative_path] = manual_count
    
    automated_scenarios = total_scenarios - manual_scenarios
    automation_percentage = (automated_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0

    report_time = datetime.now()
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Automation Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ width: 80%; margin: auto; padding: 20px; }}
        h1, h2, h4 {{ color: #2c3e50; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .automation-percentage {{ font-weight: bold; color: #27ae60; }}
        .timestamp {{ font-style: italic; color: #7f8c8d; }}
        .footer {{ text-align: center; margin-top: 40px; font-size: 0.9em; color: #7f8c8d; }}
    </style>
</head>
<body>
    <div class="container">
    <h1>Automation Rate Report</h1>
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

    html_content += f"""
    </table>
    <div class="footer">
        © 2025 Bang Thien Nguyen. All rights reserved.
    </div>
</body>
</html>
"""
    # Define the output path with a timestamp for the report
    filename = f"automation_rate_report_{report_time.strftime('%m-%d-%Y_%H-%M-%S')}.html"
    output_path = os.path.join(REPORT_DIR, filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"✅ Automation Rate Successfully Generated: {output_path}")


if __name__ == "__main__":
    main()