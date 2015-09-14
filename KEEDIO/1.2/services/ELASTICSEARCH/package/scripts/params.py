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
es_port = default('/configurations/elasticsearch/service_port',9200)
es_master_hosts = [ str(elem) for elem in config['clusterHostInfo']['elasticsearch_hosts']]
es_indexer_hosts = [ str(elem) for elem in default('/clusterHostInfo/elasticsearch_indexer_hosts',[]) ]
kibana3_host = default('/clusterHostInfo/kibana3_hosts',[])
kibana4_host = default('/clusterHostInfo/kibana4_hosts',[])
hostname = config['hostname']

is_es_master = hostname in es_master_hosts
is_es_master_str = str(hostname in es_master_hosts).lower()
is_es_indexer = hostname in es_indexer_hosts
is_es_indexer_str = str(hostname in es_indexer_hosts).lower()
is_kibana3 = hostname in kibana3_host
is_kibana4 = hostname in kibana4_host
allocated_mem = config['configurations']['elasticsearch']['allocated.memory']

path_data = config['configurations']['elasticsearch']['path.data']

#min_required_hosts = len(set(es_master_hosts + es_indexer_hosts + kibana3_host + kibana4_host))/2+1
min_required_hosts = len(set(es_master_hosts))/2+1

exclude_packages = []
if not is_kibana3:
  exclude_packages += ['kibana','httpd','rubygems','mod_passenger']
if not is_kibana4:
  exclude_packages += ['kibana4']
