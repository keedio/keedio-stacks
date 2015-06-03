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
import itertools
import os

# server configurations
config = Script.get_config()

ambari_server_hostname = config['clusterHostInfo']['ambari_server_host'][0]
security_enabled = config['configurations']['cluster-env']['security_enabled']

oozie_db_type = config['configurations']['oozie-site']['oozie.db.type']
oozie_schema_name = config['configurations']['oozie-site']['oozie.schema.name']
oozie_jdbc_url = config['configurations']['oozie-site']['oozie.service.JPAService.jdbc.url']
oozie_db_user = config['configurations']['oozie-site']['oozie.service.JPAService.jdbc.username']
oozie_db_pass = config['configurations']['oozie-site']['oozie.service.JPAService.jdbc.password']

oozie_data_path = '/var/lib/oozie' 
oozie_catalina_home = '/usr/lib/tomcatserver'
oozie_config_dir = '/etc/oozie/conf'
oozie_log_dir = '/var/log/oozie'

oozie_port = config['configurations']['oozie-env']['oozie_port']
oozie_https_port = config['configurations']['oozie-env']['oozie_https_port']
oozie_user = config['configurations']['oozie_env']['oozie_user']
oozie_group = config['configurations']['oozie_env']['oozie_group']


if oozie_db_type == "mysql":
  jdbc_driver_name="com.mysql.jdbc.Driver"
elif oozie_db_type == "postgresql":
  jdbc_driver_name="org.postgresql.Driver"
elif oozie_db_type == "oracle":
  jdbc_driver_name="oracle.jdbc.driver.OracleDriver"
else:
  is_derbydb=true
