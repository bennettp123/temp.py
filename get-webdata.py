#!/usr/bin/env python

import sqlite3
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
        curs.execute("SELECT timestamp,temperature FROM temperature")
    else:
        curs.execute("SELECT timestamp,temperature FROM temperature WHERE timestamp>datetime('now','-%s hours')" % interval)

    rows=curs.fetchall()

    conn.close()

    return rows



def get_min(interval):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    if interval == None:
        curs.execute("SELECT timestamp,min(temperature) FROM temperature")
    else:
        curs.execute("SELECT timestamp,min(temperature) FROM temperature WHERE timestamp>datetime('now','-%s hour') AND timestamp<=datetime('now')" % interval)

    rows=curs.fetchall()
    conn.close()
    return rows




def get_max(interval):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    if interval == None:
        curs.execute("SELECT timestamp,max(temperature) FROM temperature")
    else:
        curs.execute("SELECT timestamp,max(temperature) FROM temperature WHERE timestamp>datetime('now','-%s hour') AND timestamp<=datetime('now')" % interval)

    rows=curs.fetchall()
    conn.close()
    return rows




def get_avg(interval):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    if interval == None:
        curs.execute("SELECT timestamp,avg(temperature) FROM temperature")
    else:
        curs.execute("SELECT timestamp,avg(temperature) FROM temperature WHERE timestamp>datetime('now','-%s hour') AND timestamp<=datetime('now')" % interval)

    rows=curs.fetchall()
    conn.close()
    return rows




def print_webdata(rows, min, max, average):
    d = {}
    d['rows'] = rows
    d['min'] = min
    d['max'] = max
    d['avg'] = average
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
    print_webdata(records, min, max, avg)

    sys.stdout.flush()

if __name__=="__main__":
    main()
