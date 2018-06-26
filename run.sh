#!/bin/bash

for i in `seq 1 5`;
do
	python -B onlylearning.py $i &
done
