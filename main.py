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
    ft_client.upload(zip_file)

if __name__ == "__main__":
    main()