#!/usr/bin/env python

import os
import glob
import time
import sqlite3
 
def purge():
    dbname='data/temperatures.db'
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    curs.execute("DELETE FROM temperature WHERE temperature<datetime('now','-1 year');")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    if os.access(os.path.expanduser("~/.temperature-monitor-purge-old.pid"), os.F_OK):
        pidfile = open(os.path.expanduser("~/.temperature-monitor-purge-old.pid"), "r")
        pidfile.seek(0)
        old_pd = pidfile.readline()
       	if os.path.exists("/proc/%s" % old_pd):
            sys.exit(0)
	else:
            os.remove(os.path.expanduser("~/.temperature-monitor-purge-old.pid"))

    pidfile = open(os.path.expanduser("~/.temperature-monitor-purge-old.pid"), "w")
    pidfile.write("%s" % os.getpid())
    pidfile.close

    purge()

