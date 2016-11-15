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
username = str(default('/configurations/couchbase/username','admin'))
password = str(default('/configurations/couchbase/password','cbadmin'))
datadir = str(default('/configurations/couchbase/datadir','/couchbase/data'))
indexdir = str(default('/configurations/couchbase/indexdir','/couchbase/index'))
dataram = str(default('/configurations/couchbase/dataram','1000'))
indexram = str(default('/configurations/couchbase/indexram','1000'))
cb_clustercreator_host = [ str(elem) for elem in config['clusterHostInfo']['couchbase_clustercreator_hosts']]
cb_server_hosts = [ str(elem) for elem in config['clusterHostInfo']['couchbase_server_hosts']]
cb_data_hosts = [ str(elem) for elem in default('/clusterHostInfo/couchbase_data_hosts',[]) ]
cb_index_hosts = [ str(elem) for elem in default('/clusterHostInfo/couchbase_indexer_hosts',[]) ]
cb_query_hosts = [ str(elem) for elem in default('/clusterHostInfo/couchbase_query_hosts',[]) ]
creator=cb_clustercreator_host[0]
hostname = config['hostname']

is_cb_creator = hostname in cb_clustercreator_host
is_cb_datanode = hostname in cb_data_hosts
is_cb_indexnode = hostname in cb_index_hosts
is_cb_querynode = hostname in cb_query_hosts
