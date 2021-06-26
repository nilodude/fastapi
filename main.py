from typing import Optional

from fastapi import FastAPI

from pydantic import BaseModel

from matlab_interface import MatlabInterface

import json
import os
import os.path
import subprocess

app = FastAPI()

# TODO: must check matlab instances running before instancing new one


matlab = MatlabInterface()
# TODO: then once new instance running, save PID for identifying with python "session"
matlab.run_script('checkStart')


@app.get("/taskList")
def tasklist():
    taskList = subprocess.check_output(
        'tasklist /FI "imagename eq matlab.exe" /fo table /nh', shell=True)

    print(taskList)
    return {"result": taskList}


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


@app.get("/getJSON")
def getJSON(fileName: str):
    with open('D:\\Dropbox\\tfg\\Shazam-MATLAB\\app\\db\\json\\'+fileName, 'r') as f:
        res = f.read()
    jsonRes = json.loads(res, strict=False)
    return {"result": jsonRes,
            "length": len(jsonRes)}


@app.get("/shouldUpdate")
def should_update():
    DIR = 'D:\\Dropbox\\tfg\\Shazam-MATLAB\\app\\music'
    size = len([name for name in os.listdir(DIR)
               if os.path.isfile(os.path.join(DIR, name))])
    filenames = [name for name in os.listdir(DIR)
                 if os.path.isfile(os.path.join(DIR, name))]
    print(filenames)
    res = getJSON('metadata.json').get('length') != size
    return res


@app.post("/addTracks")
def add_tracks():
    res = matlab.run_script('justAddTracks')
    return {"result": json.loads(res)}


@app.post("/test_shazam")
def test_shazam(duration: Optional[int] = 3, wipe: Optional[bool] = False):
    if wipe | should_update():
        print('Adding tracks...')
        add_tracks()

    command = "test_shazam {} {}".format(duration, 0)
    result = matlab.run_command(command)
    print(json.loads(result))
    return {"result": json.loads(result)}
