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


def getSession(sid: int):
    availables = list(
        filter(lambda s:  s.sid == sid, sessions))
    return availables[0] if len(availables) > 0 else None


# TODO: must check matlab instances running before instancing new one
# TODO: then once new instance running, save PID for identifying with python "session"
# TODO: to identify your own matlab session,
# matlab PID from python command must match matlab PID from matlab command


@app.get("/newSession")
def newSession():
    availables = list(filter(lambda s: s.pid is None, sessions))
    itsNotFull = len(availables) > 0

    if itsNotFull:
        service.printS('Available Sessions:', availables)
        s = availables[0]
        index = sessions.index(s)
        sessions.pop(index)
        print('Initializing Matlab Session '+str(s.sid)+'...')
        s.matlab = MatlabInterface()
        s.matlab.run_script('checkStart')

        tasks = service.taskList()

        s.pid = tasks[0].pid
        s.matlabPID = s.matlab.run_command("feature('getpid')")
        message = 'New Matlab process with PID='+s.pid
        sessions.insert(index, s)

        service.printS('Updated Sessions: '+message, sessions)
        response = {"result": message, "session": s.toJSON()}
    else:
        message = 'No available sessions'
        response = {"result": message}

    return response


@app.get("/sessions")
def getSessions():
    return {"sessions": [s.toJSON() for s in sessions]}


@app.get("/startMatlab")
def startMatlab(sid: int):
    response = None
    s = getSession(sid)

    isItAvailable = (s is not None) & (s.pid is None)

    if isItAvailable:
        service.printS('Selected Session:', [s])
        # s = availables[0]
        index = sessions.index(s)
        sessions.pop(index)
        print('Initializing Matlab Session '+str(sid)+'...')
        s.matlab = MatlabInterface()
        s.matlab.run_script('checkStart')

        tasks = service.taskList()

        s.pid = tasks[0].pid
        s.matlabPID = s.matlab.run_command("feature('getpid')")
        message = 'New Matlab process with PID='+s.pid
        sessions.insert(index, s)

        service.printS('Updated Sessions: '+message, sessions)
        response = {"result": message, "session": s.toJSON()}
    else:
        message = 'Session ' + \
            str(sid)+' not available, already running PID=' + \
            str(s.pid)
        response = {"result": message}
        print(message)

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


@app.get("/restartSession")
def restart_matlab(sid: int):
    print('Session '+str(sid)+' Restart Selected')
    session = getSession(sid)
    if hasattr(session, 'matlab'):
        session.matlab.stop()
        session.pid = None
        session.matlabPID = None
        session.matlab = None
        response = startMatlab(session.sid)
    else:
        msg = 'Session '+str(sid) + ' is not currently running!'
        response = {"result": msg}
        print(msg)
    return response


@app.get("/stopMatlab")
def stop_matlab(sid: int, restart: Optional[bool] = False):
    option = ' Restart ' if restart else ' Stop '
    print('Session '+str(sid)+option+'Selected')
    session = getSession(sid)
    if hasattr(session, 'matlab') & (session.pid is not None):
        session.matlab.stop()
        session.pid = None
        session.matlabPID = None
        session.matlab = None
        msg = 'Session '+str(sid) + ' stopped'
        response = startMatlab(session.sid) if restart else {"result": msg}
    else:
        msg = 'Session '+str(sid) + ' is not currently running!'
        response = {"result": msg}
        print(msg)
    return response


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
