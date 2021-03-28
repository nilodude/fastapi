from typing import Optional

from fastapi import FastAPI

from pydantic import BaseModel

from matlab_interface import MatlabInterface

app = FastAPI()

matlab = MatlabInterface()
matlab.run_script('checkStart')


class RunCommand(BaseModel):

    command: str

    # args: list

    jsonResponse: Optional[bool] = False


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
    res = matlab.run_script(runcommand.commands)
    if(runcommand.jsonResponse):
        result = json.loads(res)
    else:
        result = res
    return {"result": result}


@app.post("/addTracks")
def add_tracks():
    import json
    return {"result": json.loads(matlab.run_script('justAddTracks'))}


@app.post("/test_shazam")
def test_shazam(duration: Optional[int] = 3, wipe: Optional[bool] = False):
    import json
    command = "test_shazam {} {}".format(duration, int(wipe))
    if wipe:
        print('Wipe selected. Adding tracks...')
    result = matlab.run_command(command)
    print(result)
    print(json.loads(result))
    return {"result": json.loads(result)}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Optional[str] = None):
#     return {"item_id": item_id, "q": q}


# @app.put("/items/{item_id}")
# def update_item(item_id: int, item: Item):

#     return {"item_name": item.name, "item_id": item_id}
