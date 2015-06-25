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
from utils import check_rc
def oozie(action=None,is_server=False):
  import params
  
  if action == 'start' or action == 'stop' or action == 'status':
    cmd=Popen(['service','oozie',action],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info('Oozie action: %s.\nSTDOUT=%s\nSTDERR=%s' % (action,out,err))
    if action == 'start' or action == 'status':
      check_rc(cmd.returncode,stdout=out,stderr=err)

  if action == 'config' :
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
      #File('/usr/lib/oozie/libext/ext-2.2.1.zip',
       # content=StaticFile('ext-2.2.1.zip'))
      ## oozie expect ext-2.2 directory and looks to be hardcoded
      #extract_cmd=[ 'unzip', '/usr/lib/oozie/libext/ext-2.2.1.zip','-d','/usr/lib/oozie/libext/ext-2.2' ]
      #Popen(extract_cmd)
      

      if params.oozie_jdbc_driver == "com.mysql.jdbc.Driver":
        create_db_cmd = [ "/usr/lib/oozie/bin/ooziedb.sh", "create", "-run" ]
      
      if params.oozie_jdbc_driver == "org.postgresql.Driver":
        pass
      
      if params.oozie_jdbc_driver == "oracle.jdbc.driver.OracleDriver":
        pass

      Popen(create_db_cmd)
