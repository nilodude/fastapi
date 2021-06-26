import os


class Task:
    imageName: str
    pid: int
    sessionName: str
    sessionNum: int
    memory: str
    status: str
    userName: str
    cpuTime: int
    windowName: str

    def __init__(self, task):
        fields = task.split(',')
        fields = [f.replace('"', '') for f in fields]
        # print(fields)
        self.imageName = fields[0]
        self.pid = fields[1]
        time = fields[7].split(':')
        h = int(time[0])
        m = int(time[1])
        s = int(time[2])
        h = h if h == 0 else h*3600
        m = m if m == 0 else m*60
        self.cpuTime = int(h+m+s)
        self.windowName = fields[8]
