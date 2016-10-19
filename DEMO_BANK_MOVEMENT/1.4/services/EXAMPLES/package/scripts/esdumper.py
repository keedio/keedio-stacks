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
import sys
from subprocess import *
from resource_management import *

def esdumper(action):
  if action == "config":
   import params
   cmd=Popen(['/opt/keedio-examples/bankmovements-demo/sparkstreamingvectodemo/setup.sh'],stdout=PIPE,stderr=PIPE)
   out,err=cmd.communicate()
   File(format("/etc/sudoers"),
       content=Template("sudoers.j2"),
       owner='root',
       group='root',
       mode=0400
       )
    

  if action == "install":
    Logger.info("Installing ES dumper") 

  if action == "start" or action == "stop" or action == "status":
    cmd=Popen(['service','esdumper',action],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()

    if action == "start" or action == "stop":
      Logger.info("ES dumper: "+str(action))
      Logger.info(out)
      Logger.info(err)
    if action == "status":
      from functions import check_rc
      rc=cmd.returncode
      Logger.info("ES dumper %s: %s" % (action, cmd.returncode == 0))
   
      check_rc(rc,stdout=out,stderr=err)

