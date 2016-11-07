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
from resource_management import *

from freeipa import freeipaclient

         
class IPAReplicaHandler(Script):
  def install(self, env):
      Logger.info("No install")
     
#    self.install_packages(env)
#    freeipaclient(action='install')
    
  def configure(self, env):
     Logger.info("No configure")
#    import params
#    env.set_params(params)
#    freeipaclient(action='config')
    

  def start(self, env):
     Logger.info("No start")

  def stop(self, env):
     Logger.info("No stop")

  def status(self, env):
    raise ClientComponentHasNoStatus()
     
if __name__ == "__main__":
  IPAReplicaHandler().execute()
