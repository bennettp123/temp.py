#!/usr/bin/env python

import sys
import os
import glob
import time
import sqlite3
 
#os.system('/sbin/modprobe w1-gpio')
#os.system('/sbin/modprobe w1-therm')
 
dbname='/home/bennett/src/temp.py/data/temperatures.db'
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

from threading import Timer

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.daemon = True
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


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
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    curs.execute("INSERT INTO temperature VALUES (strftime('%s','now'), (?))", (temp,))
    conn.commit()
    conn.close()

def log_null_temp(datetime):
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    curs.execute("INSERT INTO temperature VALUES ((?),NULL)", (datetime,))
    conn.commit()
    conn.close()

def insert_missing_nulls():
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    curs.execute("SELECT timestamp, temperature FROM temperature ORDER BY timestamp DESC");
    rows=curs.fetchall()
    prev_row = None
    for row in rows:
        if prev_row is not None:
            if prev_row[0] - row[0] > 60:
                null_timestamps = range(row[0]+60, prev_row[0]-60, 60)
                for timestamp in null_timestamps:
                    log_null_temp(timestamp)
        prev_row = row
    

def read_and_log_temp():
    log_temp(read_temp())

def main(argv):

    try:
        opts, args = getopt.getopt(argv, 'hf:', ["help","conf="])
    except getopt.GetoptError:
        print 'temperature-monitor.py -f <configfile>'
        sys.exit(2)

    conf_file = None

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print 'temperature-monitor.py -f <configfile>'
            sys.exit()
        elif opt in ("-f", "--conf"):
            conf_file = arg

    config = ConfigParser.RawConfigParser()
    if conf_file:
        config.read(conf_file)

    dbname = config.get('sqlite3', 'db_file')

    rt = RepeatedTimer(60, read_and_log_temp)
    time.sleep(60)
    insert_missing_nulls()

    # timer thread is a daemon thread, and exits when
    # the main thread exits -- need to wait indefinitely
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    pidfile_str = os.path.expanduser("~/.temperature-monitor.pid")
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

    main(sys.argv[1:])

    os.remove(pidfile_str)
