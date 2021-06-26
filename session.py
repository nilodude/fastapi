import json
import os
import subprocess
from task import Task
from matlab_interface import MatlabInterface
from service import Service

service = Service()


class Session:
    sid: int
    matlab: MatlabInterface
    pid = None
    matlabPID: int

    def __init__(self, sid):
        self.sid = sid
