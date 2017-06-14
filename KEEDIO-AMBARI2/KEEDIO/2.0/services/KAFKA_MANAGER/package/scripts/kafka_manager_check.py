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

import requests
import json
from resource_management import *
from kafka_manager_handler import kafka_manager


class KafkaManagerServiceCheck(Script):
    def service_check(self, env):
        import params
        env.set_params(params)
        kafka_manager(action='status')

        # TODO: Include a conditional flag to try to create the cluster or not

        # Get Kafka Manager host
        Logger.info("Kafka Manager service: " + ','.join(params.kafka_manager_hosts))
        kafka_manager_host = params.kafka_manager_hosts[0]

        # Get Kafka version
        kafka_version = '0.10.1.0' # TODO: Remove hardcoded var

        # Create Kafka Manager cluster
        url = "http://" + kafka_manager_host + ":" + str(params.kafka_manager_port) + "/clusters"
        payload = {'name': params.clustername, 'zkHosts': params.zookeeper_server_hosts, 'kafkaVersion': kafka_version}
        Logger.info("URL: " + url)
        Logger.info("Data: " + json.dumps(payload))
        response = requests.post(url, data=payload)
        if not response.status_code == 200:
            Logger.logger.warn("Couldn't auto-create cluster in Kafka Manager: CODE " + response.status_code)


if __name__ == "__main__":
    KafkaManagerServiceCheck().execute()
