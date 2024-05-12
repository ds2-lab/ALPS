#!/bin/bash

for i in 1 2 5 6 8 9 10 11 14 15 16 17 18 20 21
do
	sleep 0.1
	./ol worker --path=worker$i &
done