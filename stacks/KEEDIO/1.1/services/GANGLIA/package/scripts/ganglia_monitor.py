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

    File("/etc/init.d/gmond" + name,
       content=StaticFile("gmond.init"),
       mode=0755
    )
    functions.turn_off_autostart(params.gmond_service_name)

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


  def generate_master_configs(self):
    import params

    if params.has_namenodes:
      generate_daemon("gmond",
                      name = "NameNode",
                      role = "server",
                      owner = "root",
                      group = params.user_group)
    if params.has_hbase_masters:
      generate_daemon("gmond",
                      name = "BaseMaster",
                      role = "server",
                      owner = "root",
                      group = params.user_group)
    if params.has_resourcemanager:
      generate_daemon("gmond",
                      name = "ResourceManager",
                      role = "server",
                      owner = "root",
                      group = params.user_group)
    if params.has_nodemanager:
      generate_daemon("gmond",
                      name = "NodeManager",
                      role = "server",
                      owner = "root",
                      group = params.user_group)
    if params.has_historyserver:
      generate_daemon("gmond",
                      name = "HistoryServer",
                      role = "server",
                      owner = "root",
                      group = params.user_group)
    if params.has_slaves:
      generate_daemon("gmond",
                      name = "DataNode",
                      role = "server",
                      owner = "root",
                      group = params.user_group)
    if params.has_hbase_rs:
      generate_daemon("gmond",
                      name = "HBaseRegionServer",
                      role = "server",
                      owner = "root",
                      group = params.user_group)
    if params.has_nimbus_server:
      generate_daemon("gmond",
                      name = "Nimbus",
                      role = "server",
                      owner = "root",
                      group = params.user_group)
    if params.has_supervisor_server:
      generate_daemon("gmond",
                      name = "Supervisor",
                      role = "server",
                      owner = "root",
                      group = params.user_group)
    if params.has_kafka_broker:
      generate_daemon("gmond",
                      name = "Kafka",
                      role = "server",
                      owner = "root",
                      group = params.user_group)
    if params.has_flume:
      generate_daemon("gmond",
                      name = "FlumeServer",
                      role = "server",
                      owner = "root",
                      group = params.user_group)
    if params.has_journalnode:
      generate_daemon("gmond",
                      name = "JournalNode",
                      role = "server",
                      owner = "root",
                      group = params.user_group)
    generate_daemon("gmond",
                    name = "Slaves",
                    role = "server",
                    owner = "root",
                    group = params.user_group)


if __name__ == "__main__":
  GangliaMonitor().execute()
