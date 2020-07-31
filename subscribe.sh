#!/bin/bash
cd /home/marco/Python/Wetterstation
source venv/bin/activate
nohup python3 subscribe.py > subscribe.log &
