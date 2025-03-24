from fastapi import FastAPI
import httpx
import os

app = FastAPI()

CLICKUP_API_KEY = os.environ.get("CLICKUP_API_KEY")
CLICKUP_BASE_URL = "https://api.clickup.com/api/v2"
HEADERS = {"Authorization": CLICKUP_API_KEY}

@app.get("/")
def root():
    return {"message": "LDI Guide ClickUp Proxy is live!"}

@app.get("/course-status")
async def get_course_status(task_id: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{CLICKUP_BASE_URL}/task/{task_id}", headers=HEADERS)

    if res.status_code != 200:
        return {"error": "Unable to fetch course data."}

    data = res.json()
    return {
        "task_name": data["name"],
        "status": data["status"]["status"],
        "due_date": data.get("due_date"),
        "assignee": data["assignees"][0]["username"] if data["assignees"] else "Unassigned"
    }
