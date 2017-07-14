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

    Logger.info("Configuring datadir")
    Directory(params.datadir,
            create_parents=True,
            owner='mysql',
            group='mysql')
    File('/etc/my.cnf.d/server.cnf',
       owner='mysql',
       group='mysql',
       mode=0644,
       content=Template("server.cnf.j2")
     )
    cmd=Popen(['service','mariadb','restart'],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info("Starting MariaDB")
    Logger.info(out)
    Logger.info(err)
    #Access denied for user 
    Logger.info("Starting mysql secure installation")
    child = pexpect.spawn ('/bin/mysql_secure_installation')
    child.logfile = open("/tmp/mylog", "w")
    
    Logger.info("Enter current password for root (enter for none):")
    child.expect('.*current.*')
    Logger.info("except: sending current password")
    child.send('\r')
    i=child.expect(['.*Set root password?.*',pexpect.TIMEOUT],timeout=2)
    if i==0:
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
    if i==1:
	    Logger.warning("Cannot set mysql security: wrong password")
    try:
	    db = MySQLdb.connect("localhost",params.username,params.password)
	    cursor = db.cursor()
    except:
           raise Fail("Cannot connect to Maria DB")


    # Hue DB configuration
    if params.has_hue: 
	    Logger.info("CREATE DATABASE "+params.hue_db_name+";")
	    try: 
		 cursor.execute("CREATE DATABASE "+params.hue_db_name+";")
	    except:
		 Logger.warning("Cannot create Hue Database, probably already created")

	    Logger.info("GRANT ALL ON "+params.hue_db_name+".* to '"+params.hue_db_username+"'@'localhost' IDENTIFIED BY '"+params.hue_db_password+"';")
	    try:
		  cursor.execute("GRANT ALL ON "+params.hue_db_name+".* to '"+params.hue_db_username+"'@'localhost' IDENTIFIED BY '"+params.hue_db_password+"';")
	    except:
		 Logger.warning("Cannot create Hue localhost db user")

	    Logger.info("GRANT ALL ON "+params.hue_db_name+".* to '"+params.hue_db_username+"'@'"+str(params.hue_server_host[0])+"' IDENTIFIED BY '"+params.hue_db_password+"';")
	    try:
		    cursor.execute("GRANT ALL ON "+params.hue_db_name+".* to '"+params.hue_db_username+"'@'"+str(params.hue_server_host[0])+"' IDENTIFIED BY '"+params.hue_db_password+"';")
	    except:
		 Logger.warning("Cannot create Hue specific host db user")
	  
	    cursor.execute("FLUSH PRIVILEGES;")
    
    # Oozie DB configuration
    if params.has_oozie: 
	    Logger.info("CREATE DATABASE "+params.oozie_db_schema_name+";")
            try:
	    	cursor.execute("CREATE DATABASE "+params.oozie_db_schema_name+";")
            except: 
                Logger.warning("Cannot create Oozie db, probably already created")
	    Logger.info("GRANT ALL ON "+params.oozie_db_schema_name+".* to '"+params.oozie_db_user+"'@'localhost' IDENTIFIED BY '"+params.oozie_db_pass+"';")
            try:
	    	cursor.execute("GRANT ALL ON "+params.oozie_db_schema_name+".* to '"+params.oozie_db_user+"'@'localhost' IDENTIFIED BY '"+params.oozie_db_pass+"';")
            except: 
                Logger.warning("Oozie db localhost permission cannot be set")
	    Logger.info("GRANT ALL ON "+params.oozie_db_schema_name+".* to '"+params.oozie_db_user+"'@'"+str(params.oozie_server_host[0])+"' IDENTIFIED BY '"+params.oozie_db_pass+"';")
            try:
	    	cursor.execute("GRANT ALL ON "+params.oozie_db_schema_name+".* to '"+params.oozie_db_user+"'@'"+str(params.oozie_server_host[0])+"' IDENTIFIED BY '"+params.oozie_db_pass+"';")
            except: 
                Logger.warning("Oozie db host permission cannot be set")
             
	    cursor.execute("FLUSH PRIVILEGES;")

    # Hive DB configuration
    if params.has_hive: 
	    Logger.info("CREATE DATABASE "+params.hive_jdbc_db+";")
            try:
	    	cursor.execute("CREATE DATABASE "+params.hive_jdbc_db+";")
            except: 
                Logger.warning("Cannot create Hive db, probably already created")
	    Logger.info("GRANT ALL ON "+params.hive_jdbc_db+".* to '"+params.hive_db_user+"'@'localhost' IDENTIFIED BY '"+params.hive_db_pass+"';")
            try:
	    	cursor.execute("GRANT ALL ON "+params.hive_jdbc_db+".* to '"+params.hive_db_user+"'@'localhost' IDENTIFIED BY '"+params.hive_db_pass+"';")
            except: 
                Logger.warning("Hive db localhost permission cannot be set")
	    Logger.info("GRANT ALL ON "+params.hive_jdbc_db+".* to '"+params.hive_db_user+"'@'"+str(params.hive_meta_host[0])+"' IDENTIFIED BY '"+params.hive_db_pass+"';")
            try:
	    	cursor.execute("GRANT ALL ON "+params.hive_jdbc_db+".* to '"+params.hive_db_user+"'@'"+str(params.hive_meta_host[0])+"' IDENTIFIED BY '"+params.hive_db_pass+"';")
            except: 
                Logger.warning("Hive db host permission cannot be set")
             
	    cursor.execute("FLUSH PRIVILEGES;")
   
  elif action == 'post' :
    import params
    import MySQLdb
    try:
	    db = MySQLdb.connect("localhost",params.username,params.password)
	    cursor = db.cursor()
    except:
           raise Fail("Cannot connect to Maria DB")
    # Hue DB configuration
    if params.has_hue: 
	    Logger.info("CREATE DATABASE "+params.hue_db_name+";")
	    try: 
		 cursor.execute("CREATE DATABASE "+params.hue_db_name+";")
	    except:
		 Logger.warning("Cannot create Hue Database, probably already created")

	    Logger.info("GRANT ALL ON "+params.hue_db_name+".* to '"+params.hue_db_username+"'@'localhost' IDENTIFIED BY '"+params.hue_db_password+"';")
	    try:
		  cursor.execute("GRANT ALL ON "+params.hue_db_name+".* to '"+params.hue_db_username+"'@'localhost' IDENTIFIED BY '"+params.hue_db_password+"';")
	    except:
		 Logger.warning("Cannot create Hue localhost db user")

	    Logger.info("GRANT ALL ON "+params.hue_db_name+".* to '"+params.hue_db_username+"'@'"+str(params.hue_server_host[0])+"' IDENTIFIED BY '"+params.hue_db_password+"';")
	    try:
		    cursor.execute("GRANT ALL ON "+params.hue_db_name+".* to '"+params.hue_db_username+"'@'"+str(params.hue_server_host[0])+"' IDENTIFIED BY '"+params.hue_db_password+"';")
	    except:
		 Logger.warning("Cannot create Hue specific host db user")
	  
	    cursor.execute("FLUSH PRIVILEGES;")
    
    # Oozie DB configuration
    if params.has_oozie: 
	    Logger.info("CREATE DATABASE "+params.oozie_db_schema_name+";")
            try:
	    	cursor.execute("CREATE DATABASE "+params.oozie_db_schema_name+";")
            except: 
                Logger.warning("Cannot create Oozie db, probably already created")
	    Logger.info("GRANT ALL ON "+params.oozie_db_schema_name+".* to '"+params.oozie_db_user+"'@'localhost' IDENTIFIED BY '"+params.oozie_db_pass+"';")
            try:
	    	cursor.execute("GRANT ALL ON "+params.oozie_db_schema_name+".* to '"+params.oozie_db_user+"'@'localhost' IDENTIFIED BY '"+params.oozie_db_pass+"';")
            except: 
                Logger.warning("Oozie db localhost permission cannot be set")
	    Logger.info("GRANT ALL ON "+params.oozie_db_schema_name+".* to '"+params.oozie_db_user+"'@'"+str(params.oozie_server_host[0])+"' IDENTIFIED BY '"+params.oozie_db_pass+"';")
            try:
	    	cursor.execute("GRANT ALL ON "+params.oozie_db_schema_name+".* to '"+params.oozie_db_user+"'@'"+str(params.oozie_server_host[0])+"' IDENTIFIED BY '"+params.oozie_db_pass+"';")
            except: 
                Logger.warning("Oozie db host permission cannot be set")
             
	    cursor.execute("FLUSH PRIVILEGES;")
    # Hive DB configuration
    if params.has_hive: 
	    Logger.info("CREATE DATABASE "+params.hive_jdbc_db+";")
            try:
	    	cursor.execute("CREATE DATABASE "+params.hive_jdbc_db+";")
            except: 
                Logger.warning("Cannot create Hive db, probably already created")
	    Logger.info("GRANT ALL ON "+params.hive_jdbc_db+".* to '"+params.hive_db_user+"'@'localhost' IDENTIFIED BY '"+params.hive_db_pass+"';")
            try:
	    	cursor.execute("GRANT ALL ON "+params.hive_jdbc_db+".* to '"+params.hive_db_user+"'@'localhost' IDENTIFIED BY '"+params.hive_db_pass+"';")
            except: 
                Logger.warning("Hive db localhost permission cannot be set")
	    Logger.info("GRANT ALL ON "+params.hive_jdbc_db+".* to '"+params.hive_db_user+"'@'"+str(params.hive_meta_host[0])+"' IDENTIFIED BY '"+params.hive_db_pass+"';")
            try:
	    	cursor.execute("GRANT ALL ON "+params.hive_jdbc_db+".* to '"+params.hive_db_user+"'@'"+str(params.hive_meta_host[0])+"' IDENTIFIED BY '"+params.hive_db_pass+"';")
            except: 
                Logger.warning("Hive db host permission cannot be set")
             
	    cursor.execute("FLUSH PRIVILEGES;")
   

