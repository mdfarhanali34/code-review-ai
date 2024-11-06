from typing import Dict, Any
import logging
from itertools import islice
from data.diff import FilePatchInfo, EDIT_TYPE
from agent.llm import generate_feedback

logger = logging.getLogger(__name__)

class PRReview:
    def __init__(self, repo: Any, issue: Any):
        self.repo = repo
        self.issue = issue

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
        # Now we generate feedback and post it to GitHub
        for file_patch in diff_file:
            # Process each file patch and post line-by-line feedback
            await self.process_file_patch(file_patch, pull_request)

    async def get_diff_file(self, pull_request: Dict[str, Any], api_url: str):
        number = pull_request.get("number")
        pull = self.repo.get_pull(number)
        head_sha = pull.head.sha
        base_sha = pull.base.sha
        files = list(islice(pull.get_files(), 51))  # Limit to the first 51 files

        diff_files = []
        for file in files:
            path = file.filename
            patch = file.patch
            contents_new = self.repo.get_contents(path, ref=head_sha)
            content_new = contents_new.decoded_content.decode()

            # contents_orignal = self.repo.get_contents(path, ref=base_sha)
            # content_orignal = contents_orignal.decoded_content.decode()

            logger.info(f"Analyzing file: {path}")
            logger.info(f"Patch: {patch}")
            
            # count number of lines added and removed

            # file status can be 'added', 'removed', 'renamed', 'modified'
            if file.status == 'added':
                edit_type = EDIT_TYPE.ADDED
            elif file.status == 'removed':
                edit_type = EDIT_TYPE.DELETED
            elif file.status == 'renamed':
                edit_type = EDIT_TYPE.RENAMED
            elif file.status == 'modified':
                edit_type = EDIT_TYPE.MODIFIED


            patch_lines = patch.splitlines(keepends=True)
            num_plus_lines = len([line for line in patch_lines if line.startswith('+')])
            num_minus_lines = len([line for line in patch_lines if line.startswith('-')])
            file_patch_canonical_structure = FilePatchInfo(content_new, content_new, patch,
                                                            file.filename, edit_type=edit_type,
                                                            num_plus_lines=num_plus_lines,
                                                            num_minus_lines=num_minus_lines)
            diff_files.append(file_patch_canonical_structure)
           
        return diff_files

    async def process_file_patch(self, file_patch: FilePatchInfo, pull_request: Dict[str, Any]):
        """
        This method will process the file's patch line by line and post feedback to GitHub.
        """
        patch = file_patch.patch
        lines_added, lines_removed = self.parse_patch(patch)

        # Post comments for added lines
        for line_number, line in lines_added:
            feedback = generate_feedback(line)
            logger.info(f"Feedback for line {line_number}: {feedback}")
            await self.post_comment_on_github(file_patch.filename, line_number, feedback, pull_request)

        # Post comments for removed lines
        for line_number, line in lines_removed:
            feedback = generate_feedback(line)
            await self.post_comment_on_github(file_patch.filename, line_number, feedback, pull_request)

    def parse_patch(self, patch: str):
        """
        Parse the diff patch to identify the added and removed lines, along with line numbers.
        """
        added_lines = []
        removed_lines = []
        line_number_added = 0
        line_number_removed = 0

        patch_lines = patch.splitlines()
        for line in patch_lines:
            if line.startswith('+'):
                added_lines.append((line_number_added, line[1:].strip()))  # Skip the '+' and store line number
                line_number_added += 1
            elif line.startswith('-'):
                removed_lines.append((line_number_removed, line[1:].strip()))  # Skip the '-' and store line number
                line_number_removed += 1
        return added_lines, removed_lines

    async def post_comment_on_github(self, file_path: str, line_number: int, comment: str, pull_request: Dict[str, Any]):
        """
        Post a comment to GitHub for a specific line in a file, with error handling.
        """
        try:
            # Retrieve PR number and PR object
            number = pull_request.get("number")
            pr = self.repo.get_pull(number)

            # Create a general comment for context
            self.issue.create_comment("Howdy! This is an automated comment from the bot.")
            logger.info(f"PR head commit hash: {pr.head.sha}")
            commit = pr.get_commits().reversed[0]  # Get the latest commit
            # Attempt to post a review comment
            pr.create_issue_comment(comment)
            
            logger.info(f"Comment posted successfully for {file_path} at line {line_number}")
        
        except Exception as e:
            # Capture and log the error details
            logger.error(f"Failed to post comment on {file_path} at line {line_number}")
            logger.error(f"Error: {str(e)}")
            
            # Optionally, re-raise the error or handle it further if needed
            raise
