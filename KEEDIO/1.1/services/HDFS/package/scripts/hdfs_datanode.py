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

  if action == "configure":
    import params
    # Alessio: we do not need to set particular permission here, the datanode sets the right permission when it is started.
    Directory([params.dfs_data_dir],
        owner=params.hdfs_user,
        group=params.user_group,
        recursive=True
    )
    Directory([params.dfs_domain_socket_dir],
        owner=params.hdfs_user,
        group=params.user_group,
        recursive=True,
        mode=0751 )

  if action == "start":
    cmd=Popen(['service','hadoop-hdfs-datanode',action],stdout=PIPE,stderr=STDOUT)
    out,err=cmd.communicate()
    Logger.info("Alessio: starting datanode")
    Logger.info(out)
    Logger.info(err)
    rc = cmd.returncode
    Logger.info("Datanode service %s: %s" % (action, rc == 0))
    check_rc(rc,stdout=out,stderr=err)

  if action == "stop":
    Logger.info("Datanode service %s")
    cmd=Popen(['service','hadoop-hdfs-datanode',action],stdout=PIPE,stderr=STDOUT)
    out,err=cmd.communicate()
    Logger.info("Alessio: stopping datanode")
    Logger.info(out)
    Logger.info(err)

  if action == "status":
    cmd=Popen(['service','hadoop-hdfs-datanode',action],stdout=PIPE,stderr=STDOUT)
    out,err=cmd.communicate()
    Logger.info("Alessio:Checking datanode status")
    Logger.info(out)
    Logger.info(err)
    rc = cmd.returncode
    Logger.info("Datanode service %s: %s" % (action, rc == 0))
    check_rc(rc,stdout=out,stderr=err)


