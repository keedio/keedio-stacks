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
from utils import *
from subprocess import *
from time import sleep,strftime


def namenode(action=None, do_format=True):

  #we need this directory to be present before any action(HA manual steps for
  #additional namenode)
  if action == "configure":
    import params
    Logger.info("Configuring namenode")
    Directory([params.dfs_name_dir, params.namenode_formatted_mark.rsplit('/',1)[0]],
            owner=params.hdfs_user,
            group=params.user_group,
            recursive=True
    )

  if action == "start":
    import params
    Logger.info("Starting namenode")
    #This file is required when starting service
    File(params.exclude_file_path,
	content=Template("exclude_hosts_list.j2"),
	owner=params.hdfs_user,
	group=params.user_group
    )

    if do_format:
      Logger.info("Namenode will be be formatted")
      format_namenode()
      pass
    
    cmd=Popen(['service','hadoop-hdfs-namenode','start'],stdout=None,stderr=None)
    out,err = cmd.communicate()
    Logger.info("Starting namenode service")
    Logger.info(out)
    Logger.info(err)
    if cmd.returncode == 0 and wait_safe_mode_off():
      Logger.info("Creating hdfs directories")
      create_hdfs_directories()

  if action == "stop":
    Logger.info("Stopping namenode")
    cmd=Popen(['service','hadoop-hdfs-namenode','stop'])
    out,err = cmd.communicate()
    Logger.info(out)
    Logger.info(err)

  if action == "decommission":
    decommission()

  if action == "status":
    Logger.info("Checking namenode status")
    cmd=Popen(['service','hadoop-hdfs-namenode','status'],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info(out)
    Logger.info(err)
    rc=cmd.returncode
    check_rc(rc,stdout=out,stderr=err)
    
def wait_safe_mode_off():
  import params 

  isActive=True 
  MAX_TRIES=40
  TIMEOUT=10
  safemode_off=False 

  if params.dfs_ha_enabled:
    Logger.info("Checking if active NN")
    cmd = ["hdfs","haadmin","-getServiceState",params.namenode_id]
    out,err,rc = execute_sudo_krb(cmd)
    check_rc(rc,stdout=out,stderr=err)
    isActive= out=="active"
  if isActive:  
    for x in xrange(MAX_TRIES):
      Logger.info("Waiting for safemode OFF")
      cmd=["hdfs","dfsadmin","-safemode","get"]
      out,err,rc = execute_sudo_krb(cmd)
      check_rc(rc,stdout=out,stderr=err)
      safemode_off = "Safe mode is OFF" in out
      if safemode_off:
        break
      sleep(TIMEOUT)
    Logger.info("safemode_off: %s, output message: %s" % (safemode_off,out))
  return safemode_off
  

def create_hdfs_directories():
  import params

  cmd = ["hdfs","dfs","-mkdir","/tmp"] 
  rc = execute_sudo_krb(cmd)[2]
  if rc == 0:
    cmd = ["hdfs","dfs","-chown",params.hdfs_user]
    rc = execute_sudo_krb(cmd)[2]
  if rc == 0:
    cmd = ["hdfs","dfs","-chmod","1777"]
    rc = execute_sudo_krb(cmd)[2]
   
  cmd = ["hdfs","dfs","-mkdir -p",params.smoke_hdfs_user_dir] 
  rc = execute_sudo_krb(cmd)[2]
  if rc == 0:
    cmd = ["hdfs","dfs","-chown -R",params.smoke_user, params.smoke_hdfs_user_dir]
    rc = execute_sudo_krb(cmd)[2]

  if rc == 0:
    cmd = ["hdfs","dfs","-chmod -R",str(params.smoke_hdfs_user_mode), params.smoke_hdfs_user_dir]
    rc = execute_sudo_krb(cmd)[2]

def format_namenode(force=None):
  import params

  mark_file = params.namenode_formatted_mark
  dfs_name_dir = params.dfs_name_dir
  hdfs_user = params.hdfs_user
  hadoop_conf_dir = params.hadoop_conf_dir

  if not params.dfs_ha_enabled:
    if not force and os.path.exists(mark_file):
        Logger.info("NN won't be formatted. %s file exists." % mark_file)
        return False
    cmd = ["hdfs","namenode","-format"]
    out,err,rc=execute_sudo_krb(cmd)
    Logger.info("NN formatted %s\n%s" % (rc==0,out))
    check_rc(rc,stdout=out,stderr=err)
    file = open(mark_file, "w")
    file.write(strftime("%Y%m%d-%H%M%S"))
    file.close()
    return True

def decommission():
  import params

  hdfs_user = params.hdfs_user
  user_group = params.user_group
  
  File(params.exclude_file_path,
       content=Template("exclude_hosts_list.j2"),
       owner=hdfs_user,
       group=user_group
  )
  
  if params.dfs_ha_enabled:
    # due to a bug in hdfs, refreshNodes will not run on both namenodes so we
    # need to execute each command scoped to a particular namenode
#    cmd=["dfsadmin","-fs","hdfs://"+params.namenode_rpc,"-refreshNodes"]
     cmd=["hdfs","dfsadmin","hdfs://"+params.namenode_rpc,"-refreshNodes"]
  else:
#    cmd=["dfsadmin","-fs","-refreshNodes"]
    cmd=["hdfs","dfsadmin","-refreshNodes"]
  execute_sudo_krb(cmd)

