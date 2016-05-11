#!/usr/bin/env python

import os
import glob
import time
import sqlite3
 
#os.system('/sbin/modprobe w1-gpio')
#os.system('/sbin/modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c#, temp_f
	
def log_temp(temp):
    dbname='data/temperatures.db'
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    curs.execute("INSERT INTO temperature VALUES (datetime('now'), (?))", (temp,))
    conn.commit()
    conn.close()

if __name__ = "__main__":
    if os.access(os.path.expanduser("~/.temperature-monitor.pid"), os.F_OK):
        pidfile = open(os.path.expanduser("~/.temperature-monitor.pid""), "r")
        pidfile.seek(0)
        old_pd = pidfile.readline()
       	if os.path.exists("/proc/%s" % old_pd):
            sys.exit(0)
	else:
            os.remove(os.path.expanduser("~/.temperature-monitor.pid""))

    pidfile = open(os.path.expanduser("~/.temperature-monitor.pid""), "w")
    pidfile.write("%s" % os.getpid())
    pidfile.close

    while True:
        log_temp(read_temp())
        time.sleep(60)

