from typing import Optional

from fastapi import FastAPI

from pydantic import BaseModel

from matlab_interface import MatlabInterface

import json
import os
import os.path

app = FastAPI()

matlab = MatlabInterface()
matlab.run_script('checkStart')


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/setPath")
def restart_matlab():
    return {"result": matlab.run_command('cd \'D:\\Dropbox\\tfg\\Shazam-MATLAB\\app\\\'')}


@app.get("/stopMatlab")
def stop_matlab():
    if matlab:
        return {matlab.stop()}
    else:
        return {"already stopped"}


@app.post("/runCommands")
def run_command(commands: str, jsonResponse: Optional[bool] = False):

    res = matlab.run_command(commands)
    print(res)
    if(jsonResponse):
        result = json.loads(res)
    else:
        result = res
    return {"result": result}


# @app.post("/runCommand2")
# def run_command2(commands: str, jsonResponse: Optional[bool] = False):
#     res = matlab2.run_command(commands)
#     print(res)
#     if(jsonResponse):
#         result = json.loads(res)
#     else:
#         result = res
#     return {"result": result}


@app.post("/runScript")
def run_script(script: str, jsonResponse: Optional[bool] = False):
    res = matlab.run_script(script)
    if(jsonResponse):
        result = json.loads(res)
    else:
        result = res
    return {"result": result}


@app.post("/getJSON")
def getJSON(fileName: str):
    with open('D:\\Dropbox\\tfg\\Shazam-MATLAB\\app\\db\\json\\'+fileName, 'r') as f:
        res = f.read()
    jsonRes = json.loads(res, strict=False)
    return {"result": jsonRes,
            "length": len(jsonRes)}

# TODO: check if /music same length as metadata.json


@app.post("/shouldUpdate")
def should_update():
    DIR = 'D:\\Dropbox\\tfg\\Shazam-MATLAB\\app\\music'
    size = len([name for name in os.listdir(DIR)
               if os.path.isfile(os.path.join(DIR, name))])
    res = getJSON('metadata.json').get('length') != size
    return res


@app.post("/addTracks")
def add_tracks():
    res = matlab.run_script('justAddTracks')
    return {"result": json.loads(res)}


@app.post("/test_shazam")
def test_shazam(duration: Optional[int] = 3, wipe: Optional[bool] = False):
    if wipe:
        print('Wipe selected. Adding tracks...')
        add_tracks()

    command = "test_shazam {} {}".format(duration, 0)
    result = matlab.run_command(command)
    print(json.loads(result))
    return {"result": json.loads(result)}
