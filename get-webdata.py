#!/usr/bin/env python

import sqlite3
import os
import sys
import json


# global variables
speriod=(15*60)-1
dbname='/home/bennett/src/temp.py/data/temperatures.db'



# get data from the database
# if an interval is passed, 
# return a list of records from the database
def get_rows(interval):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    if interval == None:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), temperature FROM temperature ORDER BY timestamp ASC")
    else:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), temperature FROM temperature WHERE timestamp>strftime('%%s','now','-%s hours') ORDER BY timestamp ASC" % interval)

    rows=curs.fetchall()

    conn.close()

    return rows



def get_min(interval):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    if interval == None:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), min(temperature) FROM temperature")
    else:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), min(temperature) FROM temperature WHERE timestamp>strftime('%%s','now','-%s hours') AND timestamp<=strftime('%%s','now')" % interval)

    rows=curs.fetchall()
    conn.close()
    return rows




def get_max(interval):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    if interval == None:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), max(temperature) FROM temperature")
    else:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), max(temperature) FROM temperature WHERE timestamp>strftime('%%s','now','-%s hour') AND timestamp<=strftime('%%s','now')" % interval)

    rows=curs.fetchall()
    conn.close()
    return rows




def get_avg(interval):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    if interval == None:
        curs.execute("SELECT timestamp,avg(temperature) FROM temperature")
    else:
        curs.execute("SELECT timestamp,avg(temperature) FROM temperature WHERE timestamp>strftime('%%s','now','-%s hours') AND timestamp<=strftime('%%s','now')" % interval)

    rows=curs.fetchall()
    conn.close()
    return rows


def get_latest():

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    curs.execute("SELECT * FROM temperature ORDER BY timestamp DESC LIMIT 1;")
    rows=curs.fetchall()
    conn.close()
    return rows
    


def print_webdata(rows, min, max, average, current):
    d = {}
    d['rows'] = rows
    d['min'] = min
    d['max'] = max
    d['avg'] = average
    d['current'] = current
    print json.dumps(d, ensure_ascii=False)




# check that the option is valid
# and not an SQL injection
def validate_input(option_str):
    # check that the option string represents a number
    if option_str.isalnum():
        # check that the option is within a specific range
        if int(option_str) > 0 and int(option_str) <= 24:
            return option_str
        else:
            return None
    else: 
        return None





# main function
# This is where the program starts 
def main():

    option = str(24*7)

    # print data from the database
    records=get_rows(option)
    min = get_min(option)
    max = get_max(option)
    avg = get_avg(option)
    current = get_latest()
    print_webdata(records, min, max, avg, current)

    sys.stdout.flush()

if __name__=="__main__":
    pidfile_str = os.path.expanduser("~/.temperature-monitor-getwebdata.pid")
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

    main()

    os.remove(pidfile_str)
