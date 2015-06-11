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

kerberos_cache_file = config['configurations']['cluster-env']['kerberos_cache_file']

spark_user = config['configurations']['spark']['spark_user']
spark_group = config['configurations']['spark']['spark_group']
spark_hdfs_home = config['configurations']['spark']['spark_hdfs_home']
spark_local_home = config['configurations']['spark']['spark_local_home']
spark_principal = default('/configurations/spark/spark_principal',None)
spark_keytab = default('/configurations/spark/spark_keytab',None)

hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hdfs_principal_name = default('/configurations/hadoop-env/hdfs_principal_name',None)
hdfs_user_keytab = default('/configurations/hadoop-site/hdfs_user_keytab',None)

spark_conf_dir = config['configurations']['spark']['spark_conf_dir']
spark_assembly = config['configurations']['spark']['spark_assembly']
spark_examples_jar = config['configurations']['spark']['spark_examples_jar']
