import os
import re
import subprocess
from pathlib import Path
from tqdm import tqdm
import summary
import shutil

def convert_gitbook_to_fluid(input_folder, output_folder):
    """
    Converts all GitBook Markdown files in the input_folder to Fluid Topics-compatible Markdown.
    Uses Pandoc for format conversion and regex for syntax adjustments.
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all markdown files
    md_files = list(input_path.rglob("*.md"))

    for md_file in tqdm(md_files, desc="Processing Markdown Files"):
        #print(f"Converting: {md_file}")
        with open(md_file, "r", encoding="utf-8") as file:
            content = file.read()

        #print(content)
        #input("Press Enter to continue...")
        # Convert GitBook Markdown to Fluid Topics Markdown using Pandoc
        pandoc_command = [
            "pandoc",
            "--from=gfm",
            "--to=html", #markdown",
            "--wrap=none",
            "--lua-filter=fix_folder_links.lua",
        ]
        result = subprocess.run(pandoc_command, input=content.encode(), capture_output=True)
        converted_content = result.stdout.decode()
        #print(result.stderr.decode())
        #input("Press Enter to continue...")
        #print(converted_content)
        #input("Press Enter to continue...")

        # Replace GitBook-specific syntax with Fluid Topics format
        converted_content = adjust_markdown_syntax(converted_content)

        # Save converted file in output folder
        relative_path = md_file.relative_to(input_path)
        output_file = output_path / relative_path
        #output_file = output_file.with_suffix(".html")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(converted_content)

def adjust_markdown_syntax(content):
    """
    Adjusts GitBook-specific Markdown syntax to be compatible with Fluid Topics.
    """

    # Convert GitBook hint blocks to Fluid Topics admonitions
    #content = re.sub(r"\{% hint style=\"info\" %\}", "!!! info", content)
    #content = re.sub(r"\{% hint style=\"warning\" %\}", "!!! warning", content)
    #content = re.sub(r"\{% hint style=\"danger\" %\}", "!!! danger", content)
    #content = re.sub(r"\{% hint style=\"success\" %\}", "!!! success", content)
    #content = re.sub(r"\{% endhint %\}", "", content)

    # Convert GitBook tabbed content (Fluid Topics may need a different format)
    #content = re.sub(r"\{% tabs %\}", "", content)
    #content = re.sub(r"\{% tab title=\"(.*?)\" %\}", r"### \1", content)
    #content = re.sub(r"\{% endtab %\}", "", content)
    #content = re.sub(r"\{% endtabs %\}", "", content)

    # Convert math expressions (ensure KaTeX compatibility)
    #content = re.sub(r"\$\$(.*?)\$\$", r"```math\n\1\n```", content, flags=re.DOTALL)

    return content

def create_zip_file(input_folder, output_name="documentation"):
    """
    Creates a ZIP file from the input folder for Fluid Topics.
    """
    zip_file = os.path.join(input_folder, f"{output_name}.zip")
    shutil.make_archive(zip_file.replace(".zip", ""), "zip", input_folder)
    return zip_file

if __name__ == "__main__":
    
    
    input_folder = os.getenv("DOCS_FOLDER")
    output_folder = os.getenv("OUT_FOLDER")
    
    PUBLICATION_TITLE = os.getenv('PUBLICATION_TITLE')

    print(f"Coverting MD to html...")
    convert_gitbook_to_fluid(input_folder, output_folder)
    print(f"Done.")

    print(f"Creating Summary toc...")
    summary.create_summary(input_folder, output_folder, PUBLICATION_TITLE)
    print(f"Done.")

    print(f"Copying .gitbook folder...")
    shutil.copytree(input_folder + "/.gitbook", output_folder + "/.gitbook")
    print(f"Done.")

    print(f"Creating ZIP file...")
    zip_path = create_zip_file(output_folder)
    print(f"Created ZIP file at {zip_path}")
    print(f"\n✅ Conversion complete! Converted files saved to: {output_folder}")
