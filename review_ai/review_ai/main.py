import os
import requests
from fastapi import FastAPI, Request, HTTPException
from github import Github, GithubIntegration, BadCredentialsException
from dotenv import load_dotenv
import logging
from tools.pr_review import PRReview

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve GitHub App ID and key path from environment variables
app_id = os.getenv("APP_ID")
app_key_path = os.getenv("PRIVATE_KEY_PATH")

# Ensure the environment variables are set
if not app_id or not app_key_path:
    raise HTTPException(status_code=500, detail="GitHub App ID or private key path not set in environment variables.")

# Read the bot certificate from the specified path
try:
    with open(os.path.expanduser(app_key_path), 'r') as cert_file:
        app_key = cert_file.read()
except FileNotFoundError:
    raise HTTPException(status_code=500, detail=f"Private key file not found at path {app_key_path}")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error reading private key file: {str(e)}")

# Create a GitHub integration instance
try:
    git_integration = GithubIntegration(app_id, app_key)
except Exception as e:
    logger.error(f"Failed to create GitHub integration: {str(e)}")
    raise HTTPException(status_code=500, detail="Failed to create GitHub integration.")

@app.post("/")
async def bot(request: Request):
    try:
        # Get the event payload
        payload = await request.json()
        event = request.headers.get("X-GitHub-Event", None)

        # Check if the event is a GitHub PR creation event
        if event != 'pull_request':
            return {"status": "Event not related to pull requests"}

        action = payload.get('action')
        print(f"Received event: {event}, action: {action}")
        # if action != 'opened':
        #     return {"status": "PR not opened, skipping"}

        owner = payload['repository']['owner']['login']
        repo_name = payload['repository']['name']

        # Get a git connection as the bot
        installation = git_integration.get_installation(owner, repo_name)
        if not installation:
            raise HTTPException(status_code=400, detail="GitHub installation not found.")
        
        git_connection = Github(login_or_token=git_integration.get_access_token(installation.id).token)
        repo = git_connection.get_repo(f"{owner}/{repo_name}")

        issue = repo.get_issue(number=payload['pull_request']['number'])

        # Process the PR with PRReview (you can define the PRReview class and handle review here)
        pr_review = PRReview(repo)  # Assuming PRReview takes the payload to process it
        await pr_review.handle_request(payload, event)

        # Create a comment with the random meme
        issue.create_comment("Howdy! This is an automated comment from the bot.")
        return {"status": "PR opened, comment added successfully"}

    except requests.RequestException as e:
        logger.error(f"Request to meme-api failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Error while contacting meme-api.")
    except BadCredentialsException as e:
        logger.error(f"GitHub credentials error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid GitHub credentials.")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

# Run with uvicorn instead of app.run
# Command to run: uvicorn main:app --reload
