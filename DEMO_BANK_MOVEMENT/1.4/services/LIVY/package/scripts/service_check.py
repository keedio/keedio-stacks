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

import os
from resource_management import *
from functools import partial
from utils import *
from livy import livy

class ServiceCheck(Script):


  def service_check(self, env):
    import params,json, pprint, requests, textwrap, time 
    env.set_params(params)
    
    # Define partial aux functions
    execute_hdfs = partial(execute_sudo_krb,user=params.hdfs_user,principal=params.hdfs_principal_name,keytab=params.hdfs_user_keytab)
    execute_livy = partial(execute_sudo_krb,user=params.smoke_user,principal=params.smoke_user,keytab=params.smoke_user_keytab)


    # HDFS oozie user init
    cmd_create_dir_hdfs=['hdfs','dfs','-mkdir','-p','/user/%s' % 'livy']
    cmd_chown_dir_hdfs=['hdfs','dfs','-chown','%s:' % 'livy','/user/%s' % 'livy']
    execute_hdfs(cmd_create_dir_hdfs)
    execute_hdfs(cmd_chown_dir_hdfs)


    host = 'http://'+params.livy_server+':'+params.livy_port
    data = {'kind': 'spark'}
    headers = {'Content-Type': 'application/json'}
    s = requests.Session()
    try:
       r = s.post(host + '/sessions', data=json.dumps(data), headers=headers)
    except: 
       raise Fail("Cannot start livy session")
    status = 'none'
    counter = 0
    Logger.info(r.headers)
    session_url = host + r.headers['location']
    while status != 'idle' and counter < 10:
      r = s.get(session_url, headers=headers)
      Logger.info(r.json())
      status=r.json()['state']
      counter = counter + 1
      Logger.info('Livy connection status: '+status)
      time.sleep(5)
    if counter > 9:
      raise Fail("Something is wrong with Livy, check /var/log/livy.log")
    statements_url = session_url + '/statements'
    data = {'code': '1 + 1'}
    r = s.post(statements_url, data=json.dumps(data), headers=headers)
    statement_url = host + r.headers['location']
    status = 'none'
    counter = 0
    while status != 'available' and counter < 10:
       r = s.get(statement_url, headers=headers)
       Logger.info(r.json())
       status=r.json()['state']
       counter = counter + 1
       Logger.info('Livy connection status: '+status)
       time.sleep(5)
    if r.json()['output']['data']['text/plain'] != 'res0: Int = 2':
        "Something is wrong with Livy, check /var/log/livy.log"
    try:
       #Close connection
       #session_url = host+'/sessions/0'
       s.delete(session_url, headers=headers) 
    except: 
       raise Fail("Error in closing connection, check yarn for stale livy jobs")
#{u'state': u'idle', u'id': 0, u'kind': u'spark'}
#    execute_spark = partial(execute_sudo_krb,user=params.smoke_user,principal=params.smoke_user,keytab=params.smoke_user_keytab)
#    Logger.info("Sourcing /etc/profile.d/hadoop-env.sh")
#    cmd=Popen('/bin/grep export  /etc/profile.d/hadoop-env.sh ',stdout=PIPE,stderr=PIPE,shell=True)
#    out,err=cmd.communicate()
#    Logger.info(out)
#    Logger.info(err)
#    # parsing the output
#    listout=out.split('\n')
#    listout.remove('')
#    for line in listout:
#         cmdlist=line.replace('=',' ').split(' ') 
#         os.environ[cmdlist[1]]=cmdlist[2]

#   Logger.info("The environment for spark execution:")
#    Logger.info(os.environ)
#    check_spark = [str(params.spark_local_home)+"/bin/spark-submit","--class","org.apache.spark.examples.SparkPi",str(params.spark_local_home)+"/lib/"+str(params.spark_examples_jar),"10"]
#    out,err,rc=execute_spark(check_spark)
#    check_rc(rc,stdout=out,stderr=err)

if __name__ == "__main__":
  ServiceCheck().execute()
