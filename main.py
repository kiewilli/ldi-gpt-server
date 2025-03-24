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
    LIST_ID = "6-381118276-1"

    async with httpx.AsyncClient() as client:
        res = await client.get(f"{CLICKUP_BASE_URL}/list/{LIST_ID}/task", headers=HEADERS)
        tasks = res.json().get("tasks", [])

    # Simple case-insensitive search
    matches = [t for t in tasks if name.lower() in t["name"].lower()]
    if not matches:
        return {"message": f"No task found containing '{name}'."}

    task = matches[0]
    return {
        "task_id": task["id"],
        "task_name": task["name"],
        "status": task["status"]["status"],
        "due_date": task.get("due_date"),
        "assignee": task["assignees"][0]["username"] if task["assignees"] else "Unassigned"
    }


@app.get("/debug/team-space")
async def debug_team_space():
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{CLICKUP_BASE_URL}/team", headers=HEADERS)
        team_data = res.json()

        team_id = team_data.get("teams", [{}])[0].get("id", "No team ID")
        print("Team ID:", team_id)

        res_spaces = await client.get(f"{CLICKUP_BASE_URL}/team/{team_id}/space", headers=HEADERS)
        space_data = res_spaces.json()

        return {
            "team_data": team_data,
            "space_data": space_data
        }

@app.get("/debug/lists")
async def debug_lists():
    async with httpx.AsyncClient() as client:
        # Get all spaces for your team
        res = await client.get(f"{CLICKUP_BASE_URL}/team/24555507/space", headers=HEADERS)
        spaces = res.json().get("spaces", [])

        all_lists = []

        for space in spaces:
            space_id = space["id"]
            # Get folders in this space
            folder_res = await client.get(f"{CLICKUP_BASE_URL}/space/{space_id}/folder", headers=HEADERS)
            folders = folder_res.json().get("folders", [])

            for folder in folders:
                for lst in folder.get("lists", []):
                    all_lists.append({
                        "space_name": space["name"],
                        "folder_name": folder["name"],
                        "list_name": lst["name"],
                        "list_id": lst["id"]
                    })

        return {"lists": all_lists}
