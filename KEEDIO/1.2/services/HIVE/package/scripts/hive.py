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
from utils import *
from functools import partial

def hive(action=None,service=None):
  
  if action == 'start' or action == 'stop' or action == 'status':
    if action != 'status':
      import params
      # CREATION OF HDFS DIRECTORY
      execute_hdfs = partial(execute_sudo_krb,user=params.hdfs_user,principal=params.hdfs_principal_name,keytab=params.hdfs_user_keytab)

      create_warehouse = ["hdfs","dfs","-mkdir","-p",params.hive_metastore_warehouse]
      chown_warehouse = ["hdfs","dfs","-chown",params.hive_user, params.hive_metastore_warehouse]
      chmod_warehouse = ["hdfs","dfs","-chmod","750",params.hive_metastore_warehouse]
  
      execute_hdfs(create_warehouse)
      execute_hdfs(chown_warehouse)
      execute_hdfs(chmod_warehouse)
    
    cmd=Popen(['service',service,action],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info('%s action: %s.\nSTDOUT=%s\nSTDERR=%s' % (service,action,out,err))
    if action == 'start' or action == 'status':
      check_rc(cmd.returncode,stdout=out,stderr=err)

  if action == 'config' :
    import params
    File(params.config_dir + '/hive-site.xml',
      content=Template('hive-site.j2'),
      owner=params.hive_user,
      group=params.hive_group,
      mode=0644)
    File(params.config_dir + '/hive-env.sh',
      content=Template('hive-env.j2'),
      owner=params.hive_user,
      group=params.hive_group,
      mode=0644)

