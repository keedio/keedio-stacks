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

from resource_management import *
from yarn_resourcemanager import resourcemanager 

class Resourcemanager(Script):
  def install(self, env):
    import params
    self.install_packages(env)
    #self.install_packages(env,params.exclude_packages)
    env.set_params(params)
    #resourcemanager(action="configure")

  def start(self, env):
    import params

    env.set_params(params)
    resourcemanager(action="configure") # FOR SECURITY
    resourcemanager(action="start")

  def stop(self, env):
    import params

    env.set_params(params)

    resourcemanager(action="stop")

  def status(self, env):
    import status_params

    env.set_params(status_params)
    resourcemanager(action="status")

  def refreshqueues(self, env):
    import params

    self.configure(env)
    env.set_params(params)

    resourcemanager(action="refreshqueues")

  def decommission(self, env):
    import params

    env.set_params(params)
    rm_kinit_cmd = params.rm_kinit_cmd
    yarn_user = params.yarn_user
    conf_dir = params.hadoop_conf_dir
    user_group = params.user_group

    yarn_refresh_cmd = format("{rm_kinit_cmd} yarn --config {conf_dir} rmadmin -refreshNodes")

    File(params.exclude_file_path,
         content=Template("exclude_hosts_list.j2"),
         owner=yarn_user,
         group=user_group
    )

    if params.update_exclude_file_only == False:
      Execute(yarn_refresh_cmd,
            environment= {'PATH' : params.execute_path },
            user=yarn_user)
      pass
    pass


if __name__ == "__main__":
  Resourcemanager().execute()