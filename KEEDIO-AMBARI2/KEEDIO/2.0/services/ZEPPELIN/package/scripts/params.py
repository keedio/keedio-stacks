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
zeppelin_port = int(default('/configurations/main-zeppelin/zeppelin_port',8044))
zeppelin_ssl_port = int(default('/configurations/main-zeppelin/zeppelin_ssl_port',8043))
zeppelin_ssl = str(default('/configurations/main-zeppelin/zeppelin.ssl','false')).lower()
zeppelin_notebook_dir = str(default('/configurations/main/zeppelin_notebook_dir','notebook'))
authentication = str(default('/configurations/main/authentication','internal'))
kerberos_domain = default('/configurations/cluster-env/kerberos_domain',None)
kerberos_cache_file = default('/configurations/cluster-env/kerberos_cache_file','/tmp/ccache_keytab')
security_enabled = config['configurations']['cluster-env']['security_enabled']

hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hdfs_principal_name = default('/configurations/hadoop-env/hdfs_principal_name',None)
hdfs_user_keytab = default('/configurations/hadoop-env/hdfs_user_keytab',None)
livy_server=default("/clusterHostInfo/livy_server_host", ["localhost"])[0]
livy_port=str(default('/configurations/livy/livy_port',8998))
ldap_server=str(default('/configurations/ldap/ldap_server','master.ambari.keedio.org'))
ldap_basename=str(default('/configurations/ldap/basename','master.ambari.keedio.org'))
ldap_userdntemplate=str(default('/configurations/ldap/userdntemplate','master.ambari.keedio.org'))
ipa_server_host = default('/clusterHostInfo/ipa_server_hosts',[])
print ipa_server_host
has_ipa = not len(ipa_server_host) == 0
ipa_server='none'
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
       anonymous = False 
    else: 
       print('FreeIPA service not available, reverting authentication to  disabled') 
       use_internal_freeipa = False  
       use_authentication = False
       use_active_directory = False 
       use_external_ldap = False
       anonymous = True

elif authentication == 'ldap':
    use_internal_freeipa = False 
    use_active_directory = False 
    use_external_ldap = True
    use_authentication = True  
    anonymous = False 
elif authentication == 'ad':
    use_internal_freeipa = False 
    use_active_directory = True 
    use_external_ldap = False
    use_authentication = True 
    anonymous = False 
else:
    use_internal_freeipa = False 
    use_authentication = False 
    anonymous = True 

hostname = config['hostname']

