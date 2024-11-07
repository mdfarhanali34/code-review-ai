from typing import Dict, Any, List
import logging
from itertools import islice
from data.diff import FilePatchInfo, EDIT_TYPE
from agent.llm import generate_feedback, needs_feedback

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
        api_url = "your_api_url_here"
        diff_file = await self.get_diff_file(pull_request, api_url)

        # Process each file patch and post comments line by line
        for file_patch in diff_file:
            file_comments = await self.process_file_patch(file_patch)
            for line_number, comment in file_comments:
                await self.post_comment_on_github(comment, file_patch.filename, line_number, pull_request)

    async def get_diff_file(self, pull_request: Dict[str, Any], api_url: str):
        number = pull_request.get("number")
        pull = self.repo.get_pull(number)
        head_sha = pull.head.sha
        base_sha = pull.base.sha
        files = list(islice(pull.get_files(), 51))

        diff_files = []
        for file in files:
            path = file.filename
            patch = file.patch
            contents_new = self.repo.get_contents(path, ref=head_sha)
            content_new = contents_new.decoded_content.decode()

            edit_type = EDIT_TYPE.MODIFIED
            if file.status == 'added':
                edit_type = EDIT_TYPE.ADDED
            elif file.status == 'removed':
                edit_type = EDIT_TYPE.DELETED
            elif file.status == 'renamed':
                edit_type = EDIT_TYPE.RENAMED

            patch_lines = patch.splitlines(keepends=True)
            num_plus_lines = len([line for line in patch_lines if line.startswith('+')])
            num_minus_lines = len([line for line in patch_lines if line.startswith('-')])
            file_patch_canonical_structure = FilePatchInfo(content_new, content_new, patch,
                                                            file.filename, edit_type=edit_type,
                                                            num_plus_lines=num_plus_lines,
                                                            num_minus_lines=num_minus_lines)
            diff_files.append(file_patch_canonical_structure)

        return diff_files

    async def process_file_patch(self, file_patch: FilePatchInfo) -> List[tuple]:
        """
        Processes the file's patch, generating feedback only where necessary.
        Returns a list of tuples containing the line number and feedback comment.
        """
        patch = file_patch.patch
        lines_added, _ = self.parse_patch(patch)
        comments = []

        # Generate feedback only for lines needing it
        for line_number, line in lines_added:
            if needs_feedback(line):  # Check if feedback is required
                feedback = generate_feedback(line)
                if feedback:
                    comments.append((line_number + 1, f"- **Line {line_number + 1}** in `{file_patch.filename}`: {feedback}"))

        return comments

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
                added_lines.append((line_number_added, line[1:].strip()))
                line_number_added += 1
            elif line.startswith('-'):
                removed_lines.append((line_number_removed, line[1:].strip()))
                line_number_removed += 1
        return added_lines, removed_lines

    async def post_comment_on_github(self, comment: str, filename: str, line_number: int, pull_request: Dict[str, Any]):
        """
        Post a comment to GitHub for a specific line in a file, with error handling.
        """
        try:
            number = pull_request.get("number")
            pr = self.repo.get_pull(number)
            
            # Create a general comment for context
            #self.issue.create_comment("Howdy! This is an automated comment from the bot.")
            logger.info(f"PR head commit hash: {pr.head.sha}")
            commit = pr.get_commits().reversed[0]  # Get the latest commit
            # Attempt to post a review comment
            #pr.create_issue_comment(comment)
            pr.create_review_comment(comment, commit, filename, line_number)
            

            # Adjust comment structure with line-specific details if needed
            #pr.create_issue_comment(f"**File**: `{filename}` | **Line**: {line_number}\n{comment}")
            logger.info(f"Posted comment on PR #{number} for file {filename} at line {line_number}")
        
        except Exception as e:
            logger.error(f"Error posting comment on line {line_number} of {filename}: {str(e)}")
            raise
