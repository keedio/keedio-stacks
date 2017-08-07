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
from utils import check_rc
from subprocess import *
import yarn_conf

def resourcemanager(action=None):
  if action == "configure" or action == "start":
    yarn_conf.configure(service="resourcemanager")

  if action == "start" or action == "stop" or action == "status":
    cmd = Popen(["service","hadoop-yarn-resourcemanager",action],stdout=PIPE,stderr=PIPE)
    out,err = cmd.communicate()
    rc=cmd.returncode
    check_rc(rc,stdout=out,stderr=err)
  elif action == 'refreshQueues':
    rm_kinit_cmd = params.rm_kinit_cmd
    refresh_cmd = format("{rm_kinit_cmd} export HADOOP_LIBEXEC_DIR={hadoop_libexec_dir} && {yarn_container_bin}/yarn rmadmin -refreshQueues")

    Execute(refresh_cmd,
            user = usr,
            timeout = 20, # when Yarn is not started command hangs forever and should be killed
            tries = 5,
            try_sleep = 5,
            timeout_kill_strategy = TerminateStrategy.KILL_PROCESS_GROUP, # the process cannot be simply killed by 'kill -15', so kill pg group instread.
    )
