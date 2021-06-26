from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from matlab_interface import MatlabInterface
from service import Service
from session import Session

import json
import os
import os.path

MAX_SESSIONS = 3
app = FastAPI()
service = Service()
sessions = [Session(i) for i in range(1, MAX_SESSIONS+1)]

# TODO: must check matlab instances running before instancing new one
# TODO: then once new instance running, save PID for identifying with python "session"
# TODO: to identify your own matlab session,
# matlab PID from python command must match matlab PID from matlab command


@app.get("/newSession")
def newSession():
    availables = list(filter(lambda x: x.pid is None, sessions))
    service.printS('Available Sessions:', availables)
    itsNotFull = len(availables) > 0
    if itsNotFull:
        s = availables[0]
        index = sessions.index(s)
        sessions.pop(index)
        print('Starting Session '+str(s.sid))
        s.matlab = MatlabInterface()
        s.matlab.run_script('checkStart')

        tasks = service.taskList()

        s.pid = tasks[0].pid
        s.matlabPID = s.matlab.run_command("feature('getpid')")
        message = 'New Matlab process with PID='+s.pid
        sessions.insert(index, s)

        service.printS('Updated Sessions: '+message, sessions)
        response = {"result": message, "session": {
            "pid": s.pid, "sid": s.sid, "matlabPID": s.matlabPID}}
    else:
        message = 'No empty sessions available'
        response = {"result": message}

    print(response)

    return response


@app.get("/sessions")
def getSessions():
    return [{"pid": s.pid, "sid": s.sid, "matlabPID": s.matlabPID if s.matlabPID is not None else ""} for s in sessions]


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
