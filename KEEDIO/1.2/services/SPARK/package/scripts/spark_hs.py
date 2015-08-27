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
from yaml_utils import escape_yaml_propetry

def spark_hs(action):
  if action == "config":
   configurations = params.config['configurations']['spark']
    File(format(params.spark_conf_dir+"/spark-defaults.conf"),
       content=Template("spark_defaults.j2",configurations=configurations),
       owner=params.spark_user,
       group=params.spark_group
    )
    

  if action == "install":
    Logger.info("Installing Spark History Server") 

  if action == "start" or action == "stop" or action == "status":
    cmd=Popen(['service','spark-history-server',action],stdout=PIPE,stderr=PIPE)
    if action == "status":
      from functions import check_rc
      out,err=cmd.communicate()
      rc=cmd.returncode
      Logger.info("Spark History Server %s: %s" % (action, cmd.returncode == 0))
   
      check_rc(rc,stdout=out,stderr=err)

