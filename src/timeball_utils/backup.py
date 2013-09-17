#!/usr/bin/python
#      backup.py : handles the creation of the backups
#      Copyright (C) 2013  Kevin Brandstatter <icarusthecow@gmail.com>
#
#      This program is free software; you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation; either version 2 of the License, or
#      (at your option) any later version.


import sys
import os
import os.path
from subprocess import check_call, CalledProcessError
import datetime
from configparser import backup_parser, config_parser
from shutil import copyfile, move
import logging



class backup:
   def __init__(self, options):
      self.target = os.path.basename(options['target'])
      self.dest = os.path.realpath(options['dest'])
      self.target_dir = os.path.dirname(options['target'])
      if options['name'] == "":
         options['name'] = self.target
      self.name = self.target
      self.exclude_args = self.get_exclude_args(options['exclude'])
      self.backup_type = options['back_type']
      self.init_filenames()

   def init_filenames(self):
      self.bparse = backup_parser('{0}/{1}.backup'.format(self.dest, self.name))
      date = self.get_backup_date()
      self.tar_name = "{0}/{1}-{2}-{3}.tar".format(self.dest, self.name, self.backup_type, date)
      self.snar_name = "{0}/{1}-{2}.snar".format(self.dest, self.name, date)

   def get_exclude_args(self, exclude_options):
      excluded_files = []
      for ex in exclude_options:
         excluded_files.append("--exclude="+ ex)
      return excluded_files

   def get_backup_date(self):
      if self.backup_type == "part":
         if (len(self.bparse.backups.keys()) == 0):
            logging.error("No full backup to base a partial off of")
         else:
            return max(self.bparse.backups.keys())
      else:
         now= datetime.datetime.now()
         return now.strftime("%Y-%m-%dT%H:%M:%S")

   def do_backup(self):
      self.setup_backup()
      self.create_tar()
      archive = self.compress_archive()
      self.record_backup(archive)

   def record_backup(self, archive_file):
      if self.backup_type == "full":
         self.bparse.add_backup(outfile, date=curdate)
      elif self.backup_type == "part":
         self.bparse.add_backup(outfile)

#   def partial(self):
#      if (len(self.bparse.backups.keys()) == 0):
#         logging.error("No full backup to base a partial off of")
#      else:
#         outfile = self.run("part", max(self.bparse.backups.keys()))
#         self.bparse.add_backup(outfile)
#
#   def full(self):
#      outfile = self.run("full", curdate)
#      self.bparse.add_backup(outfile, date=curdate)


   def push_directory(self):
      self.original_directory = os.getcwd()
      if not self.target_dir == "":
         os.chdir(self.target_dir)

   def pop_directory(self):
      os.chdir(self.original_directory)


   def get_tar_options(self):
      # Set the tar command line options
      args=['tar', '-cvf', self.get_tar_name(), '--one-file-system','-g', self.get_snar_name()]
      args.extend(self.exclude_args)
      #level = 0
      #if backtype == "part":
      #   level=len(self.bparse.backups[backupdate])
      #args.append("--level="+str(level))
      args.append(self.target)
      # Cleanup past backups that failed to complete
      return args

   def setup_backup():
      self.push_directory()
      self.cleanup_failed()
      if self.backup_type == "part":
         copyfile(self.snar_name, self.snar_name+".bak")

   def create_tar(self):
      args = self.get_tar_options()
      try:
         check_call(args)
      except CalledProcessError as e:
         logging.error("Backup failed with error code: " + str(e.returncode))
         if (e.returncode > 2): # Ignore errors from tar
            os.remove(self.archive_file)
            if self.backup_type == "part":
               move(self.snar_filename+".bak", self.snar_filename)
            if self.backup_type == "full":
               os.remove(self.snar_filename)
            sys.exit(e.returncode)
         logging.warning("Files that were modified or changed during the backup may be corrupted")
      return self.archive_file

   def compress_archive(self, archive_name):
      try:
         logging.info("Archive finished, compressing with bzip2")
         check_call(['bzip2', archive_name])
         archive_name = archive_name + '.bz2'
         logging.info("Compression complete")
      except CalledProcessError as e:
         logging.error("Compression failed")
      #with open(listfile, 'a') as f:
      #   f.write(os.path.basename(outname) + "\n")
      if self.backup_type == "part":
         os.remove(self.snar_filename+".bak")
      return os.path.basename(self.archive_name)

   def cleanup_failed(self):
      # If backup failed, restore snar from backup
      if os.path.exists(self.snar_name + ".bak"):
         logging.info("Snar backup file found, recovering")
         move(self.snar_name+".bak", self.snar_name)
         # TODO remove the unecessary archives


def run(options):
   backup_type = options['back_type']

   back_ob = backup(options)
   if backup_type == "full":
      back_ob.full()
   elif backup_type == "part":
      back_ob.partial()
   else:
      print "No backup type specified"
      sys.exit(1)
