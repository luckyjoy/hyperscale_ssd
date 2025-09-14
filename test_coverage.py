# test_coverage.py
# Author: Bang Thien Nguyen
# Purpose: Genrate HTML Test Coverage Reports based on the comparisons of Behave scenarios found in features directory and requirements.csv

import os
import sys
import re
from datetime import datetime


def parse_feature_file(file_path):
    """
    Parses a single Behave .feature file to extract the feature and scenarios.
    Returns a dictionary of feature data.
    """
    feature_data = {
        'title': os.path.basename(file_path),
        'description': '',
        'scenarios': []
    }
    current_scenario = None
    in_examples = False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ Error: Feature file not found at '{file_path}'.")
        return None
    except PermissionError:
        print(f"❌ Error: Permission denied when trying to read '{file_path}'.")
        return None
    except Exception as e:
        print(f"❌ An unexpected error occurred while reading '{file_path}': {e}")
        return None
    

    for line in lines:
        line = line.strip()
        if not line:
            in_examples = False
            continue

        # Check for Feature
        feature_match = re.match(r'^Feature: (.*)$', line)
        if feature_match:
            feature_data['description'] = feature_match.group(1)
            continue

        # Check for Scenario or Scenario Outline
        scenario_match = re.match(r'^Scenario(?: Outline)?: (.*)$', line)
        if scenario_match:
            if current_scenario:
                feature_data['scenarios'].append(current_scenario)
            
            scenario_name = scenario_match.group(1)
            req_ids = re.findall(r'<REQ_SSD_(\d+)>', scenario_name)
            
            current_scenario = {
                'name': scenario_name,
                'steps': [],
                'examples': [],
                'req_ids': [f"REQ_SSD_{rid}" for rid in req_ids]
            }
            in_examples = False
            continue

        # Check for Steps (Given, When, Then, And, But)
        step_match = re.match(r'^(Given|When|Then|And|But)\s+(.*)$', line)
        if step_match and current_scenario:
            current_scenario['steps'].append(line)
            in_examples = False
            continue

        # Check for Examples
        if line.lower() == 'examples:':
            in_examples = True
            continue
        
        # Parse Examples table
        if in_examples and current_scenario:
            current_scenario['examples'].append(line)
    
    if current_scenario:
        feature_data['scenarios'].append(current_scenario)
        
    return feature_data


def parse_requirements_csv(file_path):
    """Parses a file containing requirements in 'ID: Description' format, ignoring comment lines."""
    requirements = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Find the header row to skip it
            header_found = False
            for line in lines:
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith('#'):
                    if 'requirement_id' in stripped_line and 'requirement_description' in stripped_line:
                        header_found = True
                    break

            for line in lines:
                line = line.strip()
                # Skip empty lines, comments, and the header line if found
                if not line or line.startswith('#'):
                    continue
                if header_found and 'requirement_id' in line and 'requirement_description' in line:
                    header_found = False
                    continue

                if ':' in line:
                    try:
                        req_id, description = line.split(':', 1)
                        req_id = req_id.strip()
                        description = description.strip()
                        if req_id and description:
                            requirements[req_id] = description
                    except ValueError:
                        print(f"⚠️ Warning: Skipping malformed line: '{line}'")
    except FileNotFoundError:
        print(f"❌ Error: Requirements CSV file not found at '{file_path}'.")
        return None
    except Exception as e:
        print(f"❌ An unexpected error occurred while reading the requirements file: {e}")
        return None
    return requirements


def generate_validation_plan_html(requirements, features, report_date, author):
    """
    Generates the validation plan HTML from requirements and parsed feature files.
    """
    # Build traceability data
    traceability_data = {}
    uncovered_requirements_list = []
    covered_requirements_count = 0
    total_test_cases = 0

    for req_id, description in requirements.items():
        traceability_data[req_id] = {
            'description': description,
            'scenarios': []
        }

    for feature in features:
        for scenario in feature['scenarios']:
            for req_id in scenario['req_ids']:
                if req_id in traceability_data:
                    traceability_data[req_id]['scenarios'].append({
                        'feature': feature['title'],
                        'scenario': scenario['name']
                    })
                else:
                    print(f"⚠️ Warning: Found scenario with unlisted requirement ID: {req_id} in {feature['title']}.")

    sorted_req_ids = sorted(traceability_data.keys(), key=lambda x: int(x.split('_')[-1]) if x.split('_')[-1].isdigit() else 0)

    # Calculate summary metrics
    total_requirements = len(requirements)
    for req_id in sorted_req_ids:
        entry = traceability_data[req_id]
        if entry['scenarios']:
            covered_requirements_count += 1
            total_test_cases += len(entry['scenarios'])
        else:
            uncovered_requirements_list.append(req_id)

    test_coverage_percentage = (covered_requirements_count / total_requirements) * 100 if total_requirements > 0 else 0

    # Determine coverage color
    coverage_color = 'text-green-600'
    if test_coverage_percentage < 50:
        coverage_color = 'text-red-600'
    elif 50 <= test_coverage_percentage <= 80:
        coverage_color = 'text-yellow-600'
    
    # Build HTML for the summary section
    uncovered_reqs_html = ""
    if uncovered_requirements_list:
        uncovered_reqs_html = """
            <h3 class="text-xl font-semibold text-gray-900 mb-2">Uncovered Requirements</h3>
            <ul class="list-disc list-inside text-gray-600 mb-4">
        """
        for req_id in uncovered_requirements_list:
            uncovered_reqs_html += f"<li>{req_id}: {requirements[req_id]}</li>"
        uncovered_reqs_html += "</ul>"


    summary_html = f"""
    <section id="summary" class="mb-8 p-6 bg-white rounded-xl shadow-md">
        <h2 class="text-2xl font-semibold text-gray-900 mb-4">Coverage Summary</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="bg-gray-50 p-4 rounded-lg">
                <p class="text-sm font-medium text-gray-500">Total Requirements</p>
                <p class="text-xl font-bold text-gray-900">{total_requirements}</p>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
                <p class="text-sm font-medium text-gray-500">Covered Requirements</p>
                <p class="text-xl font-bold text-gray-900">{covered_requirements_count}</p>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
                <p class="text-sm font-medium text-gray-500">Test Coverage</p>
                <p class="text-xl font-bold {coverage_color}">{test_coverage_percentage:.2f}%</p>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
                <p class="text-sm font-medium text-gray-500">Total Test Cases</p>
                <p class="text-xl font-bold text-gray-900">{total_test_cases}</p>
            </div>
        </div>
        <div class="mt-6">
            {uncovered_reqs_html}
        </div>
    </section>
    """

    # Build HTML for the traceability table
    traceability_table_html = """
    <p class="text-gray-600 mb-4">This matrix links each product requirement to the Behave scenarios that validate it, ensuring comprehensive test coverage.</p>
    <div class="overflow-x-auto rounded-lg shadow-sm border border-gray-200">
        <table class="min-w-full bg-white rounded-lg">
            <thead class="bg-gray-100">
                <tr>
                    <th class="px-6 py-3 text-left text-sm font-semibold text-gray-700 uppercase">Requirement ID</th>
                    <th class="px-6 py-3 text-left text-sm font-semibold text-gray-700 uppercase">Description</th>
                    <th class="px-6 py-3 text-left text-sm font-semibold text-gray-700 uppercase">Feature File</th>
                    <th class="px-6 py-3 text-left text-sm font-semibold text-gray-700 uppercase">Scenario(s)</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
    """
    for req_id in sorted_req_ids:
        entry = traceability_data[req_id]
        scenarios = entry['scenarios']
        
        if not scenarios:
            traceability_table_html += f"""
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 font-medium text-gray-700">{req_id}</td>
                <td class="px-6 py-4 text-gray-600">{entry['description']}</td>
                <td class="px-6 py-4 text-gray-600 italic text-red-500">No coverage</td>
                <td class="px-6 py-4 text-gray-600 italic">N/A</td>
            </tr>
            """
            continue
        
        for i, scenario_entry in enumerate(scenarios):
            traceability_table_html += "<tr>\n"
            if i == 0:
                traceability_table_html += f"                <td rowspan=\"{len(scenarios)}\" class=\"px-6 py-4 font-medium text-gray-700\">{req_id}</td>\n"
                traceability_table_html += f"                <td rowspan=\"{len(scenarios)}\" class=\"px-6 py-4 text-gray-600\">{entry['description']}</td>\n"
            
            traceability_table_html += f"                <td class=\"px-6 py-4 text-gray-600\">{scenario_entry['feature']}</td>\n"
            traceability_table_html += f"                <td class=\"px-6 py-4 text-gray-600\">{scenario_entry['scenario']}</td>\n"
            traceability_table_html += "            </tr>\n"
            
    traceability_table_html += """
            </tbody>
        </table>
    </div>
    """

    # Final HTML with a simplified structure as there's no metadata file
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Coverage Report</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            background-color: #f8fafc;
        }}
        .resizable-container {{
            display: flex;
            min-height: 100vh;
        }}
        #toc-panel {{
            min-width: 200px;
            max-width: 50%;
        }}
        #resize-bar {{
            width: 8px;
            cursor: ew-resize;
            background-color: #e2e8f0;
            transition: background-color 0.2s ease;
        }}
        #resize-bar:hover {{
            background-color: #cbd5e1;
        }}
        #content-panel {{
            flex-grow: 1;
            overflow-y: auto;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        td {{
            word-break: break-all;
        }}
    </style>
</head>
<body class="bg-gray-100 text-gray-800">

    <div class="resizable-container">
        <!-- Main Content Panel -->
        <div id="content-panel" class="flex-1 p-8 overflow-y-auto">
            <header class="bg-white rounded-xl shadow-lg p-6 mb-8">
                <h1 class="text-4xl font-extrabold text-gray-900">Test Coverage Report</h1>
                <div class="text-sm text-gray-500 mt-2">
                    <p>Report Date: {report_date}</p>
                    <p>Author: {author}</p>
                </div>
            </header>
            {summary_html}
            <section id="traceability-matrix" class="mb-8 p-6 bg-white rounded-xl shadow-md">
                <h2 class="text-2xl font-semibold text-gray-900 mb-4">Traceability Matrix</h2>
                {traceability_table_html}
            </section>
        </div>
    </div>
    <div class="footer">
        © 2025 Bang Thien Nguyen. All rights reserved.
    </div>
</body>
</html>
    """
    return html_content


def main():
    """Main function to read data and generate the HTML report."""
    if len(sys.argv) != 3:
        print("❌ Usage: python test_coverage.py <requirements_csv_path> <features_dir>")
        sys.exit(1)

    requirements_csv_path = sys.argv[1]
    features_dir_path = sys.argv[2]

    if not os.path.isfile(requirements_csv_path):
        print(f"❌ Error: Requirements CSV file not found at '{requirements_csv_path}'.")
        sys.exit(1)

    if not os.path.isdir(features_dir_path):
        print(f"❌ Error: Features directory not found or is not a directory at '{features_dir_path}'.")
        sys.exit(1)

    try:
        # Parse requirements from CSV
        requirements = parse_requirements_csv(requirements_csv_path)
        if requirements is None:
            sys.exit(1)
        if not requirements:
            print(f"❌ Error: No valid requirements found in the CSV file '{requirements_csv_path}'. Please check the column headers and data.")
            sys.exit(1)

        # Parse feature files
        features = []
        feature_files_found = False
        for filename in sorted(os.listdir(features_dir_path)):
            if filename.endswith('.feature'):
                feature_files_found = True
                feature_path = os.path.join(features_dir_path, filename)
                parsed_feature = parse_feature_file(feature_path)
                if parsed_feature:
                    features.append(parsed_feature)

        if not feature_files_found:
            print(f"❌ Error: No .feature files found in the directory '{features_dir_path}'.")
            sys.exit(1)

        # Set output path to the reports folder
        output_dir = os.path.join(os.getcwd(), 'reports')
        os.makedirs(output_dir, exist_ok=True)
        
        # Add timestamp to the filename
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_file_name = f'test_coverage_report_{timestamp}.html'
        output_file_path = os.path.join(output_dir, output_file_name)

        if os.path.exists(output_file_path):
            print(f"⚠️ Warning: Output file already exists and will be overwritten: {output_file_path}")

        report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        author = "Bang Nguyen, ontario1998@gmail.com"
        html_output = generate_validation_plan_html(requirements, features, report_date, author)
        
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(html_output)

        print(f"✅ Test Coverage Successfully Generated: {output_file_path}")
    
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
