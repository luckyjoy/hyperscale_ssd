# prd2html.py
# Author: Bang Thien Nguyen
# Purpose: Build a dynamic and comprehensive PRD summary based on input metadata product.json and requirement.csv

import json
import sys
import re
import os

def generate_html_output(metadata, requirements):
    """
    Generates a polished HTML document from metadata and requirements.
    """
    # Fallbacks for metadata fields
    title = metadata.get("Title", "Product Requirements Document Summary")
    version = metadata.get("Version", "N/A")
    date = metadata.get("Date", "N/A")
    product_name = metadata.get("ProductName", "Unknown Product")
    product_model = metadata.get("ProductModel", "N/A")
    product_version = metadata.get("ProductVersion", "N/A")
    firmware_version = metadata.get("FirmwareVersion", "N/A")
    manufacturer = metadata.get("ProductManufacturer", "N/A")
    product_manager = metadata.get("ProductManager", "N/A")
    target_env = metadata.get("TargetEnvironment", "N/A")
    interface = metadata.get("Interface", "N/A")
    form_factor = metadata.get("FormFactor", "N/A")
    copyright_notice = metadata.get("Copyright", "N/A")

    platform_support = metadata.get("PlatformSupport", {})
    operating_systems = ", ".join(platform_support.get("OperatingSystems", []))
    server_architectures = ", ".join(platform_support.get("ServerArchitectures", []))
    cloud_platforms = ", ".join(platform_support.get("CloudPlatforms", []))
    key_features = metadata.get("KeyFeatures", [])

    # Group requirements by category for the TOC
    requirements_by_category = {}
    for req in requirements:
        category = req["Category"]
        if category not in requirements_by_category:
            requirements_by_category[category] = []
        requirements_by_category[category].append(req)

    # Generate TOC and requirement sections
    toc_items = ""
    requirements_table_html = ""
    
    # Add static links to TOC
    toc_items += f'<li><a href="#product-metadata" class="text-blue-600 hover:underline">📊 Product Metadata</a></li>'
    toc_items += f'<li><a href="#requirements-summary" class="text-blue-600 hover:underline">📋 Requirements Summary</a></li>'

    for category, reqs in requirements_by_category.items():
        anchor = category.lower().replace(" ", "-")
        toc_items += f'<li><a href="#{anchor}" class="text-blue-600 hover:underline">--- {category}</a></li>'

        requirements_table_html += f"""
        <div id="{anchor}" class="mb-8">
            <h3 class="text-xl font-semibold text-gray-800 mb-4">{category}</h3>
            <div class="overflow-x-auto">
                <table class="min-w-full bg-white border border-gray-200 rounded-lg shadow-sm">
                    <thead>
                        <tr class="bg-gray-50 border-b">
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Requirement ID</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                        {"".join(f'''
                        <tr>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{req['ID']}</td>
                            <td class="px-6 py-4 text-sm text-gray-600">{req['Description']}</td>
                        </tr>''' for req in reqs)}
                    </tbody>
                </table>
            </div>
        </div>
        """

    # JavaScript for resizable panels
    js_code = """
    document.addEventListener('DOMContentLoaded', () => {
        const tocPanel = document.getElementById('toc-panel');
        const resizeBar = document.getElementById('resize-bar');

        resizeBar.addEventListener('mousedown', (e) => {
            e.preventDefault();
            document.addEventListener('mousemove', resize);
            document.addEventListener('mouseup', stopResize);
        });

        const resize = (e) => {
            const newWidth = e.clientX;
            if (newWidth > 200 && newWidth < window.innerWidth * 0.5) {
                tocPanel.style.width = newWidth + 'px';
            }
        };

        const stopResize = () => {
            document.removeEventListener('mousemove', resize);
        };
    });
    """

    # Final HTML document
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            overflow: hidden;
        }}
        .resizable-container {{
            display: flex;
            height: 100vh;
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
    </style>
</head>
<body class="bg-gray-100">

    <div class="resizable-container">
        <div id="toc-panel" class="flex-shrink-0 bg-white shadow-xl p-6 overflow-y-auto">
            <h2 class="text-2xl font-bold mb-4 text-gray-900">Table of Contents</h2>
            <nav>
                <ul class="space-y-3">
                    {toc_items}
                </ul>
            </nav>
        </div>

        <div id="resize-bar" class="cursor-ew-resize"></div>

        <div id="content-panel" class="flex-1 p-8 overflow-y-auto">
            <header class="bg-white rounded-xl shadow-lg p-6 mb-8">
                <h1 class="text-4xl font-extrabold text-gray-900">{product_name} Requirements</h1>
                <p class="text-lg text-gray-600 mt-2">Comprehensive Product Requirements Summary</p>
                <div class="mt-4 flex flex-wrap gap-6 text-sm text-gray-500">
                    <span><strong>Version:</strong> {version}</span>
                    <span><strong>Author:</strong> {product_manager}</span>
                    <span><strong>Date:</strong> {date}</span>
                </div>
            </header>

            <section id="product-metadata" class="bg-white rounded-xl shadow-md p-6 mb-8">
                <h2 class="text-2xl font-semibold text-gray-900 mb-6">📊 Product Metadata</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 text-sm">
                    <div><strong>Product Name:</strong> {product_name}</div>
                    <div><strong>Product Model:</strong> {product_model}</div>
                    <div><strong>Product Version:</strong> {product_version}</div>
                    <div><strong>Firmware Version:</strong> {firmware_version}</div>
                    <div><strong>Manufacturer:</strong> {manufacturer}</div>
                    <div><strong>Product Manager:</strong> {product_manager}</div>
                    <div><strong>Target Environment:</strong> {target_env}</div>
                    <div><strong>Interface:</strong> {interface}</div>
                    <div><strong>Form Factor:</strong> {form_factor}</div>
                </div>

                <div class="mt-8">
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">Platform Support</h3>
                    <ul class="list-disc list-inside space-y-1 text-gray-600">
                        <li><strong>Operating Systems:</strong> {operating_systems}</li>
                        <li><strong>Server Architectures:</strong> {server_architectures}</li>
                        <li><strong>Cloud Platforms:</strong> {cloud_platforms}</li>
                    </ul>
                </div>

                <div class="mt-8">
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">Key Features</h3>
                    <ul class="list-disc list-inside space-y-1 text-gray-600">
                        {"".join(f"<li>{feature}</li>" for feature in key_features)}
                    </ul>
                </div>
            </section>

            <section id="requirements-summary" class="bg-white rounded-xl shadow-md p-6">
                <h2 class="text-2xl font-semibold text-gray-900 mb-6">📋 Requirements Summary</h2>
                {requirements_table_html}
            </section>
            
            <footer class="text-center text-sm text-gray-500 py-6 mt-8">
                <p>{copyright_notice}</p>
            </footer>

        </div>

    </div>

    <script>{js_code}</script>
</body>
</html>
    """
    return html_content

def main():
    """Main function to read data and generate the HTML report."""
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("❌ Usage: python prd2html.py <metadata.json> <requirements.csv> [output_file.html]")
        sys.exit(1)

    json_file_path, csv_file_path = sys.argv[1:3]
    output_file_path_arg = sys.argv[3] if len(sys.argv) == 4 else None

    # Validate both input files exist before proceeding
    missing_files = [f for f in (json_file_path, csv_file_path) if not os.path.isfile(f)]
    if missing_files:
        print("❌ Error: The following input file(s) were not found:")
        for f in missing_files:
            print(f"   - {f}")
        sys.exit(1)

    try:
        # Load and validate JSON metadata
        with open(json_file_path, "r", encoding="utf-8") as f:
            product_metadata = json.load(f)

        if not isinstance(product_metadata, dict):
            print(f"❌ Error: Metadata JSON must be a dictionary at the root level in '{json_file_path}'.")
            sys.exit(1)

        # Warn about missing recommended keys
        recommended_keys = ["Title", "Version", "ProductName", "ProductManager"]
        for key in recommended_keys:
            if key not in product_metadata:
                print(f"⚠️ Warning: Missing recommended metadata key: '{key}'")

        # Parse CSV requirements
        requirements_list = []
        current_category = "Uncategorized"
        header_found = False

        with open(csv_file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                stripped_line = line.strip()
                if not stripped_line:
                    continue

                if not header_found:
                    if stripped_line.lower().startswith("requirement_id,requirement_description"):
                        header_found = True
                    continue

                if stripped_line.startswith("#"):
                    category_match = re.search(r"#(.*)", stripped_line)
                    if category_match:
                        current_category = category_match.group(1).strip()
                elif ":" in stripped_line:
                    parts = stripped_line.split(":", 1)
                    req_id, req_desc = parts[0].strip(), parts[1].strip()
                    if req_id and req_desc:
                        requirements_list.append(
                            {"ID": req_id, "Description": req_desc, "Category": current_category}
                        )
                    else:
                        print(f"⚠️ Skipping incomplete requirement at line {line_num}: '{stripped_line}'")
                else:
                    print(f"⚠️ Skipping unparseable line {line_num}: '{stripped_line}'")

        if not requirements_list:
            print(f"❌ Error: No valid requirements found in {csv_file_path}. Please check your file format.")
            sys.exit(1)

        # Prepare output path
        output_file_path = output_file_path_arg
        if not output_file_path:
            version = product_metadata.get("Version", "N/A")
            output_dir = os.path.dirname(json_file_path) or "."
            output_file_path = os.path.join(output_dir, f"prd_summary_{version}.html")

        if os.path.exists(output_file_path):
            print(f"⚠️ Warning: Output file already exists and will be overwritten: {output_file_path}")

        # Generate and write HTML
        html_output = generate_html_output(product_metadata, requirements_list)
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(html_output)

        print(f"✅ PRD Summary Successfully Generated: {output_file_path}")

    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format in {json_file_path}: {e}")
        sys.exit(1)
    except FileNotFoundError:
        # This is caught by the initial check, but good practice to keep
        print(f"❌ Error: A required file was not found. Please check paths.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()