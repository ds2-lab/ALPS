#!/bin/bash
schedtool -N -a 0xfff000000000 -e go run run.go > ~/artifact_results/$1
