import json
import os
import subprocess
from task import Task
from matlab_interface import MatlabInterface
from service import Service

service = Service()


class Session:
    matlab: MatlabInterface
    pid: int

    # def __init__(self, matlab):
    #     self.matlab = matlab
    #     self.matlab.run_script('checkStart')

    #     tasks = service.taskList()

    #     if len(tasks) > 1:
    #         tasks.sort(key=lambda x: x.cpuTime, reverse=True)

    #     self.pid = tasks[0].pid

    #     print('New Matlab process with PID: '+self.pid)
