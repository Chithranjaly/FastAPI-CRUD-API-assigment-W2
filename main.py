
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi import Request

app = FastAPI(title = "Task CRUD API")


tasks = [
    {"id":1, "title":"Learn FastAPI","done":False},
    {"id":2, "title":"Build CRUD API","done":False},
    {"id":3, "title":"Deploy the application","done":False},
]
@app.get("/")
def root():
    return {"name":"Task API","version":"1.0","endpoints":["/tasks"]}


@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id:int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task not found with id: {task_id}"}
    ) 
    
        


@app.get("/health")
def health_check():
    return {"Status":"ok"}


class TaskCreate(BaseModel):
    title:str


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request:Request,
    exc:RequestValidationError
):
    if request.method == "POST" and request.url.path == "/tasks":
        return JSONResponse(
            status_code=400,
            content={"error":"Task title is required!"}
        )

    return JSONResponse(
        status_code=422,
        content={"detail":exc.errors()}
    )

@app.post("/tasks",status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    title = task.title.strip()

    if not title:
        return JSONResponse(
            status_code=400,
            content={"error":"Task title cannot be empty"}
        )

    new_id = max((task["id"] for task in tasks),default=0)+1

    new_task = {
        "id":new_id,
        "title":title,
        "done":False,

    }

    tasks.append(new_task)
    return new_task

