import pandas as pd
import re
import os
import sys
import html
from datetime import datetime

def calculate_test_coverage(requirements_csv_path, feature_dir=None, output_dir="reports"):
    try:
        req_df = pd.read_csv(requirements_csv_path)
        if "requirement_id" not in req_df.columns:
            print("Error: requirements CSV must contain 'requirement_id' column")
            return
        all_requirements = set(req_df['requirement_id'].dropna())
    except FileNotFoundError:
        print(f"Error: Requirements file '{requirements_csv_path}' not found.")
        return
    except Exception as e:
        print(f"Error reading requirements file: {e}")
        return

    # Default feature_dir to ./features if not provided
    if feature_dir is None:
        feature_dir = os.path.join(os.getcwd(), "features")

    def extract_tags_from_feature(file_path):
        tags_found = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    decoded_line = html.unescape(line)
                    tags = re.findall(r"<REQ_[A-Z]+_\d+>", decoded_line)
                    tags_found.update(tag.strip("<>") for tag in tags)
        except Exception as e:
            print(f"Warning: Could not read {file_path} due to error: {e}")
        return tags_found

    if not os.path.exists(feature_dir):
        print(f"Error: Feature directory '{feature_dir}' does not exist.")
        return

    covered_tags = set()
    for root, _, files in os.walk(feature_dir):
        for filename in files:
            if filename.endswith(".feature") or filename.endswith(".feature.txt"):
                full_path = os.path.join(root, filename)
                covered_tags.update(extract_tags_from_feature(full_path))

    covered_count = len(covered_tags & all_requirements)
    total_requirements = len(all_requirements)
    coverage_percentage = (covered_count / total_requirements) * 100 if total_requirements > 0 else 0
    uncovered_requirements = all_requirements - covered_tags

    # If CSV has descriptions, map uncovered reqs
    uncovered_with_desc = []
    if "requirement_description" in req_df.columns:
        desc_map = dict(zip(req_df['requirement_id'], req_df['requirement_description']))
        for req in sorted(uncovered_requirements):
            uncovered_with_desc.append((req, desc_map.get(req, "No description available")))
    else:
        uncovered_with_desc = [(req, "No description available") for req in sorted(uncovered_requirements)]

    # Ensure reports directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
    output_html = os.path.join(output_dir, f"coverage_report_{timestamp}.html")

    # Write HTML report using template style
    try:
        with open(output_html, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Test Coverage Report</title>
    <style>
        body { font-family: sans-serif; }
        h1, h2 { color: #333; }
        .coverage-percentage { color: red; font-weight: bold; }
        .total-test-cases { color: blue; font-weight: bold; }
        .uncovered-requirements li { color: red; }
    </style>
</head>
<body>
""")
            f.write("<h1>Test Coverage Report</h1>\n")
            f.write(f"<p><strong>Report Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>\n")
            f.write('<p class="report-author">Author: Bang Nguyen, <a href="mailto:ontario1998@gmail.com">ontario1998@gmail.com</a></p>\n')

            f.write("<h2>Coverage Summary</h2>\n")
            f.write(f"<p>Total Requirements: {total_requirements}</p>\n")
            f.write(f"<p>Covered Requirements: {covered_count}</p>\n")
            f.write(f"<p class=\"coverage-percentage\">Test Coverage: {coverage_percentage:.2f}%</p>\n")
            f.write(f"<p class=\"total-test-cases\">Total Test Cases: {len(covered_tags)}</p>\n")

            f.write("<h2>Uncovered Requirements</h2>\n<ul class=\"uncovered-requirements\">\n")
            for req, desc in uncovered_with_desc:
                f.write(f"<li><strong>{req}:</strong> {desc}</li>\n")
            f.write("</ul>\n</body></html>")
        print(f"✅ Test Coverage Report Saved To: {output_html}")
    except Exception as e:
        print(f"Error writing HTML report: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_coverage.py <path_to_requirements_csv>")
    else:
        requirements_csv_path = sys.argv[1]
        # feature_dir will default to ./features relative to current working directory
        calculate_test_coverage(requirements_csv_path)

