import json
import os
import subprocess
from matlab_interface import MatlabInterface
from service import Service

service = Service()


class Session:
    sid = None
    matlab: MatlabInterface
    pid = None

    def __init__(self, sid):
        self.sid = sid

    def toJSON(self):
        return {"sid": self.sid, "pid": self.pid}
