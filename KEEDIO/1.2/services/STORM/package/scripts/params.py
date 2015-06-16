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

from resource_management.libraries.functions.version import format_hdp_stack_version, compare_versions
from resource_management import *
import status_params

# server configurations
config = Script.get_config()

storm_user = config['configurations']['storm-env']['storm_user']
conf_dir = "/etc/storm/conf"
storm_local_dir = config['configurations']['storm-site']['storm.local.dir']
storm_log_dir = "/var/log/storm"
user_group = config['configurations']['cluster-env']['user_group']

nimbus_port = config['configurations']['storm-site']['nimbus.thrift.port']
nimbus_host = config['configurations']['storm-site']['nimbus.host']

storm_env_sh_template = config['configurations']['storm-env']['content']

hostname = config['hostname']
is_nimbus_server = hostname in config['clusterHostInfo']['nimbus_hosts']
is_supervisor_server = hostname in config['clusterHostInfo']['supervisor_hosts']
is_drpc_server = hostname in config['clusterHostInfo']['drpc_server_hosts']
is_storm_ui_server = hostname in config['clusterHostInfo']['storm_ui_server_hosts']

nimbus_server = config['clusterHostInfo']['nimbus_hosts'][0]
zookeeper_hosts = config['clusterHostInfo']['zookeeper_hosts']
drpc_hosts = default("/clusterHostInfo/drpc_server_hosts",[])
has_drpc_hosts = drpc_hosts != []

exclude_packages=[]
if not is_nimbus_server:
  exclude_packages += ['storm-nimbus']
if not is_supervisor_server:
  exclude_packages += ['storm-supervisor','storm-logviewer']
if not is_drpc_server:
  exclude_packages += ['storm-drpc']
if not is_storm_ui_server:
  exclude_packages += ['storm-ui']
