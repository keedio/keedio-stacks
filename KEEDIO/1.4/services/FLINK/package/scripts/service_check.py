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
from functools import partial
from utils import *
from flink import flink

class ServiceCheck(Script):


  def service_check(self, env):
    import params
    env.set_params(params)
    execute_hdfs = partial(execute_sudo_krb,user=params.hdfs_user,principal=params.hdfs_principal_name,keytab=params.hdfs_user_keytab) 
    execute_flink = partial(execute_sudo_krb,user=params.smoke_user,principal=params.smoke_user,keytab=params.smoke_user_keytab)
    Logger.info("Sourcing /etc/profile.d/hadoop-env.sh")
    cmd=Popen('/bin/grep export  /etc/profile.d/hadoop-env.sh ',stdout=PIPE,stderr=PIPE,shell=True)
    out,err=cmd.communicate()
    Logger.info(out)
    Logger.info(err)
    # parsing the output
    listout=out.split('\n')
    listout.remove('')
    for line in listout:
         cmdlist=line.replace('=',' ').split(' ') 
         os.environ[cmdlist[1]]=cmdlist[2]

    Logger.info("The environment for Flink execution:")
    Logger.info(os.environ)
    cmd_create_dir_hdfs=['hdfs','dfs','-mkdir','-p',params.flink_hdfs_home+'/savepoints']
    cmd_chown_dir_hdfs=['hdfs','dfs','-chown','%s:',params.flink_user ,params.flink_hdfs_home]
    cmd_chown_dir_hdfs2=['hdfs','dfs','-chown','%s:',params.flink_user ,params.flink_hdfs_home+'/savepoints']
    cmd_chmod_dir_hdfs=['hdfs','dfs','-chmod','777',params.flink_hdfs_home+'/savepoints']
    execute_hdfs(cmd_create_dir_hdfs)
    execute_hdfs(cmd_chown_dir_hdfs)
    execute_hdfs(cmd_chown_dir_hdfs2)
    execute_hdfs(cmd_chmod_dir_hdfs)
    
    check_flink = ['/usr/lib/flink/default/bin/flink','run','-m','yarn-cluster','-yn','2','-j','/usr/lib/flink/default/examples/batch/KMeans.jar']
    out,err,rc=execute_flink(check_flink)
    Logger.info("Check: Batch Kmeans")
    check_rc(rc,stdout=out,stderr=err)
    Logger.info(out)
    check_flink = ['/usr/lib/flink/default/bin/flink','run','-m','yarn-cluster','-yn','2','-j','/usr/lib/flink/default/examples/streaming/Iteration.jar']
    out,err,rc=execute_flink(check_flink)
    Logger.info("Check: Streaming Iteration")
    check_rc(rc,stdout=out,stderr=err)
    Logger.info(out)

if __name__ == "__main__":
  ServiceCheck().execute()
