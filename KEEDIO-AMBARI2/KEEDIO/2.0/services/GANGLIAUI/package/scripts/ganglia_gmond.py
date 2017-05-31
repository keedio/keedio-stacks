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
from subprocess import *
from glob import glob
from os.path import basename
import os

def gmond(action=None):
  # 'start' or 'stop'
  import params 
  Logger.info("Ganglia %s services %s" % ('gmond',action))
  os.chdir('/etc/systemd/system')
  cmd=Popen(['systemctl','daemon-reload'],stdout=PIPE,stderr=PIPE)
  cmd=Popen(['systemctl','list-unit-files','gmond*'],stdout=PIPE,stderr=PIPE)

  out,err=cmd.communicate()
  Logger.info(str(out))
  clusters = glob('/etc/systemd/system/gmond.*')
  Logger.info(str(clusters))
  for service in clusters:
    base=basename(service)
    cmd=Popen(['systemctl',action,base],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info(str(out))
    Logger.info(str(err))
  cmd=Popen(['systemctl',action,'gmond.service'],stdout=PIPE,stderr=PIPE)
  out,err=cmd.communicate()
  Logger.info(str(out))
  Logger.info(str(err))
    
  rc=cmd.returncode
  Logger.info("Ganglia %s service %s: %s" % (service,action, cmd.returncode == 0))
   
  if action == "status" :
      from functions import check_rc
      check_rc(rc,stdout=out,stderr=err)
