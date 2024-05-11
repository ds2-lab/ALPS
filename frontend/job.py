class Job:
    def __init__(self, name, startTime, burstTime, classid, jobid, funcid, Priority = 0):
        self.name = name
        self.startTime = startTime
        self.burstTime = burstTime
        self._remainingTime = self.burstTime
        self.Priority = Priority
        self.classid = classid
        self.id = jobid
        self.funcid = funcid
        self.executed = 0
        self.endTime = -1
        self.contextS = 0
        self.waitTime = -1
    
    def execute(self):
        self._remainingTime -= 1
        self.executed += 1

    def executedTime(self):
        return self.executed
    
    def isEnd(self):
        return self._remainingTime == 0
    
    def __lt__(self, other):
        return self.id < other.id
    
    def __str__(self):
        return f"job instance with value: <{self.name}, {self.startTime}, {self.burstTime}>"