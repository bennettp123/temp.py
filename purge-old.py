#!/usr/bin/env python

import os
import sys
import glob
import time
import sqlite3
 
def purge():
    dbname='data/temperatures.db'
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    curs.execute("DELETE FROM temperature WHERE temperature<strftime('%s','now','-1 year');")
    conn.commit()
    conn.close()

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

    purge()
    os.remove(pidfile_str)

