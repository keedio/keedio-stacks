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

from resource_management import *
from utils import execute_sudo_krb
from subprocess import *
from functools import partial

class OozieServiceCheck(Script):
  def service_check(self, env):
    import params
    env.set_params(params)
    
    self.oozie_smoke_test()
  
  def oozie_smoke_test(self):
    import params
  
    Directory(params.tmp_dir,
      owner=params.smoke_user,
      group=params.oozie_group
    )

    # Locate oozie-examples tar   
    cmd_locate_examples_1=['rpm','-qal']
    cmd_locate_examples_2=['grep','oozie-examples.tar.gz']
    cmd_aux=Popen(cmd_locate_examples_1,stdout=PIPE)
    cmd_aux2=Popen(cmd_locate_examples_2,stdin=cmd_aux.stdout,stdout=PIPE)
    cmd_aux.stdout.close()
    oozie_examples_file=cmd_aux2.communicate()[0][:-1]
    cmd_aux2.stdout.close()


    # Define partial aux functions 
    execute_hdfs = partial(execute_sudo_krb,user=params.hdfs_user,principal=params.hdfs_principal_name,keytab=params.hdfs_user_keytab) 
    execute_oozie = partial(execute_sudo_krb,user=params.smoke_user,principal=params.smoke_user,keytab=params.smoke_user_keytab)

    cmd_untar=['su','-s','/bin/bash',params.smoke_user,'-c','tar xozf %s -C %s' % (oozie_examples_file, params.tmp_dir)]
    execute_oozie(cmd_untar)

    # HDFS oozie user init
    cmd_create_dir_hdfs=['hdfs','dfs','-mkdir','-p','/user/%s' % (params.smoke_user)]
    cmd_chown_dir_hdfs=['hdfs','dfs','-chown','%s:' % params.smoke_user ,'/user/%s' % params.smoke_user]
    execute_hdfs(cmd_create_dir_hdfs)
    execute_hdfs(cmd_chown_dir_hdfs)
  
    # Examples upload
    cmd_upload_examples=['hdfs','dfs','-put',params.tmp_dir+'/examples']
    execute_oozie(cmd_upload_examples)
    # Example properties setup
    example_job_properties=params.tmp_dir+'/examples/apps/'+params.example_job+'/job.properties'
    self.set_job_properties(example_job_properties,params.namenode,params.resourcemanager)

    # Job submit
    cmd_oozie_submit =['oozie','job','-oozie','http://%s:%d/oozie' % (params.oozie_server,params.oozie_port),'-config',example_job_properties,'-run']
    out,err,rc=execute_oozie(cmd_oozie_submit)
    jobId=out[5:-1]
    if self.check_oozie_job_status(jobId) != 0: raise Exception('JOB doesn\'t succeeded')

  def set_job_properties(self,job_properties_file,namenode,resourcemanager):
    import params

    cmd_set_namenode_8020=['sed','-i',"s|nameNode=hdfs://localhost:8020|nameNode=%s|g" % namenode, job_properties_file]
    cmd_set_namenode_9000=['sed','-i',"s|nameNode=hdfs://localhost:9000|nameNode=%s|g" % namenode, job_properties_file]
    cmd_set_jobtracker_8021=['sed','-i',"s|jobTracker=localhost:8021|jobTracker=%s|g" % resourcemanager, job_properties_file]
    cmd_set_jobtracker_8032=['sed','-i',"s|jobTracker=localhost:8032|jobTracker=%s|g" % resourcemanager, job_properties_file]
    cmd_set_jobtracker_9001=['sed','-i',"s|jobTracker=localhost:9001|jobTracker=%s|g" % resourcemanager, job_properties_file]
    cmd_set_user_path=['sed','-i',"s|${user.name}|%s|g" % params.smoke_user, job_properties_file]

    execute_oozie = partial(execute_sudo_krb,user=params.smoke_user,principal=params.smoke_user,keytab=params.smoke_user_keytab)

    execute_oozie(cmd_set_namenode_8020) 
    execute_oozie(cmd_set_namenode_9000) 
    execute_oozie(cmd_set_jobtracker_8021) 
    execute_oozie(cmd_set_jobtracker_8032) 
    execute_oozie(cmd_set_jobtracker_9001) 
    execute_oozie(cmd_set_user_path) 

  def check_oozie_job_status(self,jobId):
    import params
    import re,time
    pattern=re.compile('Status\s*\:\s*(\w+)')
    execute_oozie = partial(execute_sudo_krb,user=params.smoke_user,principal=params.smoke_user,keytab=params.smoke_user_keytab)
    
    cmd_check_status=['oozie','job','-oozie','http://%s:%d/oozie' % (params.oozie_server,params.oozie_port),'-info','%s' % jobId]
    status="RUNNING"
    while status=="RUNNING":    
      out,err,rc=execute_oozie(cmd_check_status)
      for line in out.splitlines():
        m=pattern.match(line)
        if m:
          status=m.group(1)
          break
      time.sleep(10)
    return 0 if status=="SUCCEEDED" else 1
 
if __name__ == "__main__":
  OozieServiceCheck().execute()
  
