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
import pip

class Kafka(Script):
  def install(self, env):
    #import params
    pip.main(['install', 'kafka-python'])
    self.install_packages(env)
    #env.set_params(params)
    #self.configure(env)

  def start(self, env):
    import params
    env.set_params(params)
    
    self.configure(env)
    kafka(action='start')

  def stop(self, env):
    import params
    env.set_params(params)

    kafka(action='stop')

  def configure(self, env):
    import params
    env.set_params(params)

    kafka(action='config')

  def status(self, env):
    kafka(action='status')

  def rebalance(self, env):
    import params
    executed = Popen(["/usr/lib/kafka/bin/kafka-preferred-replica-election.sh","--zookeeper",params.zookeeper_server_hosts],stdout=PIPE,stderr=PIPE)
    out,err = executed.communicate()
    Logger.info("Kafka rebalancing:")
    Logger.info(str(out))
    Logger.info(str(err))

  def repartition(self, env):
    import params
    #executed = Popen(["/usr/lib/kafka/bin/kafka-preferred-replica-election.sh","--zookeeper",params.zookeeper_server_hosts],stdout=PIPE,stderr=PIPE)
    #out,err = executed.communicate()
    Logger.info("Kafka rebalancing: Not yet implemented")
    #Logger.info(str(out))
    #Logger.info(str(err))

if __name__ == "__main__":
  Kafka().execute()
