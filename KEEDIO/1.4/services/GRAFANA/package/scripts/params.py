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
grafana_port = int(default('/configurations/grafana/grafana_port',3000))
es_port = int(default('/configurations/elasticsearch/es_port',9200))
authentication = str(default('/configurations/grafana/authentication','internal'))
es_master_hosts = [ str(elem) for elem in config['clusterHostInfo']['elasticsearch_hosts']]
es_indexer_hosts = [ str(elem) for elem in default('/clusterHostInfo/elasticsearch_indexer_hosts',[]) ]
#ldap_server=str(default('/configurations/ldap/ldap_server','master.ambari.keedio.org'))
#ldap_basename=str(default('/configurations/ldap/basename','master.ambari.keedio.org'))
#ldap_userdntemplate=str(default('/configurations/ldap/userdntemplate','master.ambari.keedio.org'))
ipa_server_host = default('/clusterHostInfo/ipa_server_hosts',[])
print ipa_server_host
has_ipa = not len(ipa_server_host) == 0
ipa_server='localhost'
if has_ipa:
   ipa_server=str(ipa_server_host[0])
   print ipa_server
ipa_realm = str(default('/configurations/freeipa/realm','none'))
ipastring =ipa_realm.split('.')
print ipastring
ldapstring=''
for string in ipastring:
   ldapstring=ldapstring+"dc="+string+',' 
#remove last ','
ldapstring=ldapstring[:-1]

if authentication == 'internal':
    if has_ipa:
       use_internal_freeipa = True  
       use_authentication = True  
       use_active_directory = False 
       use_external_ldap = False
    else: 
       print('FreeIPA service not available, reverting authentication to  disabled')
       use_internal_freeipa = False
       use_authentication = False
       use_active_directory = False
       use_external_ldap = False 
elif authentication == 'manual':
    use_internal_freeipa = False  
    use_authentication = True  
    use_active_directory = False 
    use_external_ldap = False
    
else:
    use_internal_freeipa = False 
    use_authentication = False 
hostname = config['hostname']

is_es_master = hostname in es_master_hosts
is_es_master_str = str(hostname in es_master_hosts).lower()
is_es_indexer = hostname in es_indexer_hosts
is_es_indexer_str = str(hostname in es_indexer_hosts).lower()
