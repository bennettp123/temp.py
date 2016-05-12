#!/usr/bin/env python

import os
import sys
import json
import glob
import stat
import time
import shutil
import tempfile
 
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
        

if __name__ == "__main__":
    pidfile_str = os.path.expanduser("~/.temperature-monitor-livedata.pid")
    if os.access(pidfile_str, os.F_OK):
        pidfile = open(pidfile_str, "r")
        pidfile.seek(0)
        old_pd = pidfile.readline()
        pidfile.close()
        if os.path.exists("/proc/%s" % old_pd):
            sys.exit(0)
        else:
            os.remove(pidfile_str)

    pidfile = open(pidfile_str, "w+")
    pidfile.write("%s" % os.getpid())
    pidfile.close()

    outfile = '/tmp/latest.json'

    prev_temp = None
    while True:
        temp = round(read_temp(), 1)
        if temp == prev_temp:
            continue
        prev_temp = temp
        (fd, temp_path) = tempfile.mkstemp()
        os.write(fd,json.dumps(temp,ensure_ascii=False))
        os.fchmod(fd,stat.S_IRUSR|stat.S_IWUSR|stat.S_IRGRP|stat.S_IROTH) #644
        os.close(fd)
        shutil.move(temp_path,outfile)
        time.sleep(2)

