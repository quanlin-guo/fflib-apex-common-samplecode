#!/opt/homebrew/bin/python3

import os
import re
import sys
import subprocess

# Mapping of file extensions to Salesforce metadata types
SALESFORCE_METADATA_TYPES = {
    ".cls": "ApexClass",
    ".trigger": "ApexTrigger",
    ".object-meta.xml": "CustomObject",
    ".field-meta.xml": "CustomField",
    ".app-meta.xml": "CustomApplication",
    ".page-meta.xml": "ApexPage",
    ".tab-meta.xml": "CustomTab",
    ".layout-meta.xml": "Layout",
    ".listView-meta.xml": "ListView",
    ".webLink-meta.xml": "WebLink",
    ".fieldSet-meta.xml": "FieldSet",
}

def detect_file_state(file_path, base_dir):
    """
    Determines whether the file is newly created, modified, or unchanged using Git.
    If Git isn't available, defaults to "", which means unmodified.
    """
    try:
        rel_path = os.path.relpath(file_path, base_dir)
        git_status = subprocess.run(["git", "status", "--porcelain", rel_path],
                                    capture_output=True, text=True)
        status_code = git_status.stdout.strip()[:2]  # Extract status code (e.g., "A ", "M ")

        if status_code.startswith("A"):
            return "Created"
        elif status_code.startswith("M"):
            return "Changed"
    except Exception:
        pass  # If Git isn't available, assume Unmodified

    return ""

def categorize_files(base_dir):
    """
    Scans the directory and categorizes files by type.
    """
    file_data = []

    for root, _, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(root, file)

            # Identify metadata type
            metadata_type = None
            for ext, sf_type in SALESFORCE_METADATA_TYPES.items():
                if file.endswith(ext):
                    metadata_type = sf_type
                    break
            
            if metadata_type:
                state = detect_file_state(file_path, base_dir)
                relative_path = os.path.relpath(file_path, base_dir)
                file_data.append((state, file.replace(ext, ""), metadata_type, relative_path))

    return file_data

def generate_markdown_table(file_data):
    """
    Generates a Markdown table from the categorized file data.
    """
    markdown_table = []
    markdown_table.append("| State       | Name         | Type        | Path                     |")
    markdown_table.append("|------------|-------------|------------|---------------------------|")

    for row in file_data:
        markdown_table.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} |")

    return "\n".join(markdown_table)

def print_usage():
    print("Usage: python scan_sf_directory.py <directory>")
    print("Scans a Salesforce source directory and generates a Markdown table.")

def main():
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)

    base_dir = sys.argv[1]

    if not os.path.isdir(base_dir):
        print(f"Error: Directory '{base_dir}' not found.")
        sys.exit(1)

    file_data = categorize_files(base_dir)
    markdown_table = generate_markdown_table(file_data)

    print(markdown_table)

if __name__ == "__main__":
    main()
