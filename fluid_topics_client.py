import requests
import logging

logger = logging.getLogger(__name__)

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

class FluidTopicsClient:
    def __init__(self, config):
        self.api_key = config['api_key']
        self.base_url = config['base_url']
        self.source_id = config['source_id']

    def upload(self, zip_file):
        logger.info(f'Started uploading {zip_file} to Fluid Topics')
        with open(zip_file, "rb") as file:
            files = {"file": file}
            url = f"{self.base_url}/api/admin/khub/sources/{self.source_id}/upload"
            try:
                r = requests.post(url, files=files, auth=BearerAuth(self.api_key))
                if not r.ok:
                    logger.error("Failed to upload the data to Fluid Topics.")
                    logger.error(f"Response Code: {r.status_code}")
                    logger.error(f"Response Content: {r.content}")
                    return False
            except requests.exceptions.ConnectionError:
                logger.error(f'Connection reset while sending archive to {url}, please check that file uploaded correctly')
                return False
        logger.info(f'Finished uploading {zip_file} to Fluid Topics')
        return True