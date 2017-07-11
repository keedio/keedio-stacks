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

#from resource_management.libraries.functions.version import format_hdp_stack_version, compare_versions
from resource_management import *
from ambari_commons.ambari_metrics_helper import select_metric_collector_hosts_from_hostnames
import status_params

# server configurations
config = Script.get_config()

storm_user = config['configurations']['storm-env']['storm_user']
conf_dir = "/etc/storm/conf"
storm_lib_dir = "/usr/lib/storm/lib"
storm_local_dir = config['configurations']['storm-site']['storm.local.dir']
storm_log_dir = "/var/log/storm"
user_group = config['configurations']['cluster-env']['user_group']

nimbus_port = config['configurations']['storm-site']['nimbus.thrift.port']
nimbus_host = config['configurations']['storm-site']['nimbus.host']

storm_env_sh_template = config['configurations']['storm-env']['content']

hostname = config['hostname']
is_nimbus_server = hostname in config['clusterHostInfo']['nimbus_hosts']
is_supervisor_server = hostname in config['clusterHostInfo']['supervisor_hosts']
is_drpc_server = hostname in config['clusterHostInfo']['drpc_server_hosts']
is_storm_ui_server = hostname in config['clusterHostInfo']['storm_ui_server_hosts']

nimbus_server = config['clusterHostInfo']['nimbus_hosts'][0]
zookeeper_hosts = config['clusterHostInfo']['zookeeper_hosts']
drpc_hosts = default("/clusterHostInfo/drpc_server_hosts",[])
has_drpc_hosts = drpc_hosts != []

ganglia_server_hosts = default('/clusterHostInfo/gangliaui_server_hosts', [])
has_ganglia_server = not len(ganglia_server_hosts) == 0
if has_ganglia_server:
  gmondServer = ganglia_server_hosts[0]
  nimbusjmxPort = default("/configurations/storm-site/jmxPort","12345")
  supervisorjmxPort = default("/configurations/storm-site/jmxPort","56431")
  nimbusGmondPort = default("/configurations/storm-site/nimbus.ganglia.metrics.port", 8663)
  supervisorGmondPort = default("/configurations/storm-site/supervisor.ganglia.metrics.port", 8664)

exclude_packages=[]
if not is_nimbus_server:
  exclude_packages += ['storm-nimbus']
if not is_supervisor_server:
  exclude_packages += ['storm-supervisor','storm-logviewer']
if not is_drpc_server:
  exclude_packages += ['storm-drpc']
if not is_storm_ui_server:
  exclude_packages += ['storm-ui']
ams_collector_hosts = ",".join(default("/clusterHostInfo/metrics_collector_hosts", []))
has_metric_collector = not len(ams_collector_hosts) == 0
metric_collector_port = None
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

  metric_collector_report_interval = 60
  metric_collector_app_id = "nimbus"
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
metric_collector_sink_jar = "/usr/lib/storm/lib/ambari-metrics-storm-sink-with-common-*.jar"
metric_collector_legacy_sink_jar = "/usr/lib/storm/lib/ambari-metrics-storm-sink-legacy-with-common-*.jar"
sink_jar="ambari-metrics-storm-sink.jar"

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


