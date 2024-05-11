import analyze
import struct

def generateOutput(slog, outPath):
    # write data
    analyze.writeLogs(outPath, slog.durations, slog.contextS, slog.timeSlice, slog.jobSummary)


def checkContextSwitch(policy, j, sched, timeSlice):
    if policy in ["fifo", "rr", "sfs"]:
        return (j.executedTime() >= timeSlice and not sched.is_empty()) or j.isEnd()
    elif policy in ["seal", "srtf"]:
        return (sched.checkContextSwitch(j, timeSlice) and not sched.is_empty()) or j.isEnd()
    else:
        return False
