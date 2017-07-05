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

from resource_management import *
from subprocess import *
from utils import check_rc, execute_sudo_krb
from functools import partial
def oozie(action=None,is_server=False):
  
  if action == 'install':
    import params
    cmd=Popen(['/usr/sbin/usermod','-a','-G','hadoop','oozie'],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info('Oozie action: %s.\nSTDOUT=%s\nSTDERR=%s' % (action,out,err))


  if action == 'start' or action == 'stop':
    import params
    cmd=Popen(['service','oozie',action],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info('Oozie action: %s.\nSTDOUT=%s\nSTDERR=%s' % (action,out,err))

  if action == 'status':
    cmd=Popen(['service','oozie',action],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    check_rc(cmd.returncode,stdout=out,stderr=err)

  if action == 'config' :
    import params
    import os
    if not os.path.exists('/etc/oozie/conf'):
       conf_cmd=[ 'ls', '-s','/etc/oozie/conf.d','/etc/oozie/conf' ] 
       cmd=Popen(conf_cmd)
       out,err=cmd.communicate() 
       Logger.info("/etc/oozie/conf doesn't exist: creating symlink to conf.d")
       Logger.info(str(out))
       Logger.info(str(err))
      

    File(params.oozie_config_dir + '/oozie-site.xml',
      content=Template('oozie-site.j2'),
      owner=params.oozie_user,
      group=params.oozie_group,
      mode=0644)

    File(params.oozie_config_dir+'/oozie-env.sh',
      content=Template('oozie-env.j2'),
      owner=params.oozie_user,
      group=params.oozie_group,
      mode=0644)

    File(params.oozie_config_dir+'/adminusers.txt',
      content=Template('adminusers.txt.j2'),
      owner=params.oozie_user,
      group=params.oozie_group,
      mode=0644)


    if is_server :
      execute_hdfs = partial(execute_sudo_krb,user=params.hdfs_user,principal=params.hdfs_principal_name,keytab=params.hdfs_user_keytab) 
      execute_oozie = partial(execute_sudo_krb,user=params.smoke_user,principal=params.smoke_user,keytab=params.smoke_user_keytab)

      #File('/usr/lib/oozie/libext/ext-2.2.1.zip',
      # content=StaticFile('ext-2.2.1.zip'))
      ## oozie expect ext-2.2 directory and looks to be hardcoded
      #extract_cmd=[ 'unzip', '/usr/lib/oozie/libext/ext-2.2.1.zip','-d','/usr/lib/oozie/libext/ext-2.2' ]
      #Popen(extract_cmd)

      #extract_cmd=[ 'ln', '-s','/usr/share/java/postgresql-jdbc.jar','/usr/lib/oozie/libext/postgresql-jdbc.jar' ]
      #extract_cmd=[ 'ln', '-s','/usr/share/java/mysql-connector-java.jar','/usr/lib/oozie/libext/mysql-jdbc-driver.jar' ] 
      Logger.info(params.oozie_jdbc_driver)
      if params.oozie_jdbc_driver == "com.mysql.jdbc.Driver":
         Logger.info('Oozie DB: MySQL')
         Package("mysql-connector-java")
         if os.path.exists('/usr/lib/oozie/libext/mysql-connector-java.jar'):
            rm_cmd=[ 'rm', '-f','/usr/lib/oozie/libext/mysql-connector-java.jar' ] 
            cmd=Popen(rm_cmd)
            out,err=cmd.communicate() 
            Logger.info("Removing existing jdbc symbolic link in /usr/lib/oozie/libext/")
            Logger.info(str(out))
            Logger.info(str(err))
         extract_cmd=[ 'ln', '-s','/usr/share/java/mysql-connector-java.jar','/usr/lib/oozie/libext/mysql-connector-java.jar' ] 
      if params.oozie_jdbc_driver == "org.postgresql.Driver":
         Logger.info('Oozie DB: PostgreSQL')
         #extract_cmd=[ 'ln', '-s','/usr/share/java/postgresql-jdbc.jar','/usr/lib/oozie/libext/postgresql-jdbc.jar' ] 
         extract_cmd=[ 'ln', '-s','/usr/lib/ambari-agent/postgres-jdbc-driver.jar','/usr/lib/oozie/libext/postgres-jdbc-driver.jar' ] 
      if params.oozie_jdbc_driver == "oracle.jdbc.driver.OracleDriver":
         Logger.info('Oozie DB: Oracle')
         extract_cmd=[ 'ln', '-s','/usr/lib/ambari-agent/oracle-jdbc-driver.jar','/usr/lib/oozie/libext/oracle-jdbc-driver.jar' ] 
      cmd=Popen(extract_cmd)
      out,err=cmd.communicate() 
      Logger.info("Creating jdbc symbolic link in /usr/lib/oozie/libext/")
      Logger.info(str(out))
      Logger.info(str(err))
          
      Logger.info(params.oozie_jdbc_driver)
      if params.oozie_jdbc_driver == "com.mysql.jdbc.Driver":
        create_db_cmd = format('su --shell=/bin/bash -l oozie -c "source /etc/profile.d/java.sh && /usr/lib/oozie/bin/ooziedb.sh create -sqlfile oozie.sql -run"') 
      
      if params.oozie_jdbc_driver == "org.postgresql.Driver":
        create_db_cmd = format('su --shell=/bin/bash -l oozie -c "source /etc/profile.d/java.sh && /usr/lib/oozie/bin/ooziedb.sh create -sqlfile oozie.sql -run"') 
      
      if params.oozie_jdbc_driver == "oracle.jdbc.driver.OracleDriver":
        create_db_cmd = format('su --shell=/bin/bash -l oozie -c "source /etc/profile.d/java.sh && /usr/lib/oozie/bin/ooziedb.sh create -sqlfile oozie.sql -run"') 

      cmd=Popen(create_db_cmd, shell=True)
      out,err=cmd.communicate()
      Logger.info("Installing the Oozie Schema in the DB")
      Logger.info(str(out))
      Logger.info(str(err))
