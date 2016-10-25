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

# server configurations
config = Script.get_config()
cluster_name = config['clusterName']
authentication = str(default('/configurations/main/authentication','internal'))
kerberos_domain = default('/configurations/cluster-env/kerberos_domain',None)
kerberos_cache_file = default('/configurations/cluster-env/kerberos_cache_file','/tmp/ccache_keytab')
security_enabled = config['configurations']['cluster-env']['security_enabled']

hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hdfs_principal_name = default('/configurations/hadoop-env/hdfs_principal_name',None)
hdfs_user_keytab = default('/configurations/hadoop-env/hdfs_user_keytab',None)
livy_principal = default('/configurations/oozie-site/oozie.service.HadoopAccessorService.kerberos.principal',None)
livy_keytab = default('/configurations/oozie-site/oozie.service.HadoopAccessorService.keytab.file',None)
livy_spnego_principal = default('/configurations/oozie-site/oozie.authentication.kerberos.principal',None)
livy_spnego_keytab= default('/configurations/oozie-site/oozie.authentication.kerberos.keytab',None)
smoke_user_keytab = default('/configurations/cluster-env/smokeuser_keytab',None)
smoke_user = config['configurations']['cluster-env']['smokeuser'] 

livy_server=default("/clusterHostInfo/livy_server_host", ["localhost"])[0]
livy_port=str(default('/configurations/livy/livy_port',8998))
hostname = config['hostname']

