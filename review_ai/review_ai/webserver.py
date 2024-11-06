from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from review_ai.tools.pr_review import PRReview
app = FastAPI()

def push_event(data):
    print("push event", data)
    # push_event = PushEvent(**data)
    # author = push_event.head_commit['author']['username']
    # branch = push_event.ref.split('/')[-1]
    # timestamp = datetime.strptime(push_event.head_commit['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
    # event_data = {
    #     "type": "push",
    #     "author": author,
    #     "branch": branch,
    #     "timestamp": timestamp.isoformat()
    # }
    # print(event_data)
    # return event_data

@app.post("/webhook")
async def webhook(request: Request):
    event_type = request.headers.get('X-GitHub-Event')
    data = await request.json()
    print("look here", data, event_type)
    if event_type == 'push':
        await push_event(data)
        
    # elif event_type == 'pull_request':
    #     pull_request_event = PullRequestEvent(**data)
    #     author = pull_request_event.user['login']
    #     from_branch = pull_request_event.head['ref']
    #     to_branch = pull_request_event.base['ref']
    #     timestamp = datetime.strptime(pull_request_event.created_at, "%Y-%m-%dT%H:%M:%SZ")
    #     event_data = {
    #         "type": "pull_request",
    #         "author": author,
    #         "from_branch": from_branch,
    #         "to_branch": to_branch,
    #         "545554": timestamp.isoformat()
    #     }

    #     if pull_request_event.merged:
    #         timestamp = datetime.strptime(pull_request_event.merged_at, "%Y-%m-%dT%H:%M:%SZ")
    #         event_data = {
    #             "type": "merge",
    #             "author": author,
    #             "from_branch": from_branch,
    #             "to_branch": to_branch,
    #             "timestamp": timestamp.isoformat()
    #         }
    # else:
    #     print(f"Unsupported event type: {event_type}")

    return JSONResponse(content={'message': 'Event received'}, status_code=200)

@app.get("/events")
async def get_events():
    events = []  # Replace with your database call to retrieve events
    # Sort and limit events as necessary, e.g., collection.find().sort("timestamp", -1).limit(10)
    # for event in events:
    #     event['_id'] = str(event['_id'])  # Convert MongoDB ObjectId to string
    return JSONResponse(content=events, status_code=200)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
