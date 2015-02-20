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
from resource_management.libraries.functions.dfs_datanode_helper import handle_dfs_data_dir
from utils import * 
from subprocess import *


def datanode(action=None):
  import params

  if action == "configure":
    os_mkdir(params.dfs_data_dir,
      owner=params.hdfs_user,
      group=params.hdfs_group,
      mode=750)

    Directory(params.dfs_domain_socket_dir,
              recursive=True,
              mode=0751,
              owner=params.hdfs_user,
              group=params.user_group)

  if action == "start" or action == "stop":
    """
    In this point, HDP code uses a much more complex execution,
    I assume it is for standarization porpuses and avoid using
    /etc/init.d
    """
    cmd=Popen(['service','hadoop-hdfs-datanode',action],stdout=PIPE,stderr=STDOUT)
    out,err=cmd.communicate()
    rc = cmd.returncode
    Logger.info("Datanode service %s: %s" % (action, rc == 0))

