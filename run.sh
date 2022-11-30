#!/bin/bash
source /home/ootami/envs/mm/bin/activate
nohup python smirkcat.py &
echo $! > pid.txt
