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
from time import sleep
from functools import partial
from utils import *

class HdfsServiceCheck(Script):
  def service_check(self, env):
    import params

    
    MAX_TRIES=40
    TIMEOUT=10
    safemode = True
    env.set_params(params)
    unique = functions.get_unique_id_and_date()
    dir = '/tmp'
    tmp_file = dir+"/"+unique
    smoke_user = params.smoke_user
    smoke_user_principal =  params.smoke_user_principal
    smoke_keytab =params.smoke_user_keytab
    safemode_command = ["hdfs","dfsadmin","-safemode","get"]

    execute_smoke = partial(executeSudoKrb,user=smoke_user,principal=smoke_user_principal,keytab=smoke_keytab)

    create_dir_cmd = ["hdfs","dfs","-mkdir",dir]
    chmod_command = ["hdfs","dfs","-chmod","777",dir]
    test_dir_exists = ["hdfs","dfs","-test","-e",dir]
    cleanup_cmd = ["hdfs","dfs","-rm",tmp_file]
    #cleanup put below to handle retries; if retrying there wil be a stale file
    #that needs cleanup; exit code is fn of second command
    create_file_cmd = ["hdfs","dfs","-put","/etc/passwd",tmp_file]
    test_cmd = ["hdfs","dfs","-test","-e",tmp_file]

    for x in xrange(MAX_TRIES):
      Logger.info("Waiting for safemode OFF")
      out,err,rc = executeSudoKrb(safemode_command)
      safemode_off = "Safe mode is OFF" in out
      if safemode_off:
        break
      sleep(TIMEOUT)
    Logger.info("safemode_off: %s, output message: %s" % (safemode_off,out))
    if not safemode_off:
      Logger.error("Safe mode ON, test won't be executed")
      raise Fail("Safemode ON")
    
    rc = execute_smoke(test_dir_exists)[2]
    if rc!=0:
      out,err,rc = execute_smoke(create_dir_cmd)
      check_rc(rc,stdout=out,stderr=err)
    else:
      out,err,rc = execute_smoke(chmod_command)
      check_rc(rc,stdout=out,stderr=err)

      out,err,rc = execute_smoke(cleanup_cmd)
      if rc == 0:
        out,err,rc = execute_smoke(test_cmd)[2]
        check_rc(rc,stdout=out,stderr=err)
      
      out,err,rc = execute_smoke(create_file_cmd)
      check_rc(rc,stdout=out,stderr=err)

      rc = execute_smoke(test_cmd)[2]
      check_rc(rc)

      out,err,rc = execute_smoke(cleanup_cmd)
      check_rc(rc,stdout=out,stderr=err)

    if params.has_journalnode_hosts:
      journalnode_port = params.journalnode_port
      smoke_test_user = params.smoke_user
      checkWebUIFileName = "checkWebUI.py"
      checkWebUIFilePath = format("{tmp_dir}/{checkWebUIFileName}")
      comma_sep_jn_hosts = ",".join(params.journalnode_hosts)
      checkWebUICmd = format(
        "su -s /bin/bash - {smoke_test_user} -c 'python {checkWebUIFilePath} -m "
        "{comma_sep_jn_hosts} -p {journalnode_port}'")
      File(checkWebUIFilePath,
           content=StaticFile(checkWebUIFileName))

      Execute(checkWebUICmd,
              logoutput=True,
              try_sleep=3,
              tries=5
      )

    if params.is_namenode_master:
      if params.has_zkfc_hosts:
        pid_dir = format("{hadoop_pid_dir_prefix}/{hdfs_user}")
        pid_file = format("{pid_dir}/hadoop-{hdfs_user}-zkfc.pid")
        check_zkfc_process_cmd = format(
          "ls {pid_file} >/dev/null 2>&1 && ps `cat {pid_file}` >/dev/null 2>&1")
        Execute(check_zkfc_process_cmd,
                logoutput=True,
                try_sleep=3,
                tries=5
        )


if __name__ == "__main__":
  HdfsServiceCheck().execute()
