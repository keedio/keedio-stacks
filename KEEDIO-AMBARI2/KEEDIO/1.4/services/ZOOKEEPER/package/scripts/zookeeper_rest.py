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
#from script import install_packages
from resource_management import *

from subprocess import *
from utils import *

class zookeeper_rest(Script):
  def install(self, env):
    import params
    self.install_packages(env)
    Package('zookeeper-rest')
    self.configure(env)

  def configure(self, env):
    import params
    env.set_params(params)
    import params
    Directory(format("{config_dir}/rest/"),
            owner=params.zk_user,
            create_parents = True, 
            group=params.user_group
    )
    File(format("{config_dir}/rest/rest.properties"),
       content=Template("rest.properties.j2"),
       owner="root",
       group="root"
    )

  def start(self,env):
    self.configure(env)
    cmd=Popen(['service','zookeeper-rest','start'],stdout=None,stderr=None)
    out,err=cmd.communicate()
    Logger.info("Starting zookeeper REST API")
    Logger.info(str(out))
    Logger.info(str(err))

  def stop(self,env):
    cmd=Popen(['service','zookeeper-rest','stop'],stdout=None,stderr=None)
    out,err=cmd.communicate()
    Logger.info("Stopping zookeeper REST API")
    Logger.info(str(out))
    Logger.info(str(err))

  def status(self, env):
    Logger.info("Checking zookeeper-rest status")
    cmd=Popen(['curl','http://localhost:9998/znodes/v1/'],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info(str(out))
    Logger.info(str(err))
    rc=cmd.returncode
    check_rc(rc,out,err)

if __name__ == "__main__":
  zookeeper_rest().execute()
