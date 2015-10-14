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

import sys
from resource_management import *
from subprocess import *

from hive import hive
import utils

         
class HiveServerHandler(Script):
  def install(self, env):
    import params
    self.install_packages(env,params.exclude_packages)
    self.initialize_db(env)
    
  def configure(self, env):
    import params
    env.set_params(params)
    hive(action='config',service='hive-metastore')
    
  def start(self, env):
    self.configure(env)
    hive(action='start',service='hive-metastore')
    
  def stop(self, env):
    hive(action='stop',service='hive-metastore')

  def status(self, env):
    hive(action='status',service='hive-metastore')

  def initialize_db(self,env):
    import params
    try:
        Popen(['mysql','-h',params.jdbc_host,'-b',params.jdbc_db,'-u',params.jdbc_username,'--password='+params.jdbc_password,'-e','source /usr/lib/hive/scripts/metastore/upgrade/mysql/hive-schema-0.13.0.mysql.sql;'],stdout=PIPE,stderr=PIPE)
    except: 
        Logger.info("Cannot create Hive schema in the backend database, make sure you clean the database before restarting the installation!")
        exit()
     
if __name__ == "__main__":
  HiveServerHandler().execute()
