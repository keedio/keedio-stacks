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

# server configurations
config = Script.get_config()

hive_metastore_host = config['clusterHostInfo']['hive_metastore_hosts'][0]
hive_metastore_port = config['configurations']['hive-site']['hive_metastore_port']
jdbc_connection = config['configurations']['hive-site']['jdbc_connection']
jdbc_driver = config['configurations']['hive-site']['jdbc_driver']
jdbc_username = config['configurations']['hive-site']['jdbc_username']
jdbc_password = config['configurations']['hive-site']['jdbc_password']
hive_metastore_warehouse = config['configurations']['hive-site']['hive_metastore_warehouse']
security_enabled = config['configurations']['cluster-env']['security_enabled']
hive_metastore_keytab = config['configurations']['hive-site']['hive_metastore_keytab']
hive_metastore_principal = config['configurations']['hive-site']['hive_metastore_principal']
zookeeper_hosts = config['clusterHostInfo']['zookeeper_hosts']
hive_admin_users = config['configurations']['hive-site']['hive_admin_users']
hive_server2_port = config['configurations']['hive-site']['hive_server2_port']
hive_server2_host = config['clusterHostInfo']['hive_server2_hosts'][0]
hive_server2_principal = config['configurations']['hive-site']['hive_server2_principal']
hive_server2_keytab = config['configurations']['hive-site']['hive_server2_keytab']
hive_server2_spnego_principal = config['configurations']['hive-site']['hive_server2_spnego_principal']
hive_server2_spnego_keytab = config['configurations']['hive-site']['hive_server2_spnego_keytab']

config_dir = "/etc/hive/conf"
hive_user = 'hive'
hive_group = config['configurations']['cluster-env']['user_group']

hostname = config['hostname']
is_hive_server = hostname in config['clusterHostInfo']['hive_server2_hosts']
is_hive_metastore = hostname in config['clusterHostInfo']['hive_metastore_hosts']


exclude_packages=[]
if not is_hive_metastore:
  exclude_packages += ['hive-metastore','mysql-connector-java']
if not is_hive_server:
  exclude_packages += ['hive-server2']



