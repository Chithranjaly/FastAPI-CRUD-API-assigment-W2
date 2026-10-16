
from fastapi import FastAPI

app = FastAPI(title = "Task CRUD API")


tasks = [
    {"id":1, "title":"Learn FastAPI","done":False},
    {"id":2, "title":"Build CRUD API","done":False},
]
@app.get("/")
def root():
    return {"name":"Task API","version":"1.0","endpoints":["/tasks"]}


@app.get("/tasks")
def get_tasks():
    return tasks


@app.get("/health")
def health_check():
    return {"Status":"ok"}