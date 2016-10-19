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
from resource_management.core.system import System
import os,random,string

config = Script.get_config()
secret_key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))

hue_conf_dir = config['configurations']['hue-env']["hue_conf_dir"]
hue_principal = default('/configurations/hue-ldap/hue_principal_name',None)
hue_keytab = default('/configurations/hue-ldap/hue_keytab',None)
timezone = default('/configurations/hue-env/timezone','Europe/Madrid')

webserver_group = "apache"

ganglia_server_host = set(default("/clusterHostInfo/ganglia_server_host", []))
Ganglia_server_host = str(default("/clusterHostInfo/ganglia_server_host", ["none"])[0])

hostname = config["hostname"]
namenode_host = set(default("/clusterHostInfo/namenode_host", []))
namenode_list=list(namenode_host)
namenode_one_host=str(namenode_list[0])

yarn_ha=default('/configurations/yarn-site/yarn.resourcemanager.ha.enabled',False)
resourcemanagers=[]
if yarn_ha:
  yarn_logical_name=config['configurations']['yarn-site']['yarn.resourcemanager.cluster-id']
  rm_ids=set(config['clusterHostInfo']['rm_host'])
  for rm_id in rm_ids:
    resourcemanagers.append(str(rm_id)+":8088")
    #resourcemanagers.append(str(config['configurations']['yarn-site']['yarn.resourcemanager.'+str(rm_id)+'.webapp.address']))
else:
  resourcemanagers.append(str(config['configurations']['yarn-site']['yarn.resourcemanager.webapp.address']))
  #resourcemanager_address=str(config['configurations']['yarn-site']['yarn.resourcemanager.address']).split(':')[1]
  #resourcemanager_web_port=str(config['configurations']['yarn-site']['yarn.resourcemanager.webapp.address']).split(':')[1]
hs_address = str(config['configurations']['mapred-site']['mapreduce.jobhistory.webapp.address'])

httpfs_port = str(default("/configurations/httpfs-env/httpf_port",14000))
fs_defaultsfs = str(config['configurations']['core-site']['fs.defaultFS'])

security_enabled = config['configurations']['cluster-env']['security_enabled']

db_type=config['configurations']['hue-database']['db_type']
db_host=config['configurations']['hue-database']['db_host']
db_port_config=config['configurations']['hue-database']['db_port']
db_port='3306'
db_name=config['configurations']['hue-database']['db_name']
db_user=config['configurations']['hue-database']['db_user']
db_password=config['configurations']['hue-database']['db_password']
oracle_home=config['configurations']['hue-database']['oracle_home']

if db_port_config == 'default':
#setting default port value
     if db_type == 'mysql':
        db_port='3306'
     if db_type == 'postgresql_psycopg2':
        db_port='5432'
     if db_type == 'oracle':
        db_port='1521'
else:
     try:
           int(db_port_config)
     except:
           Logger.info('db_port must be either a number or default')
           raise Fail(stderr)
     db_port=db_port_config  

brokers_path=config['configurations']['hue-kafka']['brokers_path']
consumers_path=config['configurations']['hue-kafka']['consumers_path']
ganglia_data_source=config['configurations']['hue-kafka']['ganglia_data_source']

zk_port=config['configurations']['zoo.cfg']['clientPort']
zk_hosts=set(default("/clusterHostInfo/zookeeper_hosts", []))
zk_rest_hosts=default("/clusterHostInfo/zookeeper_rest_hosts", ["none"])
zk_rest_port=config['configurations']['rest-env']['rest_port']
zk_rest_url="http://"+str(zk_rest_hosts[0])+":"+str(zk_rest_port)
zk_host_ports=""
for host in zk_hosts:
    if zk_host_ports != "":
       zk_host_ports += ","
    zk_host_ports+=host+":"+str(zk_port)


storm_ui_port=default("/configurations/storm-site/ui.port", "9744")
storm_ui_hosts=str(default("/clusterHostInfo/storm_ui_server_hosts", ["none"])[0])

use_ldap=config['configurations']['hue-ldap']['use_ldap']
ldap_base_dn=config['configurations']['hue-ldap']['base_dn']
ldap_url=config['configurations']['hue-ldap']['ldap_url']
ipa_cert=config['configurations']['hue-ldap']['ipa_cert']
use_bind=config['configurations']['hue-ldap']['use_bind']
use_start_tls=config['configurations']['hue-ldap']['use_start_tls']
ldap_bind_dn=config['configurations']['hue-ldap']['ldap_bind_dn']
ldap_bind_password=config['configurations']['hue-ldap']['ldap_bind_password']
ldap_company=config['configurations']['hue-ldap']['ldap_company']
ldap_username_pattern=config['configurations']['hue-ldap']['ldap_username_pattern']
create_users_on_login=config['configurations']['hue-ldap']['create_users_on_login']
user_filter=config['configurations']['hue-ldap']['user_filter']
user_name_attr=config['configurations']['hue-ldap']['user_name_attr']
group_filter=config['configurations']['hue-ldap']['group_filter']
group_name_attr=config['configurations']['hue-ldap']['group_name_attr']
group_member_attr=config['configurations']['hue-ldap']['group_member_attr']

if security_enabled:
    secure='true'
else:
    secure='false'

ambari_server_host = str(default("/clusterHostInfo/ambari_server_host", ["none"])[0])
Oozie_host = str(default("/clusterHostInfo/oozie_server", ["none"])[0]) 
oozie_port = str(default("configurations/oozie-env/oozie_port",11000))
#rm_host = set(default("/clusterHostInfo/rm_host", []))
#RM_host= str(default("/clusterHostInfo/rm_host", ["none"])[0])

#hs_host = set(default("/clusterHostInfo/hs_host", []))
hbase_master_hosts = set(default("/clusterHostInfo/hbase_master_hosts", []))
storm_ui_server_hosts = str(default("/clusterHostInfo/storm_ui_server_hosts", []))
hue_port = str(default('/configurations/hue-env/hue_port',8888))
kafka_broker_hosts =  set(default("/clusterHostInfo/kafka_broker_hosts", []))
kafka_ganglia_port = default("/configurations/kafka-broker/kafka.ganglia.metrics.port", 8671)

has_namenodes = not len(namenode_host) == 0
has_resourcemanager = not len(resourcemanagers) == 0
has_hbase_masters = not len(hbase_master_hosts) == 0
has_kafka_broker = not len(kafka_broker_hosts) == 0

