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
import multiprocessing
cpu_count = multiprocessing.cpu_count()

config = Script.get_config()


cluster_name = config['clusterName']
hostname = config['hostname']
security_enabled = config['configurations']['cluster-env']['security_enabled']
realm = config['configurations']['cluster-env']['kerberos_domain']


cassandra_hosts = ",".join([str(elem) for elem in default('/clusterHostInfo/cassandra_hosts',[])])

tokens = default('/configurations/cassandra/tokens',256)
cassandra_data_path = list(str(config['configurations']['cassandra']['cassandra_data_path']).split(","))
cassandra_commit_log = config['configurations']['cassandra']['cassandra_commit_log']
storage_port = config['configurations']['cassandra']['storage_port']
native_transport_port = config['configurations']['cassandra']['native_transport_port']
rpc_port = config['configurations']['cassandra']['rpc_port']
rpc_max_threads = config['configurations']['cassandra']['rpc_max_threads']
endpoint_snitch = config['configurations']['cassandra']['endpoint_snitch'] 
rack = config['configurations']['cassandra']['rack'] 
datacenter = config['configurations']['cassandra']['datacenter'] 

cassandra_user = default('/configurations/cassandra-env/cassandra_user','cassandra')
#cassandra_principal_name = default('/configurations/cassandra-env/cassandra_principal_name',None)
#cassandra_keytab_file = default('/configurations/cassandra-env/cassandra_keytab',None)
#cassandra_spnego_principal_name = default('/configurations/cassandra-env/cassandra_principal_spnego',None)
#hdfs_principal_name = default('/configurations/hadoop-env/hdfs_principal_name',None)
#hdfs_user_keytab = default('/configurations/hadoop-env/hdfs_user_keytab',None)
#kerberos_cache_file = default('/configurations/cluster-env/kerberos_cache_file','/tmp/ccache_keytab')

