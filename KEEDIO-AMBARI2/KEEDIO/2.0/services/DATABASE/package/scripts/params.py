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
username = str(default('/configurations/database/username','root'))
password = str(default('/configurations/database/password','root'))
#cb_clustercreator_host = [ str(elem) for elem in config['clusterHostInfo']['couchbase_clustercreator_hosts']]
#cb_server_hosts = [ str(elem) for elem in config['clusterHostInfo']['couchbase_server_hosts']]
#cb_data_hosts = [ str(elem) for elem in default('/clusterHostInfo/couchbase_data_hosts',[]) ]
#cb_index_hosts = [ str(elem) for elem in default('/clusterHostInfo/couchbase_indexer_hosts',[]) ]
#cb_query_hosts = [ str(elem) for elem in default('/clusterHostInfo/couchbase_query_hosts',[]) ]
#creator=cb_clustercreator_host[0]
hue_server_host = default("/clusterHostInfo/hue_hosts", [])
has_hue = not len(hue_server_host) == 0
hostname = config['hostname']

hue_db_name=str(default('/configurations/hue-database/db_name','hue'))
hue_db_username=str(default('/configurations/hue-database/db_user','hue'))
hue_db_password=str(default('/configurations/hue-database/db_password','hue'))


oozie_server_host = default('/clusterHostInfo/oozie_server',[])
has_oozie = not len(oozie_server_host) == 0
if has_oozie:
	oozie_database = default('/configurations/oozie-site/oozie_database',None)
	oozie_db_schema_name = config['configurations']['oozie-site']['oozie.db.schema.name']
	oozie_db_server = oozie_server_host
	oozie_jdbc_url = config['configurations']['oozie-site']['oozie.service.JPAService.jdbc.url']
	oozie_jdbc_driver = config['configurations']['oozie-site']['oozie.service.JPAService.jdbc.driver']
	oozie_db_user = config['configurations']['oozie-site']['oozie.service.JPAService.jdbc.username']
	oozie_db_pass = config['configurations']['oozie-site']['oozie.service.JPAService.jdbc.password']

