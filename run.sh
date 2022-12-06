#!/bin/bash
rm nohup.out
source /home/ootami/envs/mm/bin/activate
nohup python -u smirkcat.py &
echo $! > pid.txt
