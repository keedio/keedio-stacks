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

from resource_management import *
import sys

from functools import partial
from ambari_agent.AgentException import AgentException
from subprocess import *
from utils import execute_sudo_krb

def spark(service=None,action=None):
  import params
  if action == "config":
    
    execute_hdfs = partial(execute_sudo_krb,user=params.hdfs_user,principal=params.hdfs_principal_name,keytab=params.hdfs_user_keytab)
    execute_spark = partial(execute_sudo_krb,user=params.spark_user,principal=params.spark_principal,keytab=params.spark_keytab)

    create_home = ["hdfs","dfs","-mkdir","-p",params.spark_home]
    chown_home = ["hdfs","dfs","-chown",params.spark_user, params.spark_home]

    upload_jars = ["hdfs","dfs","-put",params.spark_yarn_lib_dir,params.spark_home]
 
    execute_hdfs(create_home)
    execute_hdfs(chown_home)
    execute_spark(upload_jars)

  if action == "install":
    configurations = params.config['configurations']['spark']
    File(format(params.spark_conf_dir+"/spark-defaults.conf"),
       content=Template("spark_defaults.j2",configurations=configurations),
       owner=params.spark_user,
       group=params.spark_group
    )

