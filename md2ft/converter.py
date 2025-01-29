import os
import yaml
import shutil

def parse_summary_to_hierarchy(summary_lines, base_folder):
    """
    Parse the Summary.md content and build a YAML-compatible hierarchy
    based on indentation.

    Args:
        summary_lines (list of str): Lines from Summary.md.

    Returns:
        list: Hierarchical structure for the table of contents.
    """
    hierarchy = []
    stack = []  # A stack to track the current path of nodes based on depth.

    for line in summary_lines:
        # Ignore lines that are not list items
        if not line.strip().startswith("*"):
            continue
        
        # Count the indentation level (2 spaces per level)
        level = (len(line) - len(line.lstrip(" "))) // 2
        
        # Extract the text and filepath from the line
        line_content = line.strip().lstrip("*").strip()
        if "[" in line_content and "]" in line_content and "(" in line_content and ")" in line_content:
            name = line_content.split("]")[0].lstrip("[")
            filepath = line_content.split("(", 1)[1].strip(">)< ")

            # Rename README.md to _README.md in filepath
            if os.path.basename(filepath).lower() == "readme.md":
                new_filepath = os.path.join(
                    os.path.dirname(filepath), "_README.md"
                ).replace("\\", "/")
                old_path = os.path.join(base_folder, filepath)
                new_path = os.path.join(base_folder, new_filepath)
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                filepath = new_filepath
        else:
            name, filepath = line_content, None  # Handle lines without a link
        
        # Create the current node
        node = {"filepath": filepath, "children": []}

        # Adjust the stack to match the current depth
        while len(stack) > level:
            stack.pop()
        
        # Add the node to the correct parent or the root hierarchy
        if stack:
            stack[-1]["children"].append(node)
        else:
            hierarchy.append(node)
        
        # Push the current node onto the stack
        stack.append(node)

        # Remove nodes with empty children
    def remove_empty_children(nodes):
        for node in nodes:
            # Recursively remove empty "children" from child nodes
            if node["children"]:
                remove_empty_children(node["children"])

            if not node["children"]:
                del node["children"]  # Remove the empty "children" key

    remove_empty_children(hierarchy)

    return hierarchy



def generate_toc_yaml(input_folder, summary_path, publication_title):
    """
    Reads the Summary.md file, renames README.md files, and generates toc.yml.
    """
    if not os.path.exists(summary_path):
        raise FileNotFoundError(f"Summary.md not found at {summary_path}")

    # Read the Summary.md file
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_lines = f.readlines()

    # Parse the hierarchy
    hierarchy = parse_summary_to_hierarchy(summary_lines, input_folder)

    # Add metadata
    toc_data = {
        "toc": hierarchy,
        "metadata": [
            {"key": "ft:originId", "value": "0"},
            {"key": "ft:title", "value": publication_title},
        ],
    }

    # Write to toc.yml
    toc_path = os.path.join(input_folder, "toc.yml")
    with open(toc_path, "w", encoding="utf-8") as f:
        yaml.dump(toc_data, f, default_flow_style=False, sort_keys=False)

    return toc_path


def create_zip_file(input_folder, output_name="documentation"):
    """
    Creates a ZIP file from the input folder for Fluid Topics.
    """
    zip_file = os.path.join(input_folder, f"{output_name}.zip")
    shutil.make_archive(zip_file.replace(".zip", ""), "zip", input_folder)
    return zip_file
