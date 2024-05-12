# SAILS: A Self Adaptive Learned OS Scheduler for Serverless-Functions
Welcome to ALPS scheduler project. Our innovative kernel scheduler is designed to enhance the performance of Function-as-a-Service (FaaS) workloads, which are known for their ephermeral, highly concurrent, and bursty nature. Existing OS schedulers, such as Linux Completely Fair Scheduler (CFS), often fail to meet the unique demands of serverless functions, particularly those with short execution time. ALPS addresses this challenge by approximating the principles of the Shortest Remaining Process Time (SRPT) with the robust framework on CFS, delivering a dynamic, application-aware OS scheduling solution.

## Getting Started Instructions

### Operating System required:

We have implemented ALPS based on Linux kernel version 5.18-rc5. You must compile and run the *ALPS* on the the [kernel](https://github.com/fishercht1995/linux.git). We recommend build the kernel based on Ubuntu 22.04 LTS.

### Software Required

The exact software used to build *ALPS* as follows:

- gcc 
    - version: 11.4
- go
    - version: 1.21.4
- bpftool
    - version: 5.14.0
-schedtool
    - version 1.3.0

In addition, We modify and provide exact softwares binaries to run FaaS service. 
 
- Docker
    - Docker client
        - version: 20.10.25
    - dockerd
        - version: 20.10.25
    - runc
        - version: 1.1.10
    -  containerd:
        - version 1.6.24
- OpenLambda:
    - commmit hash: 92fbdfe
   
### Step-by-Step Installation

## Detailed Instructions
