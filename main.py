from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from matlab_interface import MatlabInterface
from service import Service
from session import Session

import json
import os
import os.path

app = FastAPI()
service = Service()
session1 = Session()
session2 = Session()
# TODO: must check matlab instances running before instancing new one
# TODO: then once new instance running, save PID for identifying with python "session"
# TODO: to identify your own matlab session,
# matlab PID from python command must match matlab PID from matlab command


@app.get("/newSession1")
def newSession1():
    # session1 = Session()
    session1.matlab = MatlabInterface()
    session1.matlab.run_script('checkStart')

    tasks = service.taskList()

    if len(tasks) > 1:
        tasks.sort(key=lambda x: x.cpuTime, reverse=False)

    session1.pid = tasks[0].pid

    print('New Matlab process with PID: '+session1.pid)
    # print(response)
    return session1.pid


@app.get("/newSession2")
def newSession2():
    # session2 = Session()
    session2.matlab = MatlabInterface()
    session2.matlab.run_script('checkStart')

    tasks = service.taskList()

    if len(tasks) > 1:
        tasks.sort(key=lambda x: x.cpuTime, reverse=False)

    session2.pid = tasks[0].pid

    print('New Matlab process with PID: '+session2.pid)
    # print(response)
    return session2.pid


@app.get("/startMatlab")
def startMatlab():
    if sesion is not None:
        response = session.startMatlab()
    else:
        response = 'no session'
    # print(response)
    return response


@app.get("/taskList")
def tasklist():
    tasks = service.taskList()
    response = [json.loads(json.dumps(task.__dict__))
                for task in tasks]
    return response


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/setPath")
def restart_matlab():
    return {"result": session.matlab.run_command('cd \'D:\\Dropbox\\tfg\\Shazam-MATLAB\\app\\\'')}


@app.get("/stopMatlab")
def stop_matlab():
    if session.matlab:
        return {session.matlab.stop()}
    else:
        return {"already stopped"}


@app.post("/runCommands")
def run_command(commands: str, jsonResponse: Optional[bool] = False):

    res = session.matlab.run_command(commands)
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
    res = session.matlab.run_script(script)
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
    res = session.matlab.run_script('justAddTracks')
    return {"result": json.loads(res)}


@app.post("/test_shazam")
def test_shazam(duration: Optional[int] = 3, wipe: Optional[bool] = False):
    if wipe | should_update():
        print('Adding tracks...')
        add_tracks()

    command = "test_shazam {} {}".format(duration, 0)
    result = session.matlab.run_command(command)
    print(json.loads(result))
    return {"result": json.loads(result)}
