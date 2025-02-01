import os
from converter import generate_toc_yaml, create_zip_file, fix_relative_images_in_markdown


def main():
    # Input folder from environment variable
    input_folder = os.getenv("DOCS_FOLDER")
    if not input_folder:
        raise EnvironmentError("Please set the DOCS_FOLDER environment variable.")
    
    publication_title = os.getenv("PUBLICATION_TITLE")
    if not publication_title:
        raise EnvironmentError("Please set the PUBLICATION_TITLE environment variable.")

    # Ensure Summary.md exists
    summary_path = os.path.join(input_folder, "SUMMARY.md")
    if not os.path.exists(summary_path):
        raise FileNotFoundError(f"Summary.md not found in {input_folder}")

    # Step 1: Process Summary.md and create toc.yml
    toc_path = generate_toc_yaml(input_folder, summary_path, publication_title)
    print(f"Generated toc.yml at {toc_path}")

    # Step 2: Fix images in Markdown
    fix_relative_images_in_markdown(input_folder)
    print(f"Successfuly fixed relative images issue.")

    # Step 3: Create a ZIP file
    zip_path = create_zip_file(input_folder)
    print(f"Created ZIP file at {zip_path}")


if __name__ == "__main__":
    main()



# curl -v -X POST "https://yourbaseurl/api/admin/khub/sources/{source_id}/upload" -H "Authorization: Bearer your_api_key" -F "file=@path_to_your_zip_file.zip
