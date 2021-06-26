import json
import os
import subprocess
from task import Task


class Service:

    def taskList(self):
        output = subprocess.run(
            'tasklist /FI "imagename eq matlab.exe" /v /fo csv /nh', check=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
        taskList = list(filter(None, output.split('\r\n')))
        tasks = [Task(task) for task in taskList]

        return [json.loads(json.dumps(task.__dict__)) for task in tasks]
