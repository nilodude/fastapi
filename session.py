import json
import os
from matlab_interface import MatlabInterface

class Session:
    sid = None
    matlab: MatlabInterface
    pid = None

    def __init__(self, sid):
        self.sid = sid

    def toJSON(self):
        return {"sid": self.sid, "pid": self.pid}
