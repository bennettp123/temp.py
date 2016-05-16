#!/usr/bin/env python

import os
import sys
import glob
import time
import sqlite3
import getopt
import ConfigParser
 
dbname='/home/bennett/src/temp.py/data/temperatures.db'

def purge():
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    curs.execute("DELETE FROM temperature WHERE temperature<strftime('%s','now','-1 year');")
    conn.commit()
    conn.close()

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'hf:', ["help","conf="])
    except getopt.GetoptError:
        print 'purge-old.py -f <configfile>'
        sys.exit(2)

    conf_file = None

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print 'purge-old.py -f <configfile>'
            sys.exit()
        elif opt in ("-f", "--conf"):
            conf_file = arg

    config = ConfigParser.RawConfigParser()
    if conf_file:
        config.read(conf_file)

    dbname = config.get('sqlite3', 'db_file')

    purge()

if __name__ == "__main__":
    pidfile_str = os.path.expanduser("~/.temperature-monitor-purgeold.pid")
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
