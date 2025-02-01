import os
import re
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


# def fix_relative_images_in_markdown(input_folder: str):
#     toc_file = os.path.join(input_folder, "toc.yml")

#     # Load TOC to get Markdown file paths
#     with open(toc_file, "r") as toc:
#         toc_data = yaml.safe_load(toc)

#     # Flatten all Markdown file paths from toc.yml
#     def extract_paths(entries):
#         paths = []
#         for entry in entries:
#             path = entry.get("filepath")
#             if path and path.endswith(".md"):
#                 paths.append(os.path.join(input_folder, path))
#             if "children" in entry:
#                 paths.extend(extract_paths(entry["children"]))
#         return paths

#     md_files = extract_paths(toc_data.get("toc", []))

#     # Regex to detect relative image paths
#     image_pattern = re.compile(r"!\[.*?\]\((\.\./.*?\.png|\.jpg|\.jpeg|\.svg)\)")

#     for md_file in md_files:
#         directory = os.path.dirname(md_file)
        
#         # Process each Markdown file
#         with open(md_file, "r") as file:
#             content = file.read()
        
#         updated_content = content
#         matches = image_pattern.findall(content)

#         for match in matches:
#             relative_path = os.path.normpath(os.path.join(directory, match))
#             if os.path.exists(relative_path):
#                 # Copy image to the Markdown file's directory
#                 image_name = os.path.basename(relative_path)
#                 new_image_path = os.path.join(directory, image_name)

#                 # Avoid overwriting if the image is already there
#                 if relative_path != new_image_path:
#                     shutil.copy2(relative_path, new_image_path)

#                 # Update Markdown image path
#                 updated_content = updated_content.replace(match, image_name)
        
#         # Write back updated Markdown if changes were made
#         if updated_content != content:
#             with open(md_file, "w") as file:
#                 file.write(updated_content)

#     print("Markdown image paths fixed successfully.")


def fix_relative_images_in_markdown(input_folder: str):
    toc_file = os.path.join(input_folder, "toc.yml")

    # Load TOC to get Markdown file paths
    with open(toc_file, "r") as toc:
        toc_data = yaml.safe_load(toc)

    # Flatten all Markdown file paths from toc.yml
    def extract_paths(entries):
        paths = []
        for entry in entries:
            path = entry.get("filepath")
            if path and path.endswith(".md"):
                paths.append(os.path.join(input_folder, path))
            if "children" in entry:
                paths.extend(extract_paths(entry["children"]))
        return paths

    md_files = extract_paths(toc_data.get("toc", []))

    image_pattern = re.compile(r"(!\[.*?\]\()(\.\./)(.*?\))")

    # for md_file in md_files:
    #     print(f"checking {md_file} if needs fixing")
    #     with open(md_file, "r+", encoding="utf-8") as file:
    #         content = file.read()
    #         # Replace one instance of "../" per match
    #         updated_content = re.sub(image_pattern, lambda m: m.group(1) + m.group(3), content)
    #         if content != updated_content:
    #             print(f"=======fixing: {md_file}")
    #             file.seek(0)
    #             file.write(updated_content)
    #             file.truncate()


    #----- 2nd try
    # for md_file in md_files:
    #     print(f"checking {md_file} if needs fixing")
    #     with open(md_file, "r+", encoding="utf-8") as file:
    #         content = file.read()
    #         # Replace exactly one "../" per path instance
    #         updated_content = re.sub(r"(\.\.\/)+", r"\1\3", content)
    #         updated_content = re.sub(image_pattern, lambda m: m.group(1) + m.group(3), content)
    #         if content != updated_content:
    #             print(f"=======fixing: {md_file}")
    #             file.seek(0)
    #             file.write(updated_content)
    #             file.truncate()
    #----- 3rd try
    # for md_file in md_files:
    #     with open(md_file, 'r', encoding="utf-8") as file:
    #         content = file.read()

    #     print(f"checking {md_file} if needs fixing")
    #     # Find all occurrences of greedy ../ and replace them by removing one ../
    #     updated_content = re.sub(r'(\.\.\/)+', lambda match: match.group(0)[:-3], content)
    #     if updated_content != content:
    #         print(f"=======fixing: {md_file}")
    #     # Write the updated content back to the file
    #     with open(md_file, 'w', encoding="utf-8") as file:
    #         file.write(updated_content)

    #----- 4rd try
    for md_file in md_files:
        with open(md_file, 'r', encoding="utf-8") as file:
            content = file.read()

        #print(f"checking {md_file} if needs fixing")

        paths_in_file = find_patterns_with_dotdot(content)
        

        if paths_in_file:
        
            updated_content = content
            directory = os.path.dirname(md_file)
        #     print(f"=======fixing: {md_file}")
            for path in paths_in_file:
                ############################################
                # if ".." in path:
                #     relative_path = os.path.normpath(os.path.join(directory, path))
                #     if os.path.exists(relative_path):
                #         print(f"OK - {relative_path} = {md_file} {path}")
                #     else:
                #         relative_path = os.path.normpath(os.path.join(directory, path[3:]))
                #         if os.path.exists(relative_path):
                #             print(f"OK_after_fix. Fixing! - {relative_path} = {md_file} {path[3:]}")
                #             updated_content = updated_content.replace(path, path[3:])
                #         else:
                #             print(f"!FAIL! - {relative_path} - {md_file} {path}")
                # elif ("http" not in path) and (path[-1] == "/"):
                #     relative_path = os.path.normpath(os.path.join(directory, path))
                #     if os.path.exists(relative_path):
                #         print(f"I suspect in: {md_file} {relative_path}")
                #         temp = os.path.join(relative_path, "_README.md")
                #         if os.path.exists(temp):
                #             print(f"I found a matching: {temp}")
                ########################################
                print(f"====================================woring on: {path}")
                if (".." in path) and (path[-1] != "/"):
                    relative_path = os.path.normpath(os.path.join(directory, path))
                    if os.path.exists(relative_path):
                        print(f"OK - {relative_path} = {md_file} {path}")
                    else:
                        relative_path = os.path.normpath(os.path.join(directory, path[3:]))
                        if os.path.exists(relative_path):
                            print(f"OK_after_fix. Fixing! - {relative_path} = {md_file} {path[3:]}")
                            updated_content = updated_content.replace(path, path[3:])
                        else:
                            print(f"!FAIL! - {relative_path} - {md_file} {path}")
                elif ("http" not in path[:4]) and (path[-1] == "/"):
                    relative_path = os.path.normpath(os.path.join(directory, path))
                    if os.path.exists(relative_path):
                        print(f"I suspect in: {md_file} {relative_path}")
                        temp = os.path.join(relative_path, "_README.md")
                        if os.path.exists(temp):
                            print(f"I found a matching: {temp}")
                            updated_content = updated_content.replace(path, path + "/_README.md")

            
            if updated_content != content:
                with open(md_file, 'w', encoding="utf-8") as file:
                    file.write(updated_content)

                    # Copy image to the Markdown file's directory
        #         relative_path = os.path.normpath(os.path.join(directory, path))
        #         relative_path_minos1 = os.path.normpath(os.path.join(directory, path[3:]))

        #         if " " in relative_path or " " in relative_path_minos1:
        #             # rename the file not to have space
        #             pass


        #         if os.path.exists(relative_path):
        #             if " " in relative_path:
        #                 print(f"~~~ fixing space in {relative_path}")
        #                 relative_path = rename_space_to_dash(relative_path)
        #                 updated_content = updated_content.replace(path, relative_path)
        #             else:
        #                 print(f"~~~ nothing to fix, we are good with {relative_path}")
        #         elif os.path.exists(relative_path_minos1):
        #             if " " in relative_path_minos1:
        #                 print(f"~~~ fixing space in {relative_path_minos1}")
        #                 relative_path_minos1 = rename_space_to_dash(relative_path_minos1)
        #                 updated_content = updated_content.replace(path, relative_path_minos1)
        #             print(f"~~~ fixing minos1 to {relative_path_minos1}")
        #             updated_content = updated_content.replace(path, relative_path_minos1)
        #         else:
        #             print("!!!!!!!!!!!!!!!!! issue !!!!!!!!!!")
        #             exit(1)


                #     # Copy image to the Markdown file's directory
                #     image_name = os.path.basename(relative_path)
                #     new_image_path = os.path.join(directory, image_name)

                #     # Avoid overwriting if the image is already there
                #     if relative_path != new_image_path:
                #         shutil.copy2(relative_path, new_image_path)

                #     # Update Markdown image path
                #     updated_content = updated_content.replace(path, image_name)

                # # Find all occurrences of greedy ../ and replace them by removing one ../
                # updated_content = re.sub(r'(\.\.\/)+', lambda match: match.group(0)[:-3], content)

                # # Write the updated content back to the file
                # with open(md_file, 'w', encoding="utf-8") as file:
                #     file.write(updated_content)

    print("Fixed relative image paths.")


def find_patterns_with_dotdot(text):
    # Define the regular expressions for the two patterns
    #pattern1 = r'[\"](?=.*\/\.\.\/)(.*?)[\"]'
    #pattern1 = r'\"(?=[^()]*\.\..*?)([^()]*?)\"'
    pattern1 = r'\"(?=\.\.\/.*?)([^"]*?)\"'
    #pattern2 = r'[("](?=.*\/\.\.\/)(.*?)[\)]'
    pattern2 = r'\(<*(?=[^()]*\.\..*?)([^()]*?)>*\)'
    pattern3_test = r'\(<*(?=[^()]*.*?)([^()]*?\/)>*\)'    # [**Configure Repositories**](configure-repositories/)
    
    
    # Use re.findall() to capture all occurrences of each pattern
    matches1 = re.findall(pattern1, text)
    matches2 = re.findall(pattern2, text)
    
    matches3 = re.findall(pattern3_test, text)
    if matches3:
        print(f"************* {matches3}")
    
    
    # Combine both match results
    return list(set(matches1 + matches2 + matches3))

def rename_space_to_dash(relative_path):
    shutil.copy2(relative_path, relative_path.replace(" ","-"))
    return relative_path.replace(" ","-")

