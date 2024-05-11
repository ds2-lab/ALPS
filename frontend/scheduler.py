import numpy as np
from sklearn.linear_model import LinearRegression
import squeue
from job import Job
import analyze
from utility import generateOutput, checkContextSwitch

class Scheduler:
    def next(self):
        pass

    def enqueue(self, job):
        pass


class RRScheduler(Scheduler):
    def __init__(self):
        self.q = squeue.FIFOQueue()

    def next(self):
        return self.q.dequeue()
    
    def enqueue(self, job):
        self.q.enqueue(job)
    
    def is_empty(self):
        return self.q.is_empty()
    
class FIFOScheduler(Scheduler):
    def __init__(self):
        self.q = squeue.FIFOQueue()

    def next(self):
        return self.q.dequeue()
    
    def enqueue(self, job):
        self.q.enqueue(job)
    
    def is_empty(self):
        return self.q.is_empty()
    
class SFSScheduler(Scheduler):
    def __init__(self, timeSlice, period, SRTFSimulationPath = ""):
        self.q = squeue.SFSPriorityQueue()
        self.timeSlice = timeSlice
        self.path = SRTFSimulationPath
        self.period = period
        self.orginialTimeSlice = timeSlice
        self.iat = timeSlice
        self.startNum = 0
        self.startT = 0
        self.arrival = 0
        self.waitingT = 0

    def next(self):
        return self.q.dequeue()
    
    def updateArrival(self):
        self.arrival += 1
    
    def enqueue(self, job):
        self.q.enqueue(job)
    
    def firstEnqueue(self, job):
        self.q.firstEnqueue(job)
    
    def is_empty(self):
        return self.q.is_empty()
    
    def updatePolicy(self, t):
        if self.arrival == 0:
            self.iat = 6
        else:
            self.iat = int((t - self.startT)/self.arrival)
            if self.iat < self.orginialTimeSlice:
                self.iat = self.orginialTimeSlice
            self.startT = t
            self.arrival = 0

    def getTimeSlice(self, job):
        if job.Priority == 0:
            lastWaiting = self.waitingT
            self.waitingT = job.waitTime
            if lastWaiting > self.iat:
                return self.iat
            return self.iat
        else:
            return self.orginialTimeSlice

class SRTFScheduler(Scheduler):
    def __init__(self):
        self.q = squeue.SRTFPriorityQueue()

    def next(self):
        return self.q.dequeue()
    
    def enqueue(self, job):
        self.q.enqueue(job)
    
    def is_empty(self):
        return self.q.is_empty()
    
    def checkContextSwitch(self, job, timeS):
        if job.executed < timeS:
            return False
        hp_remainingTime = self.q.get_hp_remainingTime()
        if hp_remainingTime:
            return hp_remainingTime < job._remainingTime
        else:
            return False
        
class SEALScheduler(Scheduler):
    def __init__(self, timeSlice, period, SRTFSimulationPath = ""):
        self.q = squeue.SEALPriorityQueue()
        self.timeSlice = timeSlice
        self.policies = {i: self.timeSlice for i in range(1,6)}
        self.path = SRTFSimulationPath
        self.period = period
        self.orginialTimeSlice = timeSlice

    def getTimeSlice(self, jb):
        return self.policies[jb.classid]
    
    def statistical(self, tsD_id, wtD_id, csD_id):
        tsMedian = np.median(tsD_id)
        wtMedian = np.median(wtD_id)
        return int(tsMedian - wtMedian) if tsMedian > wtMedian + 1 else 1
    
    def linearRegression(self, tsD_id, wtD_id, csD_id):
        combined = list(zip(tsD_id, csD_id))
        sorted_combined = sorted(combined, key=lambda x: x[0])
        tsD_id, csD_id = zip(*sorted_combined)
        X = np.array(csD_id).reshape(-1,1)
        y = np.array(tsD_id)
        model = LinearRegression()
        model.fit(X, y)
        return model.predict(np.array([[csD_id[-1]]]))[0]
        
    
    def updatePolicy(self, log, csCostAdjust, method = "stat"):
        workload = log.finishedWorkload[-self.period:]
        workload = sorted(workload, key=lambda x: x.startTime)
        tsD, wtD, csD = self.offlineSimulate(workload, csCostAdjust)
        for classid in tsD:
            print(classid, self.linearRegression(tsD[classid], wtD[classid], csD[classid]),self.statistical(tsD[classid], wtD[classid], csD[classid]))
            if method == "stat":
                self.policies[classid] = self.statistical(tsD[classid], wtD[classid], csD[classid])
        
        
    def offlineSimulate(self, workload, csCost):
        timePath = {}
        offLog = analyze.simulateLog(self.orginialTimeSlice)
        for jb in workload:
            if jb.startTime not in timePath:
                timePath[jb.startTime] = [jb]
            else:
                timePath[jb.startTime].append[jb]
        offsched = SRTFScheduler()
        t = 0
        finishedJobs = 0
        hasContextSwitch = True
        csCostAdjust = 0
        while finishedJobs < len(workload):
            if t in timePath:
                for jb in timePath[t]:
                    offsched.enqueue(jb)      
            if csCostAdjust >= 1000:
                t += 1
                csCostAdjust -= 1000
                continue
            if offsched.is_empty() and hasContextSwitch:
                t += 1
                offLog.idle += 1
            else:
                if hasContextSwitch:
                    hasContextSwitch = False
                    j = offsched.next()
                    if j.waitTime == -1:
                        j.waitTime = t - j.startTime
                    j.execute()
                    if checkContextSwitch("srtf", j, offsched, self.orginialTimeSlice):
                        hasContextSwitch = True
                        if j.isEnd():
                            finishedJobs += 1
                            j.endTime = t
                            offLog.jobEnd(j, t, csCostAdjust)
                        else:
                            j.contextS += 1
                            offsched.enqueue(j)
                            offLog.jobContextSwitch(j, t)
                        j.executed = 0
                else:
                    j.execute()
                    hasContextSwitch = False
                    if checkContextSwitch("srtf", j, offsched, self.orginialTimeSlice):
                        hasContextSwitch = True
                        if j.isEnd():
                            finishedJobs += 1
                            j.endTime = t
                            offLog.jobEnd(j, t, csCostAdjust)
                        else:
                            j.contextS += 1
                            offsched.enqueue(j)
                            offLog.jobContextSwitch(j, t)
                        j.executed = 0
                t += 1
        offLog.total = t
        
        wtD = {classid: [] for classid in offLog.jobSummary}
        for classid in offLog.jobSummary:
            for name in offLog.jobSummary[classid]:
                wtD[classid].append(offLog.jobSummary[classid][name]["wait"])


        tsD = {classid: [] for classid in offLog.timeSlice.keys()}
        csD = {classid: [] for classid in offLog.contextS.keys()}
        for classid in offLog.timeSlice.keys():
            tscollection = offLog.timeSlice[classid]
            cscollection = offLog.contextS[classid]
            for k in tscollection:
                if len(tscollection[k]) == 1:
                    tsD[classid].append(tscollection[k][0])
                    csD[classid].append(cscollection[k][0])
                else:
                    for i in range(len(tscollection[k])-1):
                        tsD[classid].append(tscollection[k][i])
                        csD[classid].append(cscollection[k][i])
        return tsD, wtD, csD

    def next(self):
        return self.q.dequeue()
    
    def enqueue(self, job):
        self.q.enqueue(job)
    
    def is_empty(self):
        return self.q.is_empty()
    
    def checkContextSwitch(self, job, timeS):
        if job.executed < timeS:
            return False
        hp_priority = self.q.get_hp_priority()
        if hp_priority:
            return hp_priority <= job.Priority
        else:
            return False