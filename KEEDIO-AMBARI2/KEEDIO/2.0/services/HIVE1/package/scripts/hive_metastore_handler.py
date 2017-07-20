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

import sys
from resource_management import *
from subprocess import *

from hive import hive
import utils

         
class HiveServerHandler(Script):
  def install(self, env):
    import params
    #self.install_packages(env)
    Package("hive-metastore")
    Package("hive")
    self.initialize_db(env)
    
  def configure(self, env):
    import params
    env.set_params(params)
    hive(action='config',service='hive-metastore')
    self.initialize_db(env)
    
  def start(self, env):
    self.configure(env)
    hive(action='start',service='hive-metastore')
    
  def stop(self, env):
    hive(action='stop',service='hive-metastore')

  def status(self, env):
    hive(action='status',service='hive-metastore')

  def initialize_db(self,env):
    import params
    Logger.info("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    try:
      if params.hive_db_driver == "com.mysql.jdbc.Driver":
        Package('mysql-connector-java')
        Package('mariadb')
        Logger.info('Using Mysql, creating symlink /usr/lib/hive/lib/mysql-jdbc-driver.jar')
#        cmd=Popen(['ln','-s','/usr/share/java/postgresql-jdbc.jar','/usr/lib/hive/lib/postgresql.jar'])
        extract_cmd=[ 'ln', '-s','/usr/share/java/mysql-connector-java.jar','/usr/lib/hive/lib/mysql-jdbc-driver.jar']
        cmd=Popen(extract_cmd)
        out,err=cmd.communicate()
        Logger.info(str(out))
        Logger.info(str(err))
        Logger.info('Using MySQL, importing schema')
        cmd=Popen(['mysql','-h',params.hive_db_server,'-b',params.jdbc_db,'-u',params.jdbc_username,'--password='+params.jdbc_password,'-e','source /usr/lib/hive/scripts/metastore/upgrade/mysql/hive-schema-1.2.0.mysql.sql;'],stdout=PIPE,stderr=PIPE)
        out,err=cmd.communicate()
        Logger.info(str(out))
        Logger.info(str(err))

      elif params.hive_db_driver == "org.postgresql.Driver":
        Logger.info('Using Postgres, creating symlink /usr/lib/hive/lib/postgres-jdbc-driver.jar')
#        cmd=Popen(['ln','-s','/usr/share/java/postgresql-jdbc.jar','/usr/lib/hive/lib/postgresql.jar'])
        extract_cmd=[ 'ln', '-s','/usr/lib/ambari-agent/postgres-jdbc-driver.jar','/usr/lib/hive/lib/postgres-jdbc-driver.jar']
        cmd=Popen(extract_cmd)
        out,err=cmd.communicate()
        Logger.info(str(out))
        Logger.info(str(err))
        Logger.info('Importing schema')
        cmd=Popen(['psql','-h',params.hive_db_server,'-U',params.jdbc_username,'-d',params.jdbc_db,'-f','/usr/lib/hive/scripts/metastore/upgrade/postgres/hive-schema-0.14.0.postgres.sql'],stdout=PIPE,stderr=PIPE)
        out,err=cmd.communicate()
        Logger.info(str(out))
        Logger.info(str(err))

      elif params.hive_db_driver == "oracle.jdbc.driver.OracleDriver":
        Logger.info('Using Oracle DB, creating symlink /usr/lib/hive/lib/oracle-jdbc-driver.jar')
        extract_cmd=[ 'ln', '-s','/usr/lib/ambari-agent/oracle-jdbc-driver.jar','/usr/lib/hive/lib/oracle-jdbc-driver.jar']
        cmd=Popen(extract_cmd)
        out,err=cmd.communicate()
        Logger.info("Creating jdbc symbolic link in /usr/lib/hive/lib/")
        Logger.info(str(out))
        Logger.info(str(err))
        Logger.info("Warning:####################################################")
        Logger.info("Warning:You must preload Hive schema into Oracle DB manually")
        Logger.info("Warning:####################################################")

    
    except: 
        Logger.info("Cannot create Hive schema in the backend database, make sure you clean the database before restarting the installation!")
        exit()
     
if __name__ == "__main__":
  HiveServerHandler().execute()
