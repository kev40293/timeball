#!/usr/bin/python
#      Copyright (C) 2013  Kevin Brandstatter <icarusthecow@gmail.com>
#
#      This program is free software; you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation; either version 2 of the License, or
#      (at your option) any later version.

from configparser import backup_parser
from version import notice
import sys, os
from subprocess import call
import logging

def run(opts):
   print notice

   backup_file=os.path.realpath(opts['backup-file'])
   logging.debug("Using %s", backup_file)
   backup_dir=os.path.dirname(backup_file)
   name="".join(os.path.basename(backup_file).split('.')[0:-1])

   bparse = backup_parser(backup_file)

   backup_dates = bparse.backups.keys()
   backup_dates.sort()
   for i,b in enumerate(backup_dates):
      print str(i) + ') ' + b
   print ""
   sys.stdout.write("Select backup to delete (default 0): ")
   ui = sys.stdin.readline().rstrip()
   if ui == "":
      choice = 0
   else:
      choice = int(ui)

   sys.stdout.write("Deleting backup with date: " + backup_dates[choice] + " (y/N) ")
   ui = sys.stdin.readline().lower().rstrip('\n')
   if ui != 'y':
      print "Canceling"
      print ui
      return
   else:
      print "Deleting..."
   archives = bparse.backups[backup_dates[choice]]
   snarfile = backup_dir + "/" + name + '-' + backup_dates[choice] + ".snar"

   oldcwd = os.getcwd()
   os.chdir(backup_dir)

   for arc in archives:
      try:
         os.remove(arc)
         logging.info("rm " + arc)
      except OSError:
         logging.warning("Archive missing, perhaps from an failed delete earlier")
   logging.info("rm " + snarfile)
   try:
      os.remove(snarfile)
   except OSError:
      logging.warning("Snar file already deleted")
   print "Writing backup file"
   bparse.remove_backup(backup_dates[choice])
   bparse.write_backup()

   os.chdir(oldcwd)
