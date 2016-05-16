#!/usr/bin/env python

import sqlite3
import os
import sys
import json
import getopt
import ConfigParser


# get data from the database
# if an interval is passed, 
# return a list of records from the database
def get_rows(dbname,interval):

    conn=sqlite3.connect(dbname)
    conn.execute("PRAGMA busy_timeout = 30000")   # 30 s
    curs=conn.cursor()

    if interval == None:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), temperature FROM temperature ORDER BY timestamp ASC")
    else:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), temperature FROM temperature WHERE timestamp>strftime('%%s','now','-%s hours') ORDER BY timestamp ASC" % interval)

    rows=curs.fetchall()

    conn.close()

    return rows



def get_min(dbname,interval):

    conn=sqlite3.connect(dbname)
    conn.execute("PRAGMA busy_timeout = 30000")   # 30 s
    curs=conn.cursor()

    if interval == None:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), min(temperature) FROM temperature")
    else:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), min(temperature) FROM temperature WHERE timestamp>strftime('%%s','now','-%s hours') AND timestamp<=strftime('%%s','now')" % interval)

    rows=curs.fetchall()
    conn.close()
    return rows




def get_max(dbname,interval):

    conn=sqlite3.connect(dbname)
    conn.execute("PRAGMA busy_timeout = 30000")   # 30 s
    curs=conn.cursor()

    if interval == None:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), max(temperature) FROM temperature")
    else:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), max(temperature) FROM temperature WHERE timestamp>strftime('%%s','now','-%s hour') AND timestamp<=strftime('%%s','now')" % interval)

    rows=curs.fetchall()
    conn.close()
    return rows




def get_avg(dbname,interval):

    conn=sqlite3.connect(dbname)
    conn.execute("PRAGMA busy_timeout = 30000")   # 30 s
    curs=conn.cursor()

    if interval == None:
        curs.execute("SELECT timestamp,avg(temperature) FROM temperature")
    else:
        curs.execute("SELECT timestamp,avg(temperature) FROM temperature WHERE timestamp>strftime('%%s','now','-%s hours') AND timestamp<=strftime('%%s','now')" % interval)

    rows=curs.fetchall()
    conn.close()
    return rows


def get_latest(dbname):

    conn=sqlite3.connect(dbname)
    conn.execute("PRAGMA busy_timeout = 30000")   # 30 s
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
def main(argv):

    try:
        opts, args = getopt.getopt(argv, 'hf:', ["help","conf="])
    except getopt.GetoptError:
        print 'get-webdata.py -f <configfile>'
        sys.exit(2)

    conf_file = None

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print 'get-webdata.py -f <configfile>'
            sys.exit()
        elif opt in ("-f", "--conf"):
            conf_file = arg

    config = ConfigParser.RawConfigParser()
    if conf_file:
        config.read(conf_file)

    dbname = config.get('sqlite3', 'db_file')
    print dbname

    interval = str(24*7)

    # print data from the database
    records=get_rows(dbname,interval)
    min = get_min(dbname,interval)
    max = get_max(dbname,interval)
    avg = get_avg(dbname,interval)
    current = get_latest(dbname)
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

    main(sys.argv[1:])

    os.remove(pidfile_str)
