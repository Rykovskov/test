#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import datetime
import sys
from pathlib import Path
import paramiko
import smtplib
import logging
import traceback


#Servers
list_Servers = [
                {'NameServer':'Server1',
                 'IP': "192.168.21.48", 
                 'user': 'max', 
                 'pass': '11111', 
                 'App':[
                        {'Name':'nginx', 'LogDir':'/var/log/nginx', 'StorageTime':'2', 'RemoteTime':'31',  'WorkDir':'/home/max/test'},
                        {'Name':'app',   'LogDir':'/var/log/app',   'StorageTime':'2', 'RemoteTime':'31',  'WorkDir':'/home/max/test'}
                       ],
                },
                {'NameServer':'Server2',
                 'IP': "192.168.21.47", 
                 'user': 'max', 
                 'pass': '111111', 
                 'App':[
                         {'Name':'nginx', 'LogDir':'/var/log/nginx', 'StorageTime':'186', 'RemoteTime':'31', 'WorkDir':'/home/max/test'},
                         {'Name':'App',   'LogDir':'/var/log/app',   'StorageTime':'365', 'RemoteTime':'31', 'WorkDir':'/home/max/test'}
                       ]
                }
               ]


#Info
logging.basicConfig(filename="Backup.log", level=logging.INFO)
min_free_space = 100 # In Mbyte

#Check free space on buckup server
def check_space(dir_path):
    st = os.statvfs(dir_path)
    free_space = int(st.f_bsize * st.f_bavail / 1024 / 1024)
    if free_space<min_free_space:
       logging.error("Check space on the backup store device !!!!")
       return 0
    logging.info("Free space = " + str(free_space))
    return 1


#Get file list from server srv on date dt from directory dir_name 
def get_list_files_from_server(dt, dir_name, srv):
   search_pattern = dt.strftime("%Y") + "-" + dt.strftime("%m") + "-" + dt.strftime("%d")
   try:
      client = paramiko.SSHClient()
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      client.connect(srv['IP'],  username = srv['user'], password = srv['pass'])
      cmd = "ls " + dir_name + " | grep " + search_pattern
      stdin, stdout, stderr = client.exec_command(cmd)
      sp = stdout.read().splitlines()
      result = []
      for n in sp:
          result.append(n.decode("utf-8"))
      client.close()
      return result
   except:
      logging.error("Connection error to server "+srv['IP'])


def get_old_files_from_server(dir_name, dayes, srv):
   try:
      client = paramiko.SSHClient()
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      client.connect(srv['IP'],  username = srv['user'], password = srv['pass'])
      cmd = 'find ' + dir_name + ' -type f -mtime -' + dayes + " -printf '%f\n'"
      stdin, stdout, stderr = client.exec_command(cmd)
      sp = stdout.read().splitlines()
      result = []
      for n in sp:
          result.append(n.decode("utf-8"))
      client.close()
      return result
   except:
      logging.error("Connection error to server "+srv['IP'])


def get_old_files_from_local_server(local_dir, dayes, srv):
   try:
      cmd = 'find ' + local_dir + ' -type f -mtime -' + dayes + " -printf '%f\n'"
      st = os.popen(cmd).read().split()
      return st
   except:
      logging.error("Error get old name files from local server for " + local_dir)


def check_files_on_backup_server(list_files, local_dir, srv):
   try:
      result = []
      for f in list_files:
          patch_to_file = os.path.join(local_dir, f)
          if os.path.exists(patch_to_file):
             result.append(f)
      return result
   except:
         logging.error("Error check file " + f + " from server  "+ srv['IP'])


#Functions for download files from remote server
def get_files(list_files, dir_name, local_dir, srv):
   try:
      client = paramiko.SSHClient()
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      client.connect(srv['IP'],  username = srv['user'], password = srv['pass'])
      ftp=client.open_sftp()
      ftp.chdir(dir_name)
      for f in list_files:
          if not check_space(local_dir):
             logging.error("Error befor get file " + f + " from server " + srv['IP'] + ". No space on storage!!! ")
             sys.exit()
          patch_to_file = os.path.join(local_dir, f)
          ftp.get(f, patch_to_file)
          if not os.path.exists(patch_to_file):
             logging.error("Error get file " + f + " from server  "+ srv['IP'])
      return 1
   except:
      logging.error("Error get file from server  " + srv['IP'])
      return 0


#Functions for remove files from remote server
def remove_files(list_files, dir_name, srv):
   try:
      client = paramiko.SSHClient()
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      client.connect(srv['IP'],  username = srv['user'], password = srv['pass'])
      channel = сlient.get_transport().open_session()
      channel.get_pty()
      channel.settimeout(5)
      for f in list_files:
          patch_to_file = os.path.join(dir_name, f)
          cmd = 'sudo rm -f '+ patch_to_file
          channel.exec_command(cmd)
          channel.send(srv['pass'] +'\n')
          res = channel.recv(1024)
      return 1
   except:
      logging.error("Error delete file from remote server  " + srv['IP'])
      return 0


#Functions for remove files from local server
def local_remove_files(list_files, local_dir, srv):
   try:
       for f in list_files:
          patch_to_file = os.path.join(local_dir, f)
          os.remove(patch_to_file)
       return 1
   except:
       logging.error("Error delete file from local server  " + srv['IP'])
       return 0


# Functions for remove name of files from list files
def remove_exsist_file_name(list_files, name_dir): #listfiles - List files from remote server name_dir  - Directory where wil be locations this files 
    #Remove name files where exist in local storage
    result = []
    for f in list_files:
        fullpath = os.path.join(name_dir , f)
        if not os.path.exists(fullpath):
           result.add(f)
    return result


#Start code
yesterday_dt = datetime.datetime.now() - datetime.timedelta(days=1)
for server in list_Servers:
    for app in server['App']:
        path_app_log = os.path.join(app['WorkDir'] , app['Name'])
        
        #remove files from local server
        #Get old files from local servers
        oldfiles = get_old_files_from_local_server(path_app_log, app['StorageTime'], server)
        #Remove old files from local server
        local_remove_files(oldfiles, path_app_log, srv)

        #Remove files from remote server
        #Get old files from servers
        files = get_old_files_from_server(app['LogDir'], app['RemoteTime'], server)
        #check exsist files
        exist_files = check_files_on_backup_server(files, path_app_log, server)
        #Remove files from servers
        remove_files(exist_files, app['LogDir'], server)
        
        #Copy ney files from remote server
        if not check_space(path_app_log):
           sys.exit()
        files = get_list_files_from_server(yesterday_dt, app['LogDir'], server)
        if len(files)>0:
           get_files_list_name = remove_exsist_file_name(files, path_app_log)
        else:
           continue
        if len(get_files_list_name)==0:
           logging.info("No candidate files to backups on " + server['IP'])
        #Get files from server
        get_files(get_files_list_name, app['LogDir'], path_app_log, server) 
        if not check_space(path_app_log):
           sys.exit()
sys.exit()



