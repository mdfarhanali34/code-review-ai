from typing import Dict, Any
import logging
from itertools import islice

logger = logging.getLogger(__name__)

class PRReview:
    def __init__(self, repo: Any):
        self.repo = repo

    async def handle_request(self, body: Dict[str, Any], event: str):
        logger.info(f"Received event: {event}")
        logger.info(f"Request body: {body}")
        action = body.get("action")
        if event == "pull_request":
            await self.handle_new_pr_opened(body, event, action)

    async def handle_new_pr_opened(self, body: Dict[str, Any], event: str, action: str):
        pull_request = body.get("pull_request")
        # Process the PR
        api_url = "your_api_url_here"  # Define your api_url logic if needed
        diff_file = await self.get_diff_file(pull_request, api_url)
        # Process the diff file as required
        logger.info(f"Diff file: {diff_file}")

    async def get_diff_file(self, pull_request: Dict[str, Any], api_url: str):
        number = pull_request.get("number")
        pull = self.repo.get_pull(number)
        head_sha = pull.head.sha
        files = list(islice(pull.get_files(), 51))  # Limit to the first 51 files
        diff_files = []
        for file in files:
            path = file.filename
            patch = file.patch
            contents = self.repo.get_contents(path, ref=head_sha)
            content = contents.decoded_content.decode()
            logger.info(f"Analyzing file: {path}")
            logger.info(f"Patch: {patch}")
            logger.info(f"Content: {content}")
            diff_files.append({
                "path": path,
                "patch": patch,
                "content": content
            })
        return diff_files
