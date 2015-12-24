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
import socket,multiprocessing

#exclude_packages=[]
config = Script.get_config()
hostname = None
if config.has_key('hostname'):
  hostname = str(config['hostname'])
cluster_name=str(config['clusterName'])


all_hosts =set(default("/clusterHostInfo/all_hosts",[]))
zookeeper_server_hosts = set(default("/clusterHostInfo/zookeeper_hosts",[]))
Logger.info("jcfernandez: " + str(zookeeper_server_hosts))
namenode_host = set(default("/clusterHostInfo/namenode_host", []))
jtnode_host = set(default("/clusterHostInfo/jtnode_host", []))
rm_host = set(default("/clusterHostInfo/rm_host", []))
hs_host = set(default("/clusterHostInfo/hs_host", []))
hbase_master_hosts = set(default("/clusterHostInfo/hbase_master_hosts", []))
datanodes_hosts = set(default("/clusterHostInfo/slave_hosts", []))
tt_hosts = set(default("/clusterHostInfo/mapred_tt_hosts", []))
nm_hosts = set(default("/clusterHostInfo/nm_hosts", []))
hbase_rs_hosts = set(default("/clusterHostInfo/hbase_rs_hosts", []))
flume_hosts = set(default("/clusterHostInfo/flume_hosts", []))
jn_hosts = set(default("/clusterHostInfo/journalnode_hosts", []))
nimbus_server_hosts = set(default("/clusterHostInfo/nimbus_hosts", []))
supervisor_server_hosts = set(default("/clusterHostInfo/supervisor_hosts", []))
kafka_broker_hosts =  set(default("/clusterHostInfo/kafka_broker_hosts", []))
es_master_hosts =  str(default("/clusterHostInfo/elasticsearch_hosts", ['none']))
oozie_server_hosts = set(default('/clusterHostInfo/oozie_server',[]))
nagios_server_host = str(config['clusterHostInfo']['nagios_server_hosts'])

has_namenodes = not len(namenode_host) == 0
has_zookeeper = not len(zookeeper_server_hosts) == 0
has_jobtracker = not len(jtnode_host) == 0
has_resourcemanager = not len(rm_host) == 0
has_historyserver = not len(hs_host) == 0
has_hbase = not len(hbase_master_hosts) == 0
has_datanodes = not len(datanodes_hosts) == 0
has_tasktracker = not len(tt_hosts) == 0
has_nodemanager = not len(nm_hosts) == 0
#has_hbase_rs = not len(hbase_rs_hosts) == 0
has_flume = not len(flume_hosts) == 0
has_journalnode = not len(jn_hosts) == 0
has_storm = not len(nimbus_server_hosts) == 0
#has_supervisor_server = not len(supervisor_server_hosts) == 0
has_kafka = not len(kafka_broker_hosts) == 0
has_oozie = not len(oozie_server_hosts) == 0
if 'none' in es_master_hosts: 
    has_elasticsearch = False
else:
    has_elasticsearch = True
host_list=dict()
for host in all_hosts:
  ip = socket.gethostbyname(str(host))
  host_list[str(host)]={'groups':[],'ip':ip}

for nn in namenode_host:
  host_list[nn]['groups'].append("namenodes")
for zk in zookeeper_server_hosts:
  host_list[zk]['groups'].append('zookeeperservers')
for hbase in hbase_master_hosts:
  host_list[hbase]['groups'].append("hbasemasters")
for rm in rm_host:
  host_list[rm]['groups'].append("resourcemanager")
for hs in hs_host:
  host_list[hs]['groups'].append("historyservers")
for dn in datanodes_hosts:
  host_list[dn]['groups'].append("datanodes")
for hbase_rs in hbase_rs_hosts:
  host_list[hbase_rs]['groups'].append("hbasers")
for nimbus in nimbus_server_hosts:
  host_list[nimbus]['groups'].append("nimbuservers")
for kb in kafka_broker_hosts:
  host_list[kb]['groups'].append("kafkaservers")
for jn in jn_hosts:
  host_list[jn]['groups'].append("journalnodes")
for oozie in oozie_server_hosts:
  host_list[oozie]['groups'].append('oozieservers')


cpus=multiprocessing.cpu_count()
#for es in elasticsearch_server:
#  clusters.append("esserver")
#for flume in flume_hosts:
#  host_list[flume]['groups'].append("FlumeServer")
#for nm in nm_hosts:
#  host_list[nm]['groups'].append("NodeManager")
#for supervisor in supervisor_server_hosts:
#  host_list[supervisor]['groups'].append("Supervisor")

security_enabled = config['configurations']['cluster-env']['security_enabled']
if has_namenodes:
  data_path_nn = set(config['configurations']['hdfs-site']['dfs.namenode.name.dir'])
  data_path_dn = set(config['configurations']['hdfs-site']['dfs.datanode.data.dir'])
  data_path = data_path_nn.union(data_path_dn)

  dfs_ha_enabled  = False
  dfs_ha_nameservices = default("/configurations/hdfs-site/dfs.nameservices", None)
  dfs_ha_namenode_ids = default(format("/configurations/hdfs-site/dfs.ha.namenodes.{dfs_ha_nameservices}"), None)

  namenode_id = None
  namenode_rpc = None

  if dfs_ha_namenode_ids:
    dfs_ha_namemodes_ids_list = dfs_ha_namenode_ids.split(",")
    dfs_ha_namenode_ids_array_len = len(dfs_ha_namemodes_ids_list)
    if dfs_ha_namenode_ids_array_len > 1:
      dfs_ha_enabled = True

if has_zookeeper:
  zk_port = str(config['configurations']['zoo.cfg']['clientPort'])
  zookeeper_connection_list=""
  for zk in zookeeper_server_hosts:
    if zookeeper_connection_list != "":
      zookeeper_connection_list += ","
    zookeeper_connection_list+=host+":"+zk_port

if has_oozie:
  oozie_port=str(config['configurations']['oozie-env']['oozie_port'])
