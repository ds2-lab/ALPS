#!/bin/bash

docker rm -f $(docker ps -aq)
for i in 5001 5002 5005 5006 5008 5009 5010 5011 5014 5015 5016 5017 5018 5020 5021
do
        kill -9 $(lsof -t -i:$i) &
done

for i in 1 2 5 6 8 9 10 11 14 15 16 17 18 20 21
do
        echo $i
        rm worker$i/worker/worker.pid &
done
~