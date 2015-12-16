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

config = Script.get_config()

security_enabled = config['configurations']['cluster-env']['security_enabled']
kerberos_cache_file = default('/configurations/cluster-env/kerberos_cache_file','/tmp/ccache_keytab')
kerberos_domain = config['configurations']['cluster-env']['kerberos_domain']

smoke_user_keytab = default('/configurations/cluster-env/smokeuser_keytab',None)
smoke_user = config['configurations']['cluster-env']['smokeuser']

camus_user = config['configurations']['camus']['camus_user']
camus_group = config['configurations']['camus']['camus_group']
camus_hdfs_home = config['configurations']['camus']['camus_hdfs_home']
camus_local_home = config['configurations']['camus']['camus_local_home']

camus_principal = default('/configurations/camus/camus_principal',None)
camus_keytab = default('/configurations/camus/camus_keytab',None)

camushs_principal_name = default('/configurations/camus/dfs.camus.kerberos.principal',None)
camushs_keytab = default('/configurations/camus/camushs_keytab',None)

hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hdfs_principal_name = default('/configurations/hadoop-env/hdfs_principal_name',None)
hdfs_user_keytab = default('/configurations/hadoop-env/hdfs_user_keytab',None)

camus_conf_dir = config['configurations']['camus']['camus.configuration.directory']
camus_assembly = config['configurations']['camus']['camus_assembly']
camus_examples_jar = config['configurations']['camus']['camus_examples_jar']

#namenode_host = default("/clusterHostInfo/namenode_host", ["none"])
#namenode_host =str(namenode_host[0])

