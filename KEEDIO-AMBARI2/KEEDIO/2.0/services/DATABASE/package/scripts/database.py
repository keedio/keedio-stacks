#!/usr/bin/env python
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
import os
import time
from resource_management import *
from subprocess import *
from utils import check_rc
def database(action=None):
  
  if action == 'start' or action == 'stop' or action == 'status':
    cmd=Popen(['service','mariadb',action],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info('Mariadb action: %s.\nSTDOUT=%s\nSTDERR=%s' % (action,out,err))
    if action == 'start' or action == 'status':
      check_rc(cmd.returncode,stdout=out,stderr=err)
   
  if action == 'install' :
    import params
    Package('mariadb-server')
    Package('pexpect')
    Package('MySQL-python')
    import pexpect 
    import MySQLdb
    cmd=Popen(['service','mariadb','start'],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info("Starting MariaDB")
    Logger.info(out)
    Logger.info(err)
    
    Logger.info("Starting mysql secure installation")
    child = pexpect.spawn ('/bin/mysql_secure_installation')
    child.logfile = open("/tmp/mylog", "w")
    Logger.info("Enter current password for root (enter for none):")
    child.expect('.*current.*')
    Logger.info("except: sending current password")
    child.send('\r')
    child.expect('.*Set root password?.*')
    child.send('y\r')
    Logger.info("except: setting new password")
    child.expect('.*New password:.*')
    child.send(params.password+'\r')
    child.expect('.*Re-enter new password:.*')
    child.send(params.password+'\r')
    Logger.info("except: removing security risks")
    child.expect('.*Remove anonymous users?.*')
    child.send('y\r')
    child.expect('.*Disallow root login remotely?.*')
    child.send('y\r')
    child.expect('.*Remove test database and access to it?.*')
    child.send('y\r')
    child.expect('.*Reload privilege tables now?.*')
    child.send('y\r')
    db = MySQLdb.connect("localhost",params.username,params.password)
    cursor = db.cursor()
    Logger.info("CREATE DATABASE "+params.hue_db_name+";")
    cursor.execute("CREATE DATABASE "+params.hue_db_name+";")
#    Logger.info("CREATE USER"+params.hue_db_username+" IDENTIFIED BY '"+params.hue_db_password+"';") 
#    cursor.execute("CREATE USER"+params.hue_db_username+" IDENTIFIED BY '"+params.hue_db_password+"';")
    Logger.info("GRANT ALL ON "+params.hue_db_name+".* to '"+params.hue_db_username+"'@'localhost' IDENTIFIED BY '"+params.hue_db_password+"';")
    cursor.execute("GRANT ALL ON "+params.hue_db_name+".* to '"+params.hue_db_username+"'@'localhost' IDENTIFIED BY '"+params.hue_db_password+"';")
    Logger.info("GRANT ALL ON "+params.hue_db_name+".* to '"+params.hue_db_username+"'@'"+str(params.hue_server_host[0])+"' IDENTIFIED BY '"+params.hue_db_password+"';")
    cursor.execute("GRANT ALL ON "+params.hue_db_name+".* to '"+params.hue_db_username+"'@'"+str(params.hue_server_host[0])+"' IDENTIFIED BY '"+params.hue_db_password+"';")
    cursor.execute("FLUSH PRIVILEGES;")
    
   
