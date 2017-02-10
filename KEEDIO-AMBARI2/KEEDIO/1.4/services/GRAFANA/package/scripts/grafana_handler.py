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

from elasticsearch import elasticsearch
from grafana import grafana

         
class GrafanaHandler(Script):
  def install(self, env):
    import params
    self.install_packages(env)
    grafana(action="install")
    
  def configure(self, env):
    import params
    env.set_params(params)
    grafana(action='config')
    
  def start(self, env):
    import params
    env.set_params(params)
    if not params.is_es_master and not params.is_es_indexer:
      elasticsearch(action='config')
      elasticsearch(action='start')
    self.configure(env)
    grafana(action='start')
    
  def stop(self, env):
    import params
    if not params.is_es_master and not params.is_es_indexer:
      elasticsearch(action='stop')
    grafana(action='stop')

  def status(self, env):
    grafana(action='status')
     
if __name__ == "__main__":
  GrafanaHandler().execute()
