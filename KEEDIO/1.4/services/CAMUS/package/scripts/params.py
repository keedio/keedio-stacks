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

from resource_management.libraries.functions.version import format_hdp_stack_version, compare_versions
from resource_management import *

config = Script.get_config()

security_enabled = config['configurations']['cluster-env']['security_enabled']
kerberos_cache_file = default('/configurations/cluster-env/kerberos_cache_file','/tmp/ccache_keytab')
kerberos_domain = config['configurations']['cluster-env']['kerberos_domain']

smoke_user_keytab = default('/configurations/cluster-env/smokeuser_keytab',None)
smoke_user = config['configurations']['cluster-env']['smokeuser']

camus_user = config['configurations']['camus']['camus_user']
camus_group = config['configurations']['camus']['camus_group']
camus_hdfs_home = config['configurations']['camus']['camus_hdfs_home']
camus_local_home = config['configurations']['camus']['camus_local_home']

camus_principal = default('/configurations/camus/camus_principal',None)
camus_keytab = default('/configurations/camus/camus_keytab',None)

camushs_principal_name = default('/configurations/camus/dfs.camus.kerberos.principal',None)
camushs_keytab = default('/configurations/camus/camushs_keytab',None)

hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hdfs_principal_name = default('/configurations/hadoop-env/hdfs_principal_name',None)
hdfs_user_keytab = default('/configurations/hadoop-env/hdfs_user_keytab',None)

kafka_broker_hosts = default("/clusterHostInfo/kafka_broker_hosts",[])
kafka_fetch_buffer_size = config['configurations']['kafka-server-properties']['socket.send.buffer.bytes']

camus_configuration_directory = config['configurations']['camus']['camus.configuration.directory']
camus_assembly = config['configurations']['camus']['camus_assembly']
camus_examples_jar = config['configurations']['camus']['camus_examples_jar']
camus_job_name = config['configurations']['camus']['camus.job.name']

etl_destination_path = config['configurations']['camus']['etl.destination.path']
etl_execution_base_path = config['configurations']['camus']['etl.execution.base.path']
etl_execution_history_path = config['configurations']['camus']['etl.execution.history.path']
camus_message_decoder_class = config['configurations']['camus']['camus.message.decoder.class']
etl_record_writer_provider_class = config['configurations']['camus']['etl.record.writer.provider.class']
etl_partitioner_class = config['configurations']['camus']['etl.partitioner.class']
etl_destination_path_topic_sub_dirformat = config['configurations']['camus']['etl.destination.path.topic.sub.dirformat']
etl_output_file_time_partition_mins = config['configurations']['camus']['etl.output.file.time.partition.mins']
mapred_map_tasks = config['configurations']['camus']['mapred.map.tasks']
mapreduce_output_fileoutputformat_compress = config['configurations']['camus']['mapreduce.output.fileoutputformat.compress']
etl_output_codec = config['configurations']['camus']['etl.output.codec']
etl_deflate_level = config['configurations']['camus']['etl.deflate.level']
kafka_whitelist_topics = config['configurations']['camus']['kafka.whitelist.topics']
kafka_blacklist_topics = config['configurations']['camus']['kafka.blacklist.topics']
kafka_client_name = config['configurations']['camus']['kafka.client.name']
kafka_max_pull_hrs = config['configurations']['camus']['kafka.max.pull.hrs']
kafka_max_pull_minutes_per_task = config['configurations']['camus']['kafka.max.pull.minutes.per.task']
kafka_max_historical_days = config['configurations']['camus']['kafka.max.historical.days']
kafka_fetch_request_correlationid = config['configurations']['camus']['kafka.fetch.request.correlationid']
kafka_fetch_request_max_wait = config['configurations']['camus']['kafka.fetch.request.max.wait']
kafka_fetch_request_min_bytes = config['configurations']['camus']['kafka.fetch.request.min.bytes']
kafka_timeout_value = config['configurations']['camus']['kafka.timeout.value']
kafka_move_to_earliest_offset = config['configurations']['camus']['kafka.move.to.earliest.offset']
log4j_configuration = config['configurations']['camus']['log4j.configuration']
etl_default_timezone = config['configurations']['camus']['etl.default.timezone']

#namenode_host = default("/clusterHostInfo/namenode_host", ["none"])
#namenode_host =str(namenode_host[0])

