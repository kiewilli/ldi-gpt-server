from fastapi import FastAPI
import httpx
import os
from datetime import datetime


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
"due_date": datetime.utcfromtimestamp(int(data.get("due_date", 0)) / 1000).strftime('%Y-%m-%d') if data.get("due_date") else "None",
        "assignee": data["assignees"][0]["username"] if data["assignees"] else "Unassigned"
    }

@app.get("/search-task")
async def search_task(name: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{CLICKUP_BASE_URL}/team", headers=HEADERS)
        team_id = res.json()["teams"][0]["id"]

        res = await client.get(
            f"{CLICKUP_BASE_URL}/team/{team_id}/task",
            headers=HEADERS,
            params={"name": name}
        )

    if res.status_code != 200:
        return {"error": "Unable to search tasks."}

    tasks = res.json().get("tasks", [])
    if not tasks:
        return {"message": "No matching task found."}

    task = tasks[0]  # Top match
    return {
        "task_id": task["id"],
        "task_name": task["name"],
        "status": task["status"]["status"],
        "due_date": task.get("due_date"),
        "assignee": task["assignees"][0]["username"] if task["assignees"] else "Unassigned"
    }
