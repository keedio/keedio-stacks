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
import os
from os import path
from resource_management import *
from ganglia import generate_daemon
import ganglia
import functions
from ganglia_gmond import gmond


class GangliaMonitor(Script):
  def install(self, env):
    import params

    self.install_packages(env, params.exclude_packages)
    env.set_params(params)
    self.configure(env)

  def start(self, env):
    import params
    env.set_params(params)
    self.configure(env)
    gmond("start")

  def stop(self, env):
    gmond("stop")


  def status(self, env):
    gmond("status")

  def configure(self, env):
    import params

    ganglia.config()

    self.generate_slave_configs()

    File(path.join(params.ganglia_dir, "gmond.conf"),
         owner="root",
         group=params.user_group
    )

    if params.is_ganglia_server_host:
      self.generate_master_configs()

      if len(params.gmond_apps) != 0:
        self.generate_app_configs()
        pass
      pass


  def generate_app_configs(self):
    import params

    for gmond_app in params.gmond_apps:
      generate_daemon("gmond",
                      name=gmond_app[0],
                      role="server",
                      owner="root",
                      group=params.user_group)
      generate_daemon("gmond",
                      name = gmond_app[0],
                      role = "monitor",
                      owner = "root",
                      group = params.user_group)
    pass

  def generate_slave_configs(self):
    import params

    generate_daemon("gmond",
                    name = "Slaves",
                    role = "monitor",
                    owner = "root",
                    group = params.user_group)
    if 'ElasticSearch' in params.clusters:
      generate_daemon("gmond",
        name = "ElasticSearch",
        role = "monitor",
        owner = "root",
        group = params.user_group)
      


  def generate_master_configs(self):
    import params
    for service in params.clusters:
      generate_daemon("gmond",
                      name = service,
                      role = "server",
                      owner = "root",
                      group = params.user_group)

if __name__ == "__main__":
  GangliaMonitor().execute()
