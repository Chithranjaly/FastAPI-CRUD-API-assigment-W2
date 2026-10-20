
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi import Request
from fastapi.encoders import jsonable_encoder

app = FastAPI(title = "Task CRUD API")


tasks = [
    {"id":1, "title":"Learn FastAPI","done":False},
    {"id":2, "title":"Build CRUD API","done":False},
    {"id":3, "title":"Deploy the application","done":False},
]
@app.get("/")
def root():
    return {"name":"Task API","version":"1.0","endpoints":["/tasks","/tasks/id","/health"
    ""]}


# @app.get("/tasks")           # without filtering
# def get_tasks():
#     return tasks


# @app.get("/tasks")                  #with filtering
# def get_tasks(done:bool | None = None):
#     if done is None:
#         return tasks

#     return [task for task in tasks if task["done"] == done]


@app.get("/tasks")                  #with filtering and search
def get_tasks(done:bool | None = None, search:str | None = None):
    filtered_tasks = tasks

    if done is not None:
        filtered_tasks = [
            task for task in filtered_tasks
            if task["done"] == done
        ]


    if search is not None:
        filtered_tasks = [
            task for task in filtered_tasks
            if search.strip().lower() in task["title"].lower()
        ]

    return filtered_tasks


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
    return {"status":"ok"}


class TaskCreate(BaseModel):
    title:str


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = exc.errors()

    if request.method == "POST" and request.url.path == "/tasks":
        missing_title = any(
            tuple(error.get("loc", ())) == ("body", "title")
            and error.get("type") == "missing"
            for error in errors
        )

        if missing_title:
            return JSONResponse(
                status_code=400,
                content={"error": "Task title is required"},
            )

        return JSONResponse(
            status_code=400,
            content={"error": "Invalid request body"},
        )

    if request.method == "PUT" and request.url.path.startswith("/tasks/"):
        has_body_error = any(
            error.get("loc", (None,))[0] == "body"
            for error in errors
        )

        if has_body_error:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid request body"},
            )

    return JSONResponse(
        status_code=422,
        content={"detail": jsonable_encoder(errors)},
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



class TaskUpdate(BaseModel):
    title:str | None=None
    done:bool | None=None




@app.put("/tasks/{task_id}")
def update_task(task_id:int,task_update:TaskUpdate):
    if task_update.title is None and task_update.done is None:
        return JSONResponse(
            status_code=400,
            content={
                "error":"At least one field is required!"
            }

        )
    for task in tasks:
        if task["id"] == task_id:
            if task_update.title is not None:
                title = task_update.title.strip()

                if not title:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error":"The title can't be empty"
                        },

                    )

                task["title"] = title


            if task_update.done is not None:
                task["done"] = task_update.done

            return task

    return JSONResponse(
        status_code=404,
        content={
            "error":f"Task with id {task_id} not found"
        },
    )


@app.delete("/tasks/{task_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id:int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return

    return JSONResponse(
        status_code=404,
        content={
            "error":f"Task with id {task_id} not found!"
        }
    )



@app.get("/stats")
def get_stats():
    total = len(tasks)
    completed = sum(1 for task in tasks if task["done"])
    open_tasks = total - completed

    return{
        "total":total,
        "done": completed,
        "open": open_tasks,
    }
        

@app.post("/reset")
def reset_tasks():
    tasks.clear()
    tasks.extend([
        {"id":1, "title":"Learn FastAPI","done":False},
        {"id":2, "title":"Build CRUD API","done":False},
        {"id":3, "title":"Deploy the application","done":False},

    ])
    return {"message":"Tasks reset successfully!", "tasks":tasks}
    