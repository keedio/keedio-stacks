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

Ambari Agent

"""

import sys
from resource_management import *

from zookeeper import zookeeper
from subprocess import *
from utils import *

class ZookeeperServer(Script):
  def install(self, env):
    import params
    self.install_packages(env)
    self.configure(env)

  def configure(self, env):
    import params
    env.set_params(params)
    zookeeper(type='server')

  def start(self,env):
    self.configure(env)
    cmd=Popen(['service','zookeeper-server','start'],stdout=None,stderr=None)
    out,err=cmd.communicate()
    Logger.info("Starting zookeeper server")
    Logger.info(out)
    Logger.info(err)

  def stop(self,env):
    cmd=Popen(['service','zookeeper-server','stop'],stdout=None,stderr=None)
    out,err=cmd.communicate()
    Logger.info("Stopping zookeeper server")
    Logger.info(out)
    Logger.info(err)

  def status(self, env):
    Logger.info("Checking zookeeper server status")
    cmd=Popen(['service','zookeeper-server','status'],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info(out)
    Logger.info(err)
    rc=cmd.returncode
    check_rc(rc,out,err)

if __name__ == "__main__":
  ZookeeperServer().execute()
