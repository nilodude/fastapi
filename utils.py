import json
import os
import subprocess
from task import Task


class Utils:

    def taskList(self):
        output = subprocess.run(
            'tasklist /FI "imagename eq matlab.exe" /v /fo csv /nh', check=True, stdout=subprocess.PIPE).stdout
        if str(output).__contains__('criterios especificados.'):
            tasks = []
        else:
            output = output.decode('utf-8')
            taskList = list(filter(None, output.split('\r\n')))
            tasks = [Task(task) for task in taskList]
        return tasks

    def printS(self, title, sessions):
        print(title)
        for s in sessions:
            print(' ', vars(s))

    def toJSON(self, input):
        response = []
        for s in input:
            if not hasattr(s, 'matlab'):
                response.append(json.loads(json.dumps(vars(s))))
            else:
                response.append({
                    "pid": s.pid, "sid": s.sid})
        return response
