#!/bin/bash
source /home/ootami/catenv/bin/activate
nohup python smirkcat.py &
echo $! > pid.txt
