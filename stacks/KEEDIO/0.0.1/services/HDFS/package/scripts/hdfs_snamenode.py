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
from utils import service, check_rc
from subprocess import *

def snamenode(action=None, format=False):

  if action == "configure":
    import params
    Directory(params.fs_checkpoint_dir,
              recursive=True,
              mode=0755,
              owner=params.hdfs_user,
              group=params.user_group)
    File(params.exclude_file_path,
         content=Template("exclude_hosts_list.j2"),
         owner=params.hdfs_user,
         group=params.user_group)
  elif action == "start" or action == "stop" or action == "status":
    """
    In this point, HDP code uses a much more complex execution,
    I assume it is for standarization porpuses and avoid using
    /etc/init.d
    """
    executed = Popen(["service","hadoop-hdfs-secondarynamenode",action],stdout=PIPE,stderr=PIPE)
    out,err = executed.communicate()
    rc = executed.returncode
    check_rc(rc,out,err)

