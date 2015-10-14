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

jdbc_driver = config['configurations']['hive-site']['javax.jdo.option.ConnectionDriverName']
jdbc_connection = config['configurations']['hive-site']['javax.jdo.option.ConnectionURL']
jdbc_host = jdbc_connection.split('/')[2]
jdbc_db = config['configurations']['hive-site']['ambari.hive.db.schema.name'] 
jdbc_username = config['configurations']['hive-site']['javax.jdo.option.ConnectionUserName']
jdbc_password = default('/configurations/hive-site/javax.jdo.option.ConnectionPassword',None)

hive_metastore_warehouse = config['configurations']['hive-site']['hive_metastore_warehouse']
hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hdfs_principal_name = default('/configurations/hadoop-env/hdfs_principal_name',None)
hdfs_user_keytab = default('/configurations/hadoop-env/hdfs_user_keytab',None)
kerberos_cache_file = default('/configurations/cluster-env/kerberos_cache_file','/tmp/ccache_keytab')


hostname = config['hostname']
security_enabled = config['configurations']['cluster-env']['security_enabled']
hive_metastore_keytab = config['configurations']['hive-site']['hive.metastore.kerberos.keytab.file']
hive_metastore_principal = config['configurations']['hive-site']['hive.metastore.kerberos.principal']
zookeeper_client_port = str(config['configurations']['hive-site']['hive.zookeeper.client.port'])
zookeeper_hosts = config['clusterHostInfo']['zookeeper_hosts']
zookeeper_hosts_str=', '.join(str(e) for e in zookeeper_hosts)
aux_join_str=':'+zookeeper_client_port+','
zookeeper_hosts_port=aux_join_str.join(str(e) for e in zookeeper_hosts)+':'+zookeeper_client_port
hive_admin_users = config['configurations']['hive-site']['hive_admin_users']
hive_server2_port = config['configurations']['hive-site']['hive.server2.thrift.port']
hive_server2_host = config['clusterHostInfo']['hive_server_host'][0]
hive_server2_principal = config['configurations']['hive-site']['hive.server2.authentication.kerberos.principal']
hive_server2_keytab = config['configurations']['hive-site']['hive.server2.authentication.kerberos.keytab']
hive_server2_spnego_principal = config['configurations']['hive-site']['hive.server2.authentication.spnego.principal']
hive_server2_spnego_keytab = config['configurations']['hive-site']['hive.server2.authentication.spnego.keytab']

hive_heapsize = config['configurations']['hive-env']['hive.heapsize']
config_dir = "/etc/hive/conf"
hive_user = 'hive'
hive_group = config['configurations']['cluster-env']['user_group']

hostname = config['hostname']
is_hive_server = hostname in config['clusterHostInfo']['hive_server_host']
is_hive_metastore = hostname in config['clusterHostInfo']['hive_metastore_hosts']


exclude_packages=[]
if not is_hive_metastore:
  exclude_packages += ['hive-metastore','mysql-connector-java','mysql']
if not is_hive_server:
  exclude_packages += ['hive-server2']


#service check
smoke_user =  config['configurations']['cluster-env']['smokeuser']
smoke_user_principal = default('/configurations/cluster-env/smokeuser_principal_name',None)
smoke_user_keytab = default('/configurations/cluster-env/smokeuser_keytab',None) 

