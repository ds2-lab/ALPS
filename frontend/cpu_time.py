from bcc import BPF
import threading
import time
import os
import pickle
CPUT_map = "/mydata/CPUT_map.pkl"

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

TRACEPOINT_PROBE(sched, sched_process_exit) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;  // 获取当前 PID
    struct task_struct *task = (struct task_struct *)bpf_get_current_task();
    u64 sruntime = task->se.sum_exec_runtime; // 获取累计的 CPU 运行时间

    char comm[TASK_COMM_LEN];
    bpf_get_current_comm(&comm, sizeof(comm));
    bpf_trace_printk("PID: %d Command: %s sum_exec_runtime: %llu\\n", pid, comm, sruntime);
    return 0;
}
"""

def trace_print(stop_event, exp):
    f = open(exp, "w")
    b = BPF(text=bpf_text)
    while not stop_event.is_set():
        try:
            (task, pid, cpu, flags, ts, msg) = b.trace_fields()
            if "python" in msg.decode():
                f.write("%-6d %s\n" % (pid, msg.decode()))
        except ValueError:
            continue

def read_cpuT():
    with open(CPUT_map, "rb") as f:
        data = pickle.load(f)
    return data

def update_cpuT(expT, expR, expC = "/mydata/config"):
    if not os.path.exists(CPUT_map):
        init_data = {0: {"Amount": 1, "TotalRunning": 0, "AverageRunning": 0}}
        with open(CPUT_map, "wb") as f:
            pickle.dump(init_data, f)
    with open(CPUT_map, "rb") as f:
        data = pickle.load(f)
    
    # pid -> cpu time
    dataT = {}
    with open(expT, "r") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip().split()
        dataT[int(line[2])] = int(line[-1])//1000000
    
    # invocation id -> function id
    dataC = {}
    with open(expC, "r") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip().split()
        dataC[int(line[0])] = int(line[-1]) - 5000
    
    # function id ->  cpu time
    with open(expR, "r") as f:
        lines = f.readlines()
    for line in lines:
        if "Body" not in line:
            line = line.strip().split()
            inv_id, pid, = int(line[0]), int(line[-3])
            if pid in dataT and inv_id in dataC and dataT[pid] > 1:
                cpu_time = dataT[pid]
                function_id = dataC[inv_id]
                if function_id not in data:
                    data[function_id] = {"Amount": 0, "TotalRunning": 0, "AverageRunning": 0}
                data[function_id]["Amount"] += 1
                data[function_id]["TotalRunning"] += cpu_time
    
    try:
        for func_id in data:
            data[func_id]["AverageRunning"] = data[func_id]["TotalRunning"]/(data[func_id]["Amount"])
    except:
        print(data)
    with open(CPUT_map, "wb") as f:
        data = pickle.dump(data, f)