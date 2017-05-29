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
from ganglia_gmetad import gmetad


class GangliaServer(Script):
  def install(self, env):
    import params

    self.install_packages(env)
    Package("ganglia-gmetad")
    Package("ganglia-web")
    env.set_params(params)
    self.configure(env)
    
    functions.turn_off_autostart(params.gmond_service_name) 
    # since the package is installed as well
    File("/etc/httpd/conf.d/ganglia.conf",
      content=StaticFile("ganglia.conf"),
      owner="apache",
      group="apache"
    )

    functions.turn_off_autostart("gmetad")

  def start(self, env):
    import params
    env.set_params(params)
    self.configure(env)
    gmetad("start")

  def stop(self, env):
    gmetad("stop")

  def status(self, env):
    gmetad("status")

  def configure(self, env):
    import params
    env.set_params(params)

    ganglia.config()

    generate_daemon("gmetad",
                    name = "gmetad",
                    role = "server",
                    owner = "root",
                    group = params.user_group)

    server_files()
    File(path.join(params.ganglia_dir, "gmetad.conf"),
         owner="root",
         group=params.user_group
    )


def server_files():
  import params

  rrd_py_path = params.rrd_py_path
  Directory(rrd_py_path,
            create_parents=True
  )
  rrd_py_file_path = path.join(rrd_py_path, "rrd.py")
  TemplateConfig(rrd_py_file_path,
                 owner="root",
                 group="root",
                 mode=0755
  )
  rrd_file_owner = params.gmetad_user

  Directory(params.rrdcached_base_dir,
            owner=rrd_file_owner,
            group=rrd_file_owner,
            mode=0755,
            create_parents=True
  )
  
  if System.get_instance().os_family in ["ubuntu","suse"]:
    File( params.ganglia_apache_config_file,
      content = Template("ganglia.conf.j2"),
      mode = 0644
    )


if __name__ == "__main__":
  GangliaServer().execute()
