import json
import os
import subprocess
from task import Task
from matlab_interface import MatlabInterface
from service import Service

service = Service()


class Session:
    sid = None
    matlab: MatlabInterface
    pid = None
    matlabPID = None

    def __init__(self, sid):
        self.sid = sid

    def toJSON(self):
        return {"pid": self.pid, "sid": self.sid, "matlabPID": self.matlabPID}
