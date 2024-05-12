#!/bin/bash
systemctl stop docker 
nohup dockerd > /dev/null 2>&1 &