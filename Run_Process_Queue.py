#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on April, 2026 

@author: Humberto Vergara
"""

#from sys import argv
import queue as qu
from threading import Thread
import os
import subprocess as sp
from datetime import datetime
import glob

def worker():
    while True:
        #Obtain date 
        case_date = qu.get()                

        case_date_dt = datetime.strptime(case_date, "%Y-%m-%d %H:%M")
        case_date_stamp = case_date_dt.strftime("%Y%m%d%H%M")
        
        print("python runWorkFlow.py " + case_date)
        sp.call("python runWorkFlow.py '" + case_date + "' > " + case_date_stamp + "_run.log", shell=True)

        #Complete worker's task
        qu.task_done()

#Initiate Queue and Workers
qu = qu.Queue()
numworkers = 5
for i in range(numworkers):
    t = Thread(target=worker)
    t.daemon = True
    t.start()

#Iterate over list of control files
dates_table = ["2019-05-27 00:00", "2019-06-22 00:00", "2020-07-20 00:00", "2021-10-01 00:00", "2023-03-15 12:00"]
for package in dates_table:
    #Pass string array of dates
    qu.put(package)

#block until all tasks are done
qu.join()
