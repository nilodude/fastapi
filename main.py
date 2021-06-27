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
HOME = 'D:\\Dropbox\\tfg\\Shazam-MATLAB\\app\\'
app = FastAPI()
service = Service()
sessions = [Session(i) for i in range(1, MAX_SESSIONS+1)]


@app.get("/")
def read_root():
    return {"Hello": "World"}


def getSession(sid: int):
    availables = list(
        filter(lambda s:  s.sid == sid, sessions))
    return availables[0] if len(availables) > 0 else None


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
    return service.toJSON(tasks)


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


@app.post("/run")
def run(sid: int, commands: str, script: Optional[bool] = False):
    session = getSession(sid)
    figures = []
    if hasattr(session, 'matlab') & (session.pid is not None):
        res = session.matlab.run_script(
            commands) if script else session.matlab.run_command(commands)
        print(res)
        figures = session.matlab.run_command('figures')
        figures = figures.replace('\r', '').replace('\n', '')
        try:
            result = json.loads(res, strict=False)
        except:
            result = res
        try:
            figures = json.loads(figures)
        except:
            figures = figures
    else:
        result = 'Session '+str(sid) + ' is not currently running!'
    return {"result": result, "figures": figures}


@app.get("/getJSON")
def getJSON(fileName: str):
    with open(HOME+'db\\json\\'+fileName, 'r') as f:
        res = f.read()
    jsonRes = json.loads(res, strict=False)
    return jsonRes


@app.get("/shouldUpdate")
def should_update():
    shouldUpdate = True
    musicDir = HOME+'music'
    fileNames = [filename for filename in os.listdir(musicDir)
                 if os.path.isfile(os.path.join(musicDir, filename))]

    importedFiles = getJSON('metadata.json')
    sameSize = len(fileNames) <= len(importedFiles)

    if sameSize:
        for f in fileNames:
            found = list(filter(lambda i: f in i['Filename'], importedFiles))
            if len(found) > 0:
                shouldUpdate = False
            else:
                shouldUpdate = True
                break

    return shouldUpdate


@app.post("/addTracks")
def add_tracks(sid: int):
    session = getSession(sid)
    if hasattr(session, 'matlab') & (session.pid is not None):
        res = session.matlab.run_script('justAddTracks')
        print(res)
        result = getJSON('metadata.json')
    else:
        result = 'Session '+str(sid) + ' is not currently running!'
    return {"result": result}


@app.post("/test_shazam")
def test_shazam(duration: Optional[int] = 3, wipe: Optional[bool] = False):
    if wipe | should_update():
        print('Adding tracks...')
        add_tracks()

    command = "test_shazam {} {}".format(duration, 0)
    result = session.matlab.run_command(command)
    print(json.loads(result))
    return {"result": json.loads(result)}
