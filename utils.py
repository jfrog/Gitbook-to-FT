import os
import shutil
from dotenv import load_dotenv

def create_zip_archive(folder_path):
    zip_name = os.path.basename(folder_path)
    shutil.make_archive(base_name=zip_name, format='zip', root_dir=folder_path)
    return f"{zip_name}.zip"

def load_config():
    load_dotenv()  # This loads the variables from .env file
    
    return {
        'gitbook_repo': os.getenv('GITBOOK_REPO_URL'),
        'gitbook_repo_folder': os.getenv('GITBOOK_REPO_FOLDER'),
        'commit_hash': os.getenv('COMMIT_HASH'),
        'fluid_topics': {
            'api_key': os.getenv('FLUID_TOPICS_API_KEY'),
            'base_url': os.getenv('FLUID_TOPICS_BASE_URL'),
            'source_id': os.getenv('FLUID_TOPICS_SOURCE_ID'),
            'publication_title': os.getenv('PUBLICATION_TITLE')
        }
    }