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
from resource_management.libraries.functions.mounted_dirs_helper import handle_mounted_dirs
from utils import * 
from subprocess import *
import os

def create_dirs(data_dir):
  """
  :param data_dir: The directory to create
  :param params: parameters
  """
  import params
  Directory(data_dir,
            create_parents = True,
            cd_access="a",
            mode=0755,
            owner=params.hdfs_user,
            group=params.user_group,
            ignore_failures=True
  )
def datanode(action=None):

  if action == "configure":
    import params
    # We do not need to set particular permission here, the datanode sets the right permission when it is started.
    #Directory(params.dfs_data_dir.split(','),
    #    owner=params.hdfs_user,
    #    group=params.user_group,
    #    create_parents=True
    #)
    Directory([params.dfs_domain_socket_dir],
        owner=params.hdfs_user,
        group=params.user_group,
        create_parents=True,
        mode=0751 )

    data_dir_to_mount_file_content = handle_mounted_dirs(create_dirs, params.dfs_data_dirs, params.data_dir_mount_file, params)
    # create a history file used by handle_mounted_dirs
    File(params.data_dir_mount_file,
         owner=params.hdfs_user,
         group=params.user_group,
         mode=0644,
         content=data_dir_to_mount_file_content
    )

  if action == "start":
    cmd=Popen(['service','hadoop-hdfs-datanode',action],stdout=PIPE,stderr=STDOUT)
    out,err=cmd.communicate()
    Logger.info("Starting datanode")
    Logger.info(str(out))
    Logger.info(str(err))
    rc = cmd.returncode
    Logger.info("Datanode service %s: %s" % (action, rc == 0))
    check_rc(rc,stdout=out,stderr=err)

  if action == "stop":
    Logger.info("Datanode service stop")
    cmd=Popen(['service','hadoop-hdfs-datanode',action],stdout=PIPE,stderr=STDOUT)
    out,err=cmd.communicate()
    Logger.info("Stopping datanode")
    Logger.info(str(out))
    Logger.info(str(err))

  if action == "status":
    cmd=Popen(['service','hadoop-hdfs-datanode',action],stdout=PIPE,stderr=STDOUT)
    out,err=cmd.communicate()
    Logger.info("Checking datanode status")
    Logger.info(str(out))
    Logger.info(str(err))
    rc = cmd.returncode
    Logger.info("Datanode service %s: %s" % (action, rc == 0))
    check_rc(rc,stdout=out,stderr=err)


