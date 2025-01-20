import os
import shutil
import logging
from git import Repo
from datetime import datetime

logger = logging.getLogger(__name__)

class GitBookProcessor:
    def __init__(self, repo_url, commit_hash=None):
        self.repo_url = repo_url
        self.repo_name = repo_url.split('/')[-1].replace('.git', '')
        self.local_path = f"temp_{self.repo_name}"
        self.commit_hash = commit_hash

    def clone_or_pull(self):
        if os.path.exists(self.local_path):
            logger.info(f"Pulling updates for {self.repo_name}")
            repo = Repo(self.local_path)
            origin = repo.remotes.origin
            origin.fetch()
            if self.commit_hash:
                repo.git.checkout(self.commit_hash)
            else:
                origin.pull()
        else:
            logger.info(f"Cloning {self.repo_name}")
            repo = Repo.clone_from(self.repo_url, self.local_path)
            if self.commit_hash:
                repo.git.checkout(self.commit_hash)

    def process(self):
        self.clone_or_pull()
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        processed_folder = f"{self.repo_name}_processed_{timestamp}"
        shutil.copytree(self.local_path, processed_folder)
        return processed_folder