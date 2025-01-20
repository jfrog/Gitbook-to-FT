# GitBook to Fluid Topics Converter

A Python-based tool that processes GitBook documentation repositories and prepares them for publication to Fluid Topics. This tool clones your GitBook repository, converts Markdown content to HTML, generates the required FTMap structure, and creates a ZIP archive ready for Fluid Topics.

## Features

- Clones or updates GitBook repositories
- Supports specific commit checkout
- Converts Markdown to HTML with special handling for:
  - Tables
  - Code blocks
  - Hint blocks
  - Lists and nested content
- Generates Fluid Topics compatible navigation map (FTMap)
- Creates a properly structured ZIP archive
- Uploads content to Fluid Topics via API

## Prerequisites

- Python 3.x
- Git installed and configured
- Access to your GitBook repository
- Fluid Topics API credentials

## Installation

1. Clone this repository:


2. (Optional) Create and activate a virtual environment:
   
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```   
4. Create a `.env` file in the root directory with your configuration:
   ```env
   ### GITBOOK_REPO_URL=<your-gitbook-repo-url>
   GITBOOK_REPO_FOLDER=<your-gitbook-repo-folder-in-local-filesystem>
   COMMIT_HASH=<optional-specific-commit>
   FLUID_TOPICS_API_KEY=<your-api-key>
   FLUID_TOPICS_BASE_URL=<fluid-topics-base-url>
   FLUID_TOPICS_SOURCE_ID=<your-source-id>
   PUBLICATION_TITLE=<your-publication-title>
   ```
## Usage

Run the converter:

```bash
python main.py
```

The tool will:
1. Clone/update your GitBook repository
2. Convert all Markdown files to HTML
3. Generate the FTMap navigation structure
4. Create a ZIP archive
5. Upload to Fluid Topics 

## Component Overview

### GitBook Processor (`gitbook_processor.py`)
Handles repository cloning and management:
- Clones GitBook repositories
- Supports checking out specific commits
- Creates a working copy for processing

### HTML Converter (`html_converter.py`)
Converts Markdown content to Fluid Topics compatible HTML:
- Processes tables, code blocks, and hint blocks
- Ensures proper HTML structure
- Maintains document hierarchy

### FTMap Generator (`ftmap_generator.py`)
Creates the navigation structure required by Fluid Topics FTML connector.

- Generates an XML-based navigation map (FTMAP) that defines the structure of your documentation
- Maps the hierarchical relationship between documents
- Preserves the GitBook navigation structure in Fluid Topics
- Handles document references and links
- Assigns unique identifiers to each content node
- Maintains the table of contents (TOC) structure

Example FTMAP structure:
```xml
<ft:map xmlns:ft="http://ref.fluidtopics.com/v3/ft#" ft:lang="en-US" ft:title="Documentation">
    <ft:toc>
        <ft:node ft:originId="1" ft:title="Getting Started" href="getting-started.html">
            <ft:node ft:originId="2" ft:title="Installation" href="installation.html"/>
            <ft:node ft:originId="3" ft:title="Configuration" href="configuration.html"/>
        </ft:node>
    </ft:toc>
</ft:map>
```

### Fluid Topics Client (`fluid_topics_client.py`)
Manages communication with the Fluid Topics API. 

The upload process:
1. Authenticates with Fluid Topics using the API key
2. Prepares the ZIP archive with HTML content, assets and the FTMAP 
3. Uploads the pulblication to the specified source ID(FTML Source)





