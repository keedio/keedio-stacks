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
import itertools
import os

# server configurations
config = Script.get_config()

namenode=config['configurations']['core-site']['fs.defaultFS']
resourcemanager=config['configurations']['yarn-site']['yarn.resourcemanager.address']

example_job='map-reduce'
ambari_server_hostname = config['clusterHostInfo']['ambari_server_host'][0]
security_enabled = config['configurations']['cluster-env']['security_enabled']
kerberos_cache_file = config['configurations']['cluster-env']['kerberos_cache_file']
hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hdfs_principal_name = default('/configurations/hadoop-env/hdfs_principal_name',None)
hdfs_user_keytab = default('/configurations/hadoop-site/hdfs_user_keytab',None)

oozie_db_type = default('/configurations/oozie-site/oozie_database',None)
oozie_db_schema_name = config['configurations']['oozie-site']['oozie.db.schema.name']
oozie_db_server = config['configurations']['oozie-site']['oozie.db.server']
oozie_db_user = config['configurations']['oozie-site']['oozie.service.JPAService.jdbc.username']
oozie_db_pass = config['configurations']['oozie-site']['oozie.service.JPAService.jdbc.password']

oozie_data_path = '/var/lib/oozie' 
oozie_catalina_home = '/usr/lib/tomcatserver'
oozie_config_dir = '/etc/oozie/conf'
oozie_log_dir = '/var/log/oozie'

oozie_server = config['clusterHostInfo']['oozie_server'][0]
oozie_port = config['configurations']['oozie-env']['oozie_port']
oozie_https_port = config['configurations']['oozie-env']['oozie_https_port']
oozie_user = config['configurations']['oozie-env']['oozie_user']
oozie_group = config['configurations']['oozie-env']['oozie_group']
oozie_principal = default('/configurations/oozie-env/oozie_principal',None)
oozie_keytab = default('/configurations/oozie-env/oozie_keytab',None)

if oozie_db_type is not None:
  if oozie_db_type == "mysql":
    jdbc_driver_name="com.mysql.jdbc.Driver"
    oozie_jdbc_url='jdbc:mysql://%s/%s' % (oozie_db_server,oozie_db_schema_name )
  elif oozie_db_type == "postgresql":
    jdbc_driver_name="org.postgresql.Driver"
  elif oozie_db_type == "oracle":
    jdbc_driver_name="oracle.jdbc.driver.OracleDriver"
  else:
    is_derbydb=true

tmp_dir='/tmp/oozie'
