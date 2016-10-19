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
from esdumper import esdumper
from subprocess import *

class Es_dumper(Script):
  def install(self, env):
    import params
    env.set_params(params)
    self.install_packages(env)
    File(format("/etc/init.d/esdumper"),
       content=Template("esdumper.j2"),
       owner='root',
       group='root',
       mode=0755
    )

  def configure(self, env):
    import params
    env.set_params(params)
    #This sets up directories
    esdumper(action="config")

  def start(self, env):
    import params
    env.set_params(params)
    self.configure(env)
    esdumper(action="start")
 
  def stop(self, env):
    import params
    env.set_params(params)
    esdumper(action="stop")

  def status(self, env):
    import params
    env.set_params(params)
    esdumper(action="status")

if __name__ == "__main__":
   Es_dumper().execute()

