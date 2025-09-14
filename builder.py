# builder.py
# Author: Bang Thien Nguyen
# Purpose: Build a dynamic and comprehensive Validation Plan based on input metadata validation.json and Behave scenarios under features directory

import json
import os
import sys
import re

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
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            in_examples = False
            continue

        # Feature
        feature_match = re.match(r'^Feature: (.*)$', line)
        if feature_match:
            feature_data['description'] = feature_match.group(1)
            continue

        # Scenario
        scenario_match = re.match(r'^Scenario(?: Outline)?: (.*)$', line)
        if scenario_match:
            if current_scenario:
                feature_data['scenarios'].append(current_scenario)
            
            scenario_name = scenario_match.group(1)
            # Find requirement IDs, e.g., <REQ_COM_01> or <REQ_SSD_123>
            req_ids = re.findall(r'(REQ_[A-Z_0-9]+)', scenario_name)
            
            current_scenario = {
                'name': scenario_name,
                'steps': [],
                'examples': [],
                'req_ids': req_ids
            }
            in_examples = False
            continue

        # Steps
        step_match = re.match(r'^(Given|When|Then|And|But)\s+(.*)$', line)
        if step_match and current_scenario:
            step_text = step_match.group(0)
            formatted_step = re.sub(r'<([^>]+)>', r'<span class="text-blue-600 font-bold">\1</span>', step_text)
            current_scenario['steps'].append(formatted_step)
            in_examples = False
            continue

        # Examples
        if line.lower() == 'examples:':
            in_examples = True
            continue
        
        if in_examples and current_scenario:
            formatted_example = re.sub(r'<([^>]+)>', r'<span class="text-blue-600 font-bold">\1</span>', line)
            current_scenario['examples'].append(formatted_example)
    
    if current_scenario:
        feature_data['scenarios'].append(current_scenario)
        
    return feature_data


def get_value(data, possible_keys, default=None):
    for key in possible_keys:
        if key in data:
            return data[key]
    return default


def build_feature_sections(features):
    """Builds HTML content and TOC links for a list of parsed features."""
    sections = ""
    toc_links = ""

    for feature in features:
        feature_id = re.sub(r'[^a-z0-9]+', '-', feature['title'].lower()).strip('-')
        toc_links += f"          <li><a href=\"#{feature_id}\" class=\"block p-2 rounded hover:bg-gray-200 transition-colors duration-150\">{feature['title']}</a></li>\n"
        
        sections += f'<details id="{feature_id}" class="mb-8 bg-white rounded-xl shadow-md" open>\n'
        sections += f'  <summary class="flex items-center justify-between cursor-pointer px-6 py-4 text-2xl font-semibold text-gray-900 hover:text-blue-700 transition-colors duration-150">\n'
        sections += f'    {feature["title"]}\n'
        sections += f'    <span class="chevron transition-transform duration-300">▶</span>\n'
        sections += f'  </summary>\n'
        sections += f'  <div class="p-6 border-t border-gray-200">\n'
        sections += f"    <p class=\"text-gray-600 mb-6\"><strong>Feature:</strong> {feature['description']}</p>\n"
        
        for scenario in feature['scenarios']:
            scenario_summary = scenario['name'].replace('<', '&lt;').replace('>', '&gt;')
            sections += f"    <details class=\"mb-4 p-4 rounded-lg bg-gray-50 border border-gray-200 hover:shadow-md transition-shadow duration-200\">\n"
            sections += f"      <summary class=\"cursor-pointer font-bold text-blue-800 hover:text-blue-600 transition-colors duration-150\">{scenario_summary}</summary>\n"
            sections += f"      <div class=\"mt-4 pl-4 border-l-2 border-gray-300\">\n"
            sections += f"        <ul class=\"list-disc list-inside space-y-1 text-sm text-gray-700\">\n"
            for step in scenario['steps']:
                sections += f"          <li>{step}</li>\n"
            if scenario['examples']:
                sections += f"          <div class=\"mt-4\"><strong class=\"text-sm text-gray-700\">Examples:</strong></div>\n"
                sections += f"          <div class=\"overflow-x-auto\">\n"
                sections += f"            <table class=\"w-auto divide-y divide-gray-200 mt-2 rounded-lg overflow-hidden border border-gray-300\">\n"
                sections += f"              <thead class=\"bg-gray-100\">\n"
                sections += f"                <tr>\n"
                header = scenario['examples'][0]
                headers = [h.strip() for h in header.strip('|').split('|') if h.strip()]
                for h in headers:
                    sections += f"                  <th scope=\"col\" class=\"px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500\">{h}</th>\n"
                sections += f"                </tr>\n"
                sections += f"              </thead>\n"
                sections += f"              <tbody class=\"bg-white divide-y divide-gray-200\">\n"
                data_rows = scenario['examples'][1:]
                for row in data_rows:
                    sections += f"                <tr>\n"
                    cells = [c.strip() for c in row.strip('|').split('|') if c.strip()]
                    for cell in cells:
                        sections += f"                  <td class=\"px-6 py-4 whitespace-nowrap text-sm text-gray-900\">{cell}</td>\n"
                    sections += f"                </tr>\n"
                sections += f"              </tbody>\n"
                sections += f"            </table>\n"
                sections += f"          </div>\n"
            sections += f"        </ul>\n"
            sections += f"      </div>\n"
            sections += f"    </details>\n"
        sections += f'  </div>\n'
        sections += f'</details>\n\n'
    
    return sections, toc_links


def generate_validation_plan_html(metadata, features, manual_features):
    # Build traceability
    traceability_data = {}
    for collection in [features, manual_features]:
        for feature in collection:
            for scenario in feature['scenarios']:
                for req_id in scenario['req_ids']:
                    if req_id not in traceability_data:
                        traceability_data[req_id] = []
                    traceability_data[req_id].append({
                        'feature': feature['title'],
                        'scenario': scenario['name']
                    })

    sorted_req_ids = sorted(traceability_data.keys(), key=lambda x: int(x.split('_')[-1]) if x.split('_')[-1].isdigit() else float('inf')) if traceability_data else []

    traceability_table_html = "<p class=\"text-gray-600\">No requirement traceability data available.</p>"
    if sorted_req_ids:
        traceability_table_html = """
        <p class="text-gray-600 mb-4">This matrix links each product requirement to the Behave scenarios that validate it, ensuring comprehensive test coverage.</p>
        <div class="overflow-x-auto rounded-lg shadow-sm border border-gray-200">
            <table class="min-w-full bg-white rounded-lg">
                <thead class="bg-gray-100">
                    <tr>
                        <th class="px-6 py-3 text-left text-sm font-semibold text-gray-700 uppercase">Requirement ID</th>
                        <th class="px-6 py-3 text-left text-sm font-semibold text-gray-700 uppercase">Feature File</th>
                        <th class="px-6 py-3 text-left text-sm font-semibold text-gray-700 uppercase">Scenario(s)</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
        """
        for req_id in sorted_req_ids:
            scenarios = traceability_data[req_id]
            for i, entry in enumerate(scenarios):
                traceability_table_html += "<tr>\n"
                if i == 0:
                    traceability_table_html += f"<td rowspan=\"{len(scenarios)}\" class=\"px-6 py-4 font-medium text-gray-700\">{req_id}</td>\n"
                traceability_table_html += f"<td class=\"px-6 py-4 text-gray-600\">{entry['feature']}</td>\n"
                traceability_table_html += f"<td class=\"px-6 py-4 text-gray-600\">{entry['scenario']}</td>\n"
                traceability_table_html += "</tr>\n"
        traceability_table_html += "</tbody></table></div>"

    automated_feature_sections, automated_feature_toc_links = build_feature_sections(features)
    manual_feature_sections, manual_feature_toc_links = build_feature_sections(manual_features)

    # HTML template
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{metadata.get('Title', 'Validation Plan')}</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
  body {{ font-family: 'Inter', sans-serif; }}
  .resizable-container {{ display: flex; height: 100vh; }}
  #toc-panel {{ min-width: 250px; max-width: 50%; }}
  #resize-bar {{ width: 8px; cursor: ew-resize; background-color: #e2e8f0; transition: background-color 0.2s ease; }}
  #resize-bar:hover {{ background-color: #cbd5e1; }}
  #content-panel {{ flex-grow: 1; overflow-y: auto; }}
  details[open] > summary .chevron {{ transform: rotate(90deg); }}
</style>
</head>
<body class="bg-gray-100 text-gray-800">

<div class="resizable-container">
  <div id="toc-panel" class="flex-shrink-0 bg-white shadow-xl p-6 overflow-y-auto">
    <h2 class="text-2xl font-bold mb-4 text-gray-900">📑 Table of Contents</h2>
    <nav>
      <ul class="space-y-1 text-sm font-medium">
        <li><a href="#product-summary" class="block p-2 rounded hover:bg-gray-200">Product Summary</a></li>
        <li><a href="#validation-summary" class="block p-2 rounded hover:bg-gray-200">Validation Summary</a></li>
        <li><a href="#test-purposes" class="block p-2 rounded hover:bg-gray-200">Test Purposes</a></li>
        <li><a href="#framework-capabilities" class="block p-2 rounded hover:bg-gray-200">Framework Capabilities</a></li>
        <li><a href="#platform-support" class="block p-2 rounded hover:bg-gray-200">Platform Support</a></li>
        <li><a href="#key-features" class="block p-2 rounded hover:bg-gray-200">Key Features</a></li>
        <li><a href="#challenges" class="block p-2 rounded hover:bg-gray-200">Challenges</a></li>
        <li><a href="#limitations" class="block p-2 rounded hover:bg-gray-200">Limitations</a></li>
        <li><a href="#schedule-and-roles" class="block p-2 rounded hover:bg-gray-200">Schedule & Roles</a></li>
        <li>
          <a href="#automated-features" class="block p-2 rounded hover:bg-gray-200">Automated Features</a>
          <ul class="ml-4 pl-4 space-y-1">{automated_feature_toc_links}</ul>
        </li>
        <li>
          <a href="#manual-features" class="block p-2 rounded hover:bg-gray-200">Manual Features</a>
          <ul class="ml-4 pl-4 space-y-1">{manual_feature_toc_links}</ul>
        </li>
        <li><a href="#traceability-matrix" class="block p-2 rounded hover:bg-gray-200">Traceability Matrix</a></li>
        <li><a href="#revisions" class="block p-2 rounded hover:bg-gray-200">Revision History</a></li>
      </ul>
    </nav>
  </div>

  <div id="resize-bar"></div>

  <div id="content-panel" class="flex-1 p-8 overflow-y-auto">
    <header class="bg-white rounded-xl shadow-lg p-6 mb-8">
      <div class="flex items-center justify-between">
        <h1 class="text-4xl font-extrabold text-gray-900">{metadata.get('Title', 'Validation Plan')}</h1>
        <button id="toggle-all-btn" class="px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-75">
          Collapse All
        </button>
      </div>
      <p class="text-lg text-gray-600 mt-2">Comprehensive Validation Plan Summary</p>
      <div class="mt-4 flex flex-wrap gap-6 text-sm text-gray-500">
        <span><strong>Version:</strong> {metadata.get('Version', 'N/A')}</span>
        <span><strong>Date:</strong> {metadata.get('Date', 'N/A')}</span>
      </div>
    </header>

    <section id="product-summary" class="mb-8 p-6 bg-white rounded-xl shadow-md">
      <h2 class="text-2xl font-semibold text-gray-900 mb-4">Product Summary</h2>
      <ul class="list-disc list-inside text-gray-600 space-y-1">
        <li><strong>Product Name:</strong> {metadata.get('ProductName', 'N/A')}</li>
        <li><strong>Product Model:</strong> {metadata.get('ProductModel', 'N/A')}</li>
        <li><strong>Product Manufacturer:</strong> {metadata.get('ProductManufacturer', 'N/A')}</li>
        <li><strong>Interface:</strong> {metadata.get('Interface', 'N/A')}</li>
        <li><strong>Form Factor:</strong> {metadata.get('FormFactor', 'N/A')}</li>
        <li><strong>Target Environment:</strong> {metadata.get('TargetEnvironment', 'N/A')}</li>
        <li><strong>Product Manager:</strong> {metadata.get('ProductManager', 'N/A')}</li>
      </ul>
    </section>

    <section id="validation-summary" class="mb-8 p-6 bg-white rounded-xl shadow-md">
      <h2 class="text-2xl font-semibold text-gray-900 mb-4">Validation Summary</h2>
      <p class="text-gray-600"><strong>Objective:</strong> {metadata.get('Objective', 'N/A')}</p>
      <div class="mt-6 grid md:grid-cols-2 gap-8">
        <div>
          <h3 class="text-lg font-semibold text-gray-800 mb-2">In Scope</h3>
          <ul class="list-disc list-inside text-gray-600">
            {"".join(f"<li>{item}</li>" for item in get_value(metadata.get('Scope', {}), ["InScope"], []))}
          </ul>
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-800 mb-2">Out of Scope</h3>
          <ul class="list-disc list-inside text-gray-600">
            {"".join(f"<li>{item}</li>" for item in get_value(metadata.get('Scope', {}), ["OutOfScope", "OutScope"], []))}
          </ul>
        </div>
      </div>
    </section>

    <section id="test-purposes" class="mb-8 p-6 bg-white rounded-xl shadow-md">
      <h2 class="text-2xl font-semibold text-gray-900 mb-4">Test Purposes</h2>
      <ul class="list-disc list-inside text-gray-600">
        {"".join(f"<li>{item}</li>" for item in metadata.get('TestPurposes', []))}
      </ul>
    </section>

    <section id="framework-capabilities" class="mb-8 p-6 bg-white rounded-xl shadow-md">
      <h2 class="text-2xl font-semibold text-gray-900 mb-4">Framework Capabilities</h2>
      <ul class="list-disc list-inside text-gray-600">
        {"".join(f"<li>{item}</li>" for item in metadata.get('FrameworkCapabilities', []))}
      </ul>
    </section>

    <section id="platform-support" class="mb-8 p-6 bg-white rounded-xl shadow-md">
      <h2 class="text-2xl font-semibold text-gray-900 mb-4">Platform Support</h2>
      <div class="grid md:grid-cols-3 gap-6 text-gray-600">
        <div>
          <h3 class="font-semibold">Operating Systems</h3>
          <ul class="list-disc list-inside">
            {"".join(f"<li>{os}</li>" for os in get_value(metadata.get('PlatformSupport', {}), ["OperatingSystems"], []))}
          </ul>
        </div>
        <div>
          <h3 class="font-semibold">Server Architectures</h3>
          <ul class="list-disc list-inside">
            {"".join(f"<li>{arch}</li>" for arch in get_value(metadata.get('PlatformSupport', {}), ["ServerArchitectures"], []))}
          </ul>
        </div>
        <div>
          <h3 class="font-semibold">Cloud Platforms</h3>
          <ul class="list-disc list-inside">
            {"".join(f"<li>{cloud}</li>" for cloud in get_value(metadata.get('PlatformSupport', {}), ["CloudPlatforms"], []))}
          </ul>
        </div>
      </div>
    </section>

    <section id="key-features" class="mb-8 p-6 bg-white rounded-xl shadow-md">
      <h2 class="text-2xl font-semibold text-gray-900 mb-4">Key Features</h2>
      <ul class="list-disc list-inside text-gray-600">
        {"".join(f"<li>{item}</li>" for item in metadata.get('KeyFeatures', []))}
      </ul>
    </section>

    <section id="challenges" class="mb-8 p-6 bg-white rounded-xl shadow-md">
      <h2 class="text-2xl font-semibold text-gray-900 mb-4">Challenges</h2>
      <ul class="list-disc list-inside text-gray-600">
        {"".join(f"<li>{item}</li>" for item in metadata.get('Challenges', []))}
      </ul>
    </section>

    <section id="limitations" class="mb-8 p-6 bg-white rounded-xl shadow-md">
      <h2 class="text-2xl font-semibold text-gray-900 mb-4">Limitations</h2>
      <ul class="list-disc list-inside text-gray-600">
        {"".join(f"<li>{item}</li>" for item in metadata.get('Limitations', []))}
      </ul>
    </section>

    <section id="schedule-and-roles" class="mb-8 p-6 bg-white rounded-xl shadow-md">
      <h2 class="text-2xl font-semibold text-gray-900 mb-4">Validation Schedule & Roles</h2>
      <p class="text-gray-600"><strong>Estimated Duration:</strong> {metadata.get('ValidationDurationDays', 'N/A')} days</p>
      <div class="mt-4 grid md:grid-cols-2 gap-4 text-gray-600">
        <div><strong>QA Manager:</strong> {metadata.get('QA_Manager', 'N/A')}</div>
        <div><strong>Validation Engineer:</strong> {metadata.get('Validation_Engineer', 'N/A')}</div>
      </div>
    </section>

    <section id="automated-features" class="mb-8 p-6 bg-white rounded-xl shadow-md">
      <details open>
        <summary class="flex items-center justify-between cursor-pointer text-2xl font-semibold text-gray-900 hover:text-blue-700">
          Automated Behave Features & Scenarios
          <span class="chevron transition-transform duration-300">▶</span>
        </summary>
        <div class="mt-4">
          {automated_feature_sections}
        </div>
      </details>
    </section>

    <section id="manual-features" class="mb-8 p-6 bg-white rounded-xl shadow-md">
      <details>
        <summary class="flex items-center justify-between cursor-pointer text-2xl font-semibold text-gray-900 hover:text-blue-700">
          Manual Test Features & Scenarios
          <span class="chevron transition-transform duration-300">▶</span>
        </summary>
        <div class="mt-4">
          {manual_feature_sections}
        </div>
      </details>
    </section>

    <section id="traceability-matrix" class="mb-8 p-6 bg-white rounded-xl shadow-md">
      <h2 class="text-2xl font-semibold text-gray-900 mb-4">Traceability Matrix</h2>
      {traceability_table_html}
    </section>

    <section id="revisions" class="mb-8 p-6 bg-white rounded-xl shadow-md">
      <h2 class="text-2xl font-semibold text-gray-900 mb-4">Revision History</h2>
      <ul class="list-disc list-inside text-gray-600">
        {"".join(f"<li><strong>{rev.get('Version', 'N/A')}</strong> - {rev.get('Date', 'N/A')}: {rev.get('Changes', 'N/A')}</li>" for rev in metadata.get('RevisionHistory', []))}
      </ul>
    </section>

    <footer class="text-center text-sm text-gray-500 py-6">
      <p>{metadata.get('Copyright', 'N/A')}</p>
    </footer>
  </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', () => {{
  const tocPanel = document.getElementById('toc-panel');
  const resizeBar = document.getElementById('resize-bar');
  let isResizing = false;
  resizeBar.addEventListener('mousedown', () => {{
    isResizing = true;
    document.body.style.userSelect = 'none';
    document.body.style.cursor = 'ew-resize';
  }});
  document.addEventListener('mousemove', (e) => {{
    if (!isResizing) return;
    const newWidth = e.clientX;
    if (newWidth >= 250 && newWidth <= window.innerWidth * 0.5) {{
      tocPanel.style.width = newWidth + 'px';
    }}
  }});
  document.addEventListener('mouseup', () => {{
    isResizing = false;
    document.body.style.userSelect = 'auto';
    document.body.style.cursor = 'default';
  }});

  const toggleAllBtn = document.getElementById('toggle-all-btn');
  toggleAllBtn.addEventListener('click', () => {{
    const allDetails = document.querySelectorAll('details');
    let allOpen = true;

    allDetails.forEach(detail => {{
      if (!detail.open) {{
        allOpen = false;
      }}
    }});

    allDetails.forEach(detail => {{
      detail.open = !allOpen;
    }});

    if (allOpen) {{
      toggleAllBtn.textContent = 'Expand All';
    }} else {{
      toggleAllBtn.textContent = 'Collapse All';
    }}
  }});
}});
</script>

</body>
</html>
"""
    return html_content


def main():
    if len(sys.argv) != 3:
        print("❌ Error: Invalid number of arguments.")
        print("Usage: python builder.py <metadata.json> <features_dir>")
        sys.exit(1)

    metadata_file_path = sys.argv[1]
    features_dir_path = sys.argv[2]
    
    try:
        if not os.path.isfile(metadata_file_path):
            print(f"❌ Error: Metadata file not found at '{metadata_file_path}'.")
            sys.exit(1)

        if not os.path.isdir(features_dir_path):
            print(f"❌ Error: Features directory not found at '{features_dir_path}'.")
            sys.exit(1)

        print(f"✅ Input files found. Parsing data from '{features_dir_path}' and '{metadata_file_path}'...")
        
        with open(metadata_file_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        features = []
        manual_features = []
        for root, _, files in os.walk(features_dir_path):
            for filename in sorted(files):
                if filename.endswith('.feature'):
                    file_path = os.path.join(root, filename)
                    parsed = parse_feature_file(file_path)
                    if "manual_tests" in root.lower():
                        manual_features.append(parsed)
                    else:
                        features.append(parsed)
        
        if not features and not manual_features:
            print(f"❌ Error: No .feature files found in '{features_dir_path}'.")
            sys.exit(1)

        output_dir = os.path.dirname(metadata_file_path) or '.'
        version = metadata.get('Version', 'N/A')
        output_file_path = os.path.join(output_dir, f'validation_plan_v{version}.html')

        if os.path.exists(output_file_path):
            print(f"⚠️ Warning: Output file already exists and will be overwritten: {output_file_path}")

        print("🔄 Generating HTML validation plan...")
        html_output = generate_validation_plan_html(metadata, features, manual_features)
        
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(html_output)

        print(f"✅ Validation Plan Successfully Generated: {output_file_path}")

    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format in '{metadata_file_path}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()