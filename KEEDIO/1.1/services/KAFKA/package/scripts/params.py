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
from kazoo.client import KazooClient
from time import sleep

#exclude_packages=[]
config = Script.get_config()
zookeeper_server_hosts = str(default("/configurations/kafka-server-properties/zookeeper.connect",None))
kafka_broker_hosts = default("/clusterHostInfo/kafka_broker_hosts",[])
log_dirs = default("/configurations/kafka-server-properties/log.dirs","")

ganglia_server_hosts = default('/clusterHostInfo/ganglia_server_host', [])
kafka_conf = default("/configurations/kafka-server-properties",[])

has_ganglia_server = not len(ganglia_server_hosts) == 0
if has_ganglia_server:
  gmondServer = ganglia_server_hosts[0]
  jmxPort = default("/configurations/kafka-env/jmxPort","9999")
  gmondPort = default("/configurations/kafka-broker/kafka.ganglia.metrics.port", 8671)
#else:
#  exclude_packages.append('jmxtrans')
hostname = None
if config.has_key('hostname'):
  hostname = str(config['hostname'])

znode_kafka_path=default("/configurations/kafka-env/znode_path","/ambari/kafka")
kafka_id=None


zk = KazooClient(hosts=zookeeper_server_hosts)
zk.start()
Logger.error("Open kazoo client")
zk.ensure_path(znode_kafka_path)
tries=0
while tries < 10:
  Logger.error("Trying to adquire lock: %i" % tries)
  tries+=1
  try:
    zk.create(znode_kafka_path+'/lock',value=hostname,ephemeral=True,makepath=True)
    break
  except NodeExistsError:
    sleep(5)
    continue
if zk.exists(znode_kafka_path+'/brokers/'+hostname):
  kafka_id=zk.get(znode_kafka_path+'/brokers/'+hostname)[0]
else:
  kafka_id=str(zk.create(znode_kafka_path+'/ids/',sequence=True,value=hostname).rsplit('/',1)[1])
  zk.create(znode_kafka_path+'/brokers/'+hostname,value=kafka_id,makepath=True)
zk.stop()

