# ALPS: Adaptive-Learning Priority OS Scheduler for Serverless-Functions
Welcome to ALPS scheduler project. Our innovative kernel scheduler is designed to enhance the performance of Function-as-a-Service (FaaS) workloads, which are known for their ephermeral, highly concurrent, and bursty nature. Existing OS schedulers, such as Linux Completely Fair Scheduler (CFS), often fail to meet the unique demands of serverless functions, particularly those with short execution time. ALPS addresses this challenge by approximating the principles of the Shortest Remaining Process Time (SRPT) with the robust framework on CFS, delivering a dynamic, application-aware OS scheduling solution.

## Getting Started Instructions

<font color=blue>For the artifact review, we recommend that reviewers utilize our dedicated deployment environment, iad-1, which features a bare-metal machine equipped with 56 CPUs and 128 MB of memory. To use this environment and save effort on setup, please contact [Yuqi](jwx3px@virginia). I will assist with setting up the virtual machine and scheduling your access.</font>

### Operating System required:

We have implemented ALPS based on Linux kernel version 5.18-rc5. You must compile and run the *ALPS* on the the [kernel](https://github.com/fishercht1995/linux.git). We recommend build the kernel based on Ubuntu 22.04 LTS. 

### Software Required

The exact software used to build *ALPS* as follows:

- gcc 
    - version: 11.4
- go
    - version: 1.21.10
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

#### gcc installation
```
apt update -y
sudo apt install build-essential
gcc --version 
```

#### go installtion
Download the Go language binary archive
```
wget https://go.dev/dl/go1.21.10.linux-amd64.tar.gz
sudo tar -xvf go1.12.linux-amd64.tar.gz
sudo mv go /usr/local
```
Setup Go environment, including `GOROOT` and `GOPATH`. Add environment variables to the `~/.profile`.
```
export GOROOT=/usr/local/go
mkdir $HOME/project
export GOPATH=$HOME/project
export PATH=$GOPATH/bin:$GOROOT/bin:$PATH
```
Verify installation
```
~$ go version
~$ go version go1.21.10 linux/amd64
```
### bpftool
Clone bpftool repository and build following [installation instruction](https://github.com/libbpf/bpftool/blob/main/README.md)
```
git clone --recurse-submodules https://github.com/libbpf/bpftool.git
```
### schedtool
Install schedtool by apt
```
sudo apt-get update -y
sudo apt-get install -y schedtool
```
### Docker
Clone *ALPS* repository and copy docker binaries to `/usr/sbin`
```
git clone https://github.com/fishercht1995/ALPS.git
cd docker_binaries
cp binary-client/* /usr/bin/
cp binary-daemon/* /usr/bin/
```
OpenLambda

## Detailed Instructions
