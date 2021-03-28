from typing import Optional

from fastapi import FastAPI

from pydantic import BaseModel

from matlab_interface import MatlabInterface

app = FastAPI()

matlab = MatlabInterface()
matlab.run_script('checkStart')


class RunCommand(BaseModel):

    commands: str

    # args: list

    # is_offer: Optional[bool] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/checkMatlab")
def check_matlab():
    return {"result": matlab.run_script('D:\\Dropbox\\666\\fastapi\\checkStart')}


@app.get("/stopMatlab")
def stop_matlab():
    if matlab is not None:
        return {matlab.stop()}
    else:
        return {"already stopped"}


@app.post("/runCommand")
def run_command(runcommand: RunCommand):
    return {"result": matlab.run_command(runcommand.commands)}


@app.post("/runScript")
def run_script(runcommand: RunCommand):
    import json
    return {"result": json.loads(matlab.run_script(runcommand.commands))}


@app.post("/addTracks")
def run_script():
    import json
    return {"result": json.loads(matlab.run_script('justAddTracks'))}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Optional[str] = None):
#     return {"item_id": item_id, "q": q}


# @app.put("/items/{item_id}")
# def update_item(item_id: int, item: Item):

#     return {"item_name": item.name, "item_id": item_id}
