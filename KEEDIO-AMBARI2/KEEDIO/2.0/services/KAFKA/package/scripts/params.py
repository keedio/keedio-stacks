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

#from resource_management.libraries.functions.version import format_hdp_stack_version, compare_versions
from resource_management import *
from kazoo.client import KazooClient
from time import sleep
import kazoo

#exclude_packages=[]
config = Script.get_config()
zookeeper_server_hosts = str(default("/configurations/kafka-broker/zookeeper.connect",None))
kafka_broker_hosts = default("/clusterHostInfo/kafka_broker_hosts",[])
log_dirs = default("/configurations/kafka-broker/log.dirs","")

ganglia_server_hosts = default('/clusterHostInfo/gangliaui_server_hosts', [])
kafka_conf = default("/configurations/kafka-broker",[])
kafka_topic_conf = default("/configurations/kafka-topic-properties",[])

has_ganglia_server = not len(ganglia_server_hosts) == 0
if has_ganglia_server:
  gmondServer = ganglia_server_hosts[0]
  jmxPort = default("/configurations/kafka-env/jmxPort","19999")
  gmondPort = default("/configurations/kafka-broker/kafka.ganglia.metrics.port", 8671)
else:
  jmxPort = "19999"

metric_collector_port = ""
metric_collector_protocol = ""
metric_truststore_path= default("/configurations/ams-ssl-client/ssl.client.truststore.location", "")
metric_truststore_type= default("/configurations/ams-ssl-client/ssl.client.truststore.type", "")
metric_truststore_password= default("/configurations/ams-ssl-client/ssl.client.truststore.password", "")

ams_collector_hosts = ",".join(default("/clusterHostInfo/metrics_collector_hosts", []))
has_metric_collector = not len(ams_collector_hosts) == 0

if has_metric_collector:
  if 'cluster-env' in config['configurations'] and \
      'metrics_collector_vip_port' in config['configurations']['cluster-env']:
    metric_collector_port = config['configurations']['cluster-env']['metrics_collector_vip_port']
  else:
    metric_collector_web_address = default("/configurations/ams-site/timeline.metrics.service.webapp.address", "0.0.0.0:6188")
    if metric_collector_web_address.find(':') != -1:
      metric_collector_port = metric_collector_web_address.split(':')[1]
    else:
      metric_collector_port = '6188'
  if default("/configurations/ams-site/timeline.metrics.service.http.policy", "HTTP_ONLY") == "HTTPS_ONLY":
    metric_collector_protocol = 'https'
  else:
    metric_collector_protocol = 'http'
  pass
#else:
#  exclude_packages.append('jmxtrans')
hostname = None
if config.has_key('hostname'):
  hostname = str(config['hostname'])

znode_kafka_path=str(default("/configurations/kafka-env/znode_path","/ambari/kafka"))
kafka_id=None
Logger.info("PROVAAA"+zookeeper_server_hosts)
zk = KazooClient(hosts=zookeeper_server_hosts)
zk.start()

lock = zk.Lock("/kafka-lock", hostname)
lock.acquire(timeout=60)

if zk.exists(znode_kafka_path+'/brokers/'+hostname):
  kafka_id=int(zk.get(znode_kafka_path+'/brokers/'+hostname)[0])
else:
  kafka_id=int(zk.create(znode_kafka_path+'/ids/',sequence=True,value=hostname,makepath=True).rsplit('/',1)[1])
  zk.create(znode_kafka_path+'/brokers/'+hostname,value=str(kafka_id),makepath=True)
lock.release()
zk.stop()


