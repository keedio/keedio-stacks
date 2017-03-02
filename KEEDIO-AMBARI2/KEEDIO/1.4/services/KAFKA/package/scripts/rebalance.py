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
from kafka_handler import kafka
from subprocess import *

class Rebalance(Script):

  def rebalance(self, env):
    import params
      executed = Popen(["/usr/lib/kafka/bin/kafka-preferred-replica-election.sh","--zookeeper",params.zookeeper_server_hosts+'/kafka'],stdout=PIPE,stderr=PIPE)
      out,err = executed.communicate()
      Logger.info("Kafka rebalancing:")
      Logger.info(action)
      Logger.info(str(out))
      Logger.info(str(err))
  
    



if __name__ == "__main__":
  Rebalance().execute()
