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
def get_rows(curs,interval):

    if interval == None:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), temperature FROM temperature ORDER BY timestamp ASC")
    else:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), temperature FROM temperature WHERE timestamp>strftime('%%s','now','-%s hours') ORDER BY timestamp ASC" % interval)

    rows=curs.fetchall()
    return rows



def get_min(curs,interval):

    if interval == None:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), min(temperature) FROM temperature")
    else:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), min(temperature) FROM temperature WHERE timestamp>strftime('%%s','now','-%s hours') AND timestamp<=strftime('%%s','now')" % interval)

    rows=curs.fetchall()
    return rows




def get_max(curs,interval):

    if interval == None:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), max(temperature) FROM temperature")
    else:
        curs.execute("SELECT datetime(timestamp,'unixepoch', 'localtime'), max(temperature) FROM temperature WHERE timestamp>strftime('%%s','now','-%s hour') AND timestamp<=strftime('%%s','now')" % interval)

    rows=curs.fetchall()
    return rows




def get_avg(curs,interval):

    if interval == None:
        curs.execute("SELECT timestamp,avg(temperature) FROM temperature")
    else:
        curs.execute("SELECT timestamp,avg(temperature) FROM temperature WHERE timestamp>strftime('%%s','now','-%s hours') AND timestamp<=strftime('%%s','now')" % interval)

    rows=curs.fetchall()
    return rows


def get_latest(curs):

    curs.execute("SELECT * FROM temperature ORDER BY timestamp DESC LIMIT 1;")
    rows=curs.fetchall()
    return rows
    


def print_webdata(rows, min, recordmin, max, recordmax, average, current):
    d = {}
    d['rows'] = rows
    d['min'] = min
    d['max'] = max
    d['recordmin'] = recordmin
    d['recordmax'] = recordmax
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

    interval = str(24*7*1)

    # print data from the database
    conn=sqlite3.connect(dbname)
    conn.execute("PRAGMA query_only = true;")
    conn.execute("PRAGMA busy_timeout = 30000")   # 30 s
    curs=conn.cursor()
    records=get_rows(curs,interval)
    min_interval = get_min(curs,interval)
    min_alltime = get_min(curs,None)
    max_interval = get_max(curs,interval)
    max_alltime = get_max(curs,None)
    avg = get_avg(curs,interval)
    current = get_latest(curs)
    conn.close()
    print_webdata(records, min_interval, min_alltime, max_interval, max_alltime, avg, current)

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
