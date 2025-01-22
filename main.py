import logging
from gitbook_processor import GitBookProcessor
from html_converter import HTMLConverter
from ftmap_generator import FTMapGenerator
from fluid_topics_client import FluidTopicsClient
from utils import create_zip_archive, load_config

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def main():
    config = load_config()

    # Print the requested arguments
    print(f"GitBook Repo Folder: {config['gitbook_repo_folder']}")
    print(f"Commit Hash: {config['commit_hash']}")

    fluid_topics = config['fluid_topics']
    masked_api_key = f"{fluid_topics['api_key'][:3]}***" if fluid_topics['api_key'] else "Not Set"

    print(f"API Key: {masked_api_key}")
    print(f"Base URL: {fluid_topics['base_url']}")
    print(f"Source ID: {fluid_topics['source_id']}")
    print(f"Publication Title: {fluid_topics['publication_title']}")  # Fixed access here
    
    # Process GitBook content
    #gitbook_processor = GitBookProcessor(config['gitbook_repo'], commit_hash=config['commit_hash'])
    #processed_folder = gitbook_processor.process()
    
    processed_folder = config['gitbook_repo_folder']
    
    # Convert to HTML
    html_converter = HTMLConverter(processed_folder)
    html_converter.convert_all()

    # Generate FTMAP
    ftmap_generator = FTMapGenerator(processed_folder,title=config['fluid_topics']['publication_title'])
    ftmap_generator.generate()
    
    # Create ZIP archive
    zip_file = create_zip_archive(processed_folder)
    
    # Upload to Fluid Topics
    ft_client = FluidTopicsClient(config['fluid_topics'])
    return ft_client.upload(zip_file)

if __name__ == "__main__":
    main()
