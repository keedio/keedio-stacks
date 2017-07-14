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

from database import database

         
class CouchbaseHandler(Script):
  def install(self, env):
    import params
    env.set_params(params)
    self.install_packages(env)
    database(action="install")
    
  def configure(self, env):
    import params
    env.set_params(params)
    database(action='config')
    
  def start(self, env):
    import params
    env.set_params(params)
    self.configure(env)
    database(action='start')
    database(action='post')
    
  def stop(self, env):
    import params
    database(action='stop')

  def rebalance(self, env):
    import params
    database(action='rebalance')

  def status(self, env):
    database(action='status')
     
if __name__ == "__main__":
  CouchbaseHandler().execute()
