import json
import os
import subprocess
from task import Task


class Service:

    def taskList(self):
        output = subprocess.run(
            'tasklist /FI "imagename eq matlab.exe" /v /fo csv /nh', check=True, stdout=subprocess.PIPE).stdout
        if str(output).__contains__('criterios especificados.'):
            tasks = []
        else:
            output = output.decode('utf-8')
            taskList = list(filter(None, output.split('\r\n')))
            tasks = [Task(task) for task in taskList]
            response = [json.loads(json.dumps(task.__dict__))
                        for task in tasks]
            print(response)
        return tasks
