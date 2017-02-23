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

class ServiceCheck(Script):


  def service_check(self, env):
    import params,json, pprint, requests, textwrap, time 
    env.set_params(params)
    
    # Define partial aux functions
    execute_hdfs = partial(execute_sudo_krb,user=params.hdfs_user,principal=params.hdfs_principal_name,keytab=params.hdfs_user_keytab)
    #execute_zeppelin = partial(execute_sudo_krb,user=params.smoke_user,principal=params.smoke_user,keytab=params.smoke_user_keytab)


    # HDFS oozie user init
    cmd_create_dir_hdfs=['hdfs','dfs','-mkdir','-p','/user/%s' % 'zeppelin']
    cmd_chown_dir_hdfs=['hdfs','dfs','-chown','%s:' % 'zeppelin','/user/%s' % 'zeppelin']
    execute_hdfs(cmd_create_dir_hdfs)
    execute_hdfs(cmd_chown_dir_hdfs)



if __name__ == "__main__":
  ServiceCheck().execute()
