import os


class Task:
    imageName: str
    pid: int
    sessionName: str
    sessionNum: int
    memory: str
    status: str
    userName: str
    cpuTime: str
    windowName: str

    def __init__(self, task):
        fields = task.split(',')
        fields = [f.replace('"', '') for f in fields]
        # print(fields)
        self.imageName = fields[0]
        self.pid = fields[1]
        self.cpuTime = fields[7]
        self.windowName = fields[8]
