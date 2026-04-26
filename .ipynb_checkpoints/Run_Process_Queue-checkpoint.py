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
import datetime as dt
import glob

def worker():
    while True:
        #Obtain string array of filenames and folders 
        filename = qu.get()                
	
        print("/hydros/humberva/EF5/EF5/bin/ef5 " + filename)
        sp.call("echo " + filename + " > " + filename + "_run.log", shell=True)

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
ctrl_list = ['run0','run1','run2', 'run3', 'run4']
for ctr_file in ctrl_list:
    #Pass string array of filenames and folders
    qu.put(ctr_file)

#block until all tasks are done
qu.join()
