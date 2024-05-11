import job
import numpy as np
import random
from cpu_time import read_cpuT

SEAL_LOGS = "/mydata/seal_logs"


def readWorkload(init, init_v, lens = 100):
    lines = open(SEAL_LOGS,"r").readlines()
    wl = []
    if len(lines) <= 0:
        return wl, init_v
    w = []
    bt = {}
    invocationId = 1
    for line in lines:
        strdata = line.split("\"")[-2].split(";")
        startTime = int(strdata[0].split(":")[-1])
        class_id = int(strdata[2].split(":")[-1])
        funcName = strdata[3].split(":")[-1].strip()
        burstTime = int(strdata[4].split(":")[-1])
        invocationId += 1
        if class_id not in bt:
            bt[class_id] = []
        bt[class_id].append(burstTime)   
        w.append([invocationId, startTime, burstTime, class_id, invocationId, func_class_id(funcName)])
    w = random.sample(w, len(w)//24)
    w = sorted(w,key=lambda k: k[1])
    length = lens if len(w) > lens else len(w)
    rw = w[-length:]
    initSt = rw[0][1]
    for d in rw:
        invocationId, startTime, burstTime, class_id, invocationId, func_id = d
        startTime -= initSt
        wl.append(job.Job(invocationId, startTime, get_cpu_time(class_id), class_id, invocationId, class_id))
    return wl, init_v


def get_cpu_time(cid):
    d = read_cpuT()
    return int(0.69*d[cid]['AverageRunning']) # execution time

def func_class_id(name):
    app, l = name[:-1], int(name[-1])
    if app in ["graphBfs", "graphMst", "graphPagerank", "featureExtractor"]:
        return 1
    if name == "floatOperation":
        return 2
    else:
        if l == 1:
            return 1
        elif l <= 3:
            return 2
        elif l <= 4:
            return 3
        else:
            return 4