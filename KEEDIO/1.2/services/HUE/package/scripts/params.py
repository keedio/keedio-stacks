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
import os

config = Script.get_config()

hue_conf_dir = config['configurations']['hue-env']["hue_conf_dir"]

webserver_group = "apache"

ganglia_server_host = set(default("/clusterHostInfo/ganglia_server_host", []))
Ganglia_server_host = str(default("/clusterHostInfo/ganglia_server_host", ["none"])[0])

hostname = config["hostname"]
namenode_host = set(default("/clusterHostInfo/namenode_host", []))
namenode_list=list(namenode_host)

namenode_one_host=str(namenode_list[0])

security_enabled = config['configurations']['cluster-env']['security_enabled']

mysql_host=config['configurations']['hue-mysql']['mysql_host']
mysql_port=config['configurations']['hue-mysql']['mysql_port']
mysql_name=config['configurations']['hue-mysql']['mysql_name']
mysql_user=config['configurations']['hue-mysql']['mysql_user']
mysql_password=config['configurations']['hue-mysql']['mysql_password']

brokers_path=config['configurations']['hue-kafka']['brokers_path']
consumers_path=config['configurations']['hue-kafka']['consumers_path']
ganglia_data_source=config['configurations']['hue-kafka']['ganglia_data_source']

zk_port=config['configurations']['zoo.cfg']['clientPort']
zk_hosts=set(default("/clusterHostInfo/zookeeper_hosts", []))
zk_rest_url="http://ambari1.ambari.keedio.org:9998"
zk_host_ports=""
for host in zk_hosts:
    zk_host_ports+=host+":"+str(zk_port)


storm_ui_port=default("/configurations/storm-site/ui.port", "9744")
storm_ui_hosts=str(default("/clusterHostInfo/storm_ui_server_hosts", ["none"])[0])

print "Alessiiooooo"
print config['configurations']
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
jtnode_host = set(default("/clusterHostInfo/jtnode_host", []))
JTnode_host = str(default("/clusterHostInfo/jtnode_host", ["none"])[0])
Oozie_host = str(default("/clusterHostInfo/oozie_server", ["none"])[0]) 
rm_host = set(default("/clusterHostInfo/rm_host", []))
RM_host= str(default("/clusterHostInfo/rm_host", ["none"])[0])

hs_host = set(default("/clusterHostInfo/hs_host", []))
hbase_master_hosts = set(default("/clusterHostInfo/hbase_master_hosts", []))
datanodes_hosts = set(default("/clusterHostInfo/slave_hosts", []))
tt_hosts = set(default("/clusterHostInfo/mapred_tt_hosts", []))
nm_hosts = set(default("/clusterHostInfo/nm_hosts", []))
hbase_rs_hosts = set(default("/clusterHostInfo/hbase_rs_hosts", []))
flume_hosts = set(default("/clusterHostInfo/flume_hosts", []))
jn_hosts = set(default("/clusterHostInfo/journalnode_hosts", []))
nimbus_server_hosts = set(default("/clusterHostInfo/nimbus_hosts", []))
storm_ui_server_hosts = str(default("/clusterHostInfo/storm_ui_server_hosts", []))
hue_server_host = str(default("/clusterHostInfo/nimbus_hosts", []))
supervisor_server_hosts = set(default("/clusterHostInfo/supervisor_hosts", []))
kafka_broker_hosts =  set(default("/clusterHostInfo/kafka_broker_hosts", []))
kafka_ganglia_port = default("/configurations/kafka-broker/kafka.ganglia.metrics.port", 8671)

pure_slave = not hostname in (namenode_host | jtnode_host | rm_host | hs_host | \
                              hbase_master_hosts | datanodes_hosts | tt_hosts | hbase_rs_hosts | \
                              flume_hosts | nm_hosts | jn_hosts | nimbus_server_hosts | \
                              supervisor_server_hosts)
is_ganglia_server_host = (hostname == ganglia_server_host)

has_namenodes = not len(namenode_host) == 0
has_jobtracker = not len(jtnode_host) == 0
has_resourcemanager = not len(rm_host) == 0
has_historyserver = not len(hs_host) == 0
has_hbase_masters = not len(hbase_master_hosts) == 0
has_datanodes = not len(datanodes_hosts) == 0
has_tasktracker = not len(tt_hosts) == 0
has_nodemanager = not len(nm_hosts) == 0
has_hbase_rs = not len(hbase_rs_hosts) == 0
has_flume = not len(flume_hosts) == 0
has_journalnode = not len(jn_hosts) == 0
has_nimbus_server = not len(nimbus_server_hosts) == 0
has_supervisor_server = not len(supervisor_server_hosts) == 0
has_kafka_broker = not len(kafka_broker_hosts) == 0

