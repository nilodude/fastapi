from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from matlab_interface import MatlabInterface
from utils import Utils
from session import Session
from fastapi.middleware.cors import CORSMiddleware

import json
import os
import os.path

tags_metadata = [
    {
        "name": "main",
        "description": "Operations needed for the main application",
    },
    {
        "name": "extra",
        "description": "",
    }
]

app = FastAPI(title="Matlab Online Workspace API")

origins = [
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_SESSIONS = 3
HOME = 'D:\\Dropbox\\tfg\\Shazam-MATLAB\\app\\'

utils = Utils()
sessions = [Session(i) for i in range(1, MAX_SESSIONS+1)]


@app.get("/")
def read_root():
    return {"Add /docs to URL to acces Matlab Online Workspace API"}


def getSession(sid: int):
    availables = list(
        filter(lambda s:  s.sid == sid, sessions))
    return availables[0] if len(availables) > 0 else None


@app.get("/sessions", tags=["main"])
def getSessions():
    return {"sessions": [s.toJSON() for s in sessions]}


@app.get("/taskList", tags=["main"])
def tasklist():
    tasks = utils.taskList()
    return utils.toJSON(tasks)


@app.get("/newSession", tags=["main"])
def newSession():
    availables = list(filter(lambda s: s.pid is None, sessions))
    itsNotFull = len(availables) > 0

    if itsNotFull:
        utils.printS('Available Sessions:', availables)
        s = availables[0]
        index = sessions.index(s)
        sessions.pop(index)
        print('Initializing Matlab Session '+str(s.sid)+'...')
        s.matlab = MatlabInterface()
        # s.matlab.run_command('checkStart',False)
        s.pid = s.matlab.run_command("clear,feature('getpid')", False)
        message = 'New Matlab process with PID='+s.pid

        sessions.insert(index, s)

        utils.printS('Updated Sessions: '+message, sessions)
        response = {"result": message, "session": s.toJSON()}
    else:
        message = 'No available sessions'
        response = {"result": message}

    return response


@app.get("/startMatlab", tags=["main"])
def startMatlab(sid: int):
    response = None
    s = getSession(sid)

    isItAvailable = (s is not None) & (s.pid is None)

    if isItAvailable:
        utils.printS('Selected Session:', [s])
        index = sessions.index(s)
        sessions.pop(index)
        print('Initializing Matlab Session '+str(sid)+'...')
        s.matlab = MatlabInterface()
        # s.matlab.run_script('checkStart')
        s.pid = s.matlab.run_command("clear,feature('getpid')", False)
        s.matlab.run_command('clear', False)
        message = 'New Matlab process with PID='+s.pid
        sessions.insert(index, s)

        utils.printS('Updated Sessions: '+message, sessions)
        response = {"result": message, "session": s.toJSON()}
    else:
        message = 'Session ' + str(sid)+' not available, already running PID=' + str(s.pid)
        response = {"result": message}
        print(message)
    return response


@app.get("/stopMatlab", tags=["main"])
def stopMatlab(sid: int, restart: Optional[bool] = False):
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


@app.get("/run", tags=["main"])
def run(sid: int, commands: str):
    session = getSession(sid)
    figures = []
    if hasattr(session, 'matlab') & (session.pid is not None):
        print('Session '+str(sid)+': ')
        res = session.matlab.run_command(commands, True)
        
        figures = session.matlab.run_command('figures', False)
        try:
            figures = figures.replace('\r', '').replace('\n', '')
        except:
            figures = figures
        try:
            result = json.loads(res, strict=False)
        except:
            result = res
        try:
            figures = json.loads(figures, strict=False)
        except:
            figures = figures
    else:
        result = 'Session '+str(sid) + ' is not currently running!'
    return {"result": result, "figures": figures}


@app.get("/getJSON", tags=["extra"])
def getJSON(fileName: str):
    with open(HOME+'db\\json\\'+fileName, 'r') as f:
        res = f.read()
    jsonRes = json.loads(res, strict=False)
    return jsonRes


@app.get("/shouldUpdate", tags=["extra"])
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


@app.post("/addTracks", tags=["extra"])
def add_tracks(sid: int):
    session = getSession(sid)
    if hasattr(session, 'matlab') & (session.pid is not None):
        res = session.matlab.run_script('justAddTracks')
        print(res)
        result = getJSON('metadata.json')
    else:
        result = 'Session '+str(sid) + ' is not currently running!'
    return {"result": result}


@app.post("/test_shazam", tags=["extra"])
def test_shazam(duration: Optional[int] = 3, wipe: Optional[bool] = False):
    if wipe | should_update():
        print('Adding tracks...')
        add_tracks()

    command = "test_shazam {} {}".format(duration, 0)
    result = session.matlab.run_command(command, True)
    print(json.loads(result))
    return {"result": json.loads(result)}
