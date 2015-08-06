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

from subprocess import *

def portal(service=None,action=None):

  if action == "config":
    import params
    #configurations = params.config['configurations']['spark']
    print params.portal_conf_dir+params.portal_conf_dir
    File(format(params.portal_conf_dir+"00-default.conf"),
       content=Template("00-default.conf.j2"),
       owner="root",
       group="root"
    )
    File(format(params.portal_www_dir+"/index.html"),
      content=Template("index.html.j2"),
      owner="root",
      group="root"
    )
    File(format(params.portal_www_dir+"/background.png"),
      content=StaticFile("background.png"),
      owner="root",
      group="root"
    )

  if action == "start" or action == "stop":
    cmd=Popen(['service','httpd',action],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    rc=cmd.returncode
    Logger.info("Httpd service %s: %s" % (action, cmd.returncode == 0)) 

  if action == "status":
      from utils import check_rc
      cmd=Popen(['service','httpd',action],stdout=PIPE,stderr=PIPE)
      out,err=cmd.communicate()
      rc=cmd.returncode
      Logger.info(rc)
      Logger.info("Httpd service %s: %s" % (action, cmd.returncode == 0))

      check_rc(rc,stdout=out,stderr=err)

  
