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
from portal import portal
from subprocess import *

class Portal(Script):
  def install(self, env):
    import params
    env.set_params(params)
    self.install_packages(env)
    portal(action="config")

  def configure(self, env):
    import params
    env.set_params(params)
    portal(action="config")

  def start(self, env):
    import params
    env.set_params(params)
    self.configure(env)
    portal(action="start")

  def stop(self, env):
    import params
    env.set_params(params)
    portal(action="stop")

  def status(self, env):
    portal(action="status")

if __name__ == "__main__":
  Portal().execute()

