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
from ambari_commons.ambari_metrics_helper import select_metric_collector_hosts_from_hostnames

config = Script.get_config()

user_group = config['configurations']['cluster-env']['user_group']
proxyuser_group =  config['configurations']['hadoop-env']['proxyuser_group']

security_enabled = False

#hdp_stack_version = str(config['hostLevelParams']['stack_version'])
#:x
#hdp_stack_version = format_hdp_stack_version(hdp_stack_version)
#stack_is_hdp22_or_further = hdp_stack_version != "" and compare_versions(hdp_stack_version, '2.2') >= 0

#hadoop params
#if stack_is_hdp22_or_further:
#  flume_bin = '/usr/hdp/current/flume-server/bin/flume-ng'
#  flume_hive_home = '/usr/hdp/current/hive-metastore'
#  flume_hcat_home = '/usr/hdp/current/hive-webhcat'
#else:
#  flume_bin = '/usr/bin/flume-ng'
#  flume_hive_home = '/usr/lib/hive'
#  flume_hcat_home = '/usr/lib/hive-hcatalog'

flume_conf_dir = '/etc/flume/conf'
flume_agent_conf_dir = '/etc/flume/conf.d'
java_home = config['hostLevelParams']['java_home']
flume_log_dir = '/var/log/flume'
flume_run_dir = '/var/run/flume'
flume_user = 'flume'
flume_group = 'flume'
flume_extra = None

if 'flume-user' in config['configurations'] and 'flume_user' in config['configurations']['flume-env']:
  flume_user = config['configurations']['flume-env']['flume_user']

if 'flume-conf' in config['configurations'] and 'content' in config['configurations']['flume-conf']:
  flume_conf_content = config['configurations']['flume-conf']['content']
else:
  flume_conf_content = None

if 'flume-log4j' in config['configurations'] and 'content' in config['configurations']['flume-log4j']:
  flume_log4j_content = config['configurations']['flume-log4j']['content']
else:
  flume_log4j_content = None

if 'flume-env' in config['configurations'] and 'content' in config['configurations']['flume-env']:
  flume_env_content = config['configurations']['flume-env']['content']
else:
  flume_env_content = None
if 'flume-extra' in config['configurations']:
  flume_extra = config['configurations']['flume-extra']

targets = default('/commandParams/flume_handler', None)
flume_command_targets = [] if targets is None else targets.split(',')


ganglia_server_hosts = default('/clusterHostInfo/gangliaui_server_hosts', [])
has_ganglia_server = not len(ganglia_server_hosts) == 0
if has_ganglia_server:
  ganglia_server_host = ganglia_server_hosts[0]

hostname = None
if config.has_key('hostname'):
  hostname = config['hostname']

set_instanceId = "false"
cluster_name = config["clusterName"]

if 'cluster-env' in config['configurations'] and \
        'metrics_collector_external_hosts' in config['configurations']['cluster-env']:
  ams_collector_hosts = config['configurations']['cluster-env']['metrics_collector_external_hosts']
  set_instanceId = "true"
else:
  ams_collector_hosts = ",".join(default("/clusterHostInfo/metrics_collector_hosts", []))

has_metric_collector = not len(ams_collector_hosts) == 0
metric_collector_port = None
if has_metric_collector:
  metric_collector_host = select_metric_collector_hosts_from_hostnames(ams_collector_hosts)
  if 'cluster-env' in config['configurations'] and \
      'metrics_collector_external_port' in config['configurations']['cluster-env']:
    metric_collector_port = config['configurations']['cluster-env']['metrics_collector_external_port']
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
  metric_truststore_path= default("/configurations/ams-ssl-client/ssl.client.truststore.location", "")
  metric_truststore_type= default("/configurations/ams-ssl-client/ssl.client.truststore.type", "")
  metric_truststore_password= default("/configurations/ams-ssl-client/ssl.client.truststore.password", "")
  pass
metrics_report_interval = default("/configurations/ams-site/timeline.metrics.sink.report.interval", 60)
metrics_collection_period = default("/configurations/ams-site/timeline.metrics.sink.collection.period", 10)

# Cluster Zookeeper quorum
zookeeper_quorum = None
if not len(default("/clusterHostInfo/zookeeper_hosts", [])) == 0:
  if 'zoo.cfg' in config['configurations'] and 'clientPort' in config['configurations']['zoo.cfg']:
    zookeeper_clientPort = config['configurations']['zoo.cfg']['clientPort']
  else:
    zookeeper_clientPort = '2181'
  zookeeper_quorum = (':' + zookeeper_clientPort + ',').join(config['clusterHostInfo']['zookeeper_hosts'])
  # last port config
  zookeeper_quorum += ':' + zookeeper_clientPort

