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
import re
from subprocess import *


def get_port(address):
  """
  Extracts port from the address like 0.0.0.0:1019
  """
  if address is None:
    return None
  m = re.search(r'(?:http(?:s)?://)?([\w\d.]*):(\d{1,5})', address)
  if m is not None:
    return int(m.group(2))
  else:
    return None

def is_secure_port(port):
  """
  Returns True if port is root-owned at *nix systems
  """
  if port is not None:
    return port < 1024
  else:
    return False

def check_rc(rc,stdout=None,stderr=None):
  if rc == 2:
    Logger.error("Code 2: Invalid argument\n%s" % stderr)
    raise InvalidArgument(stderr)
  if rc == 3:
    Logger.error("Code 3: Component is Not Running\n%s" % stderr)
    raise ComponentIsNotRunning(stderr)
  if rc > 0:
    Logger.error("Code %d: Undefined error\n%s" % (rc,stderr))
    raise Fail(stderr)

def hdfs_mkdir(sudo_cmd,path,owner=None,group=None,recursive=False,mode=None):
  cmd_aux = list(sudo_cmd) 
  cmd_aux.extend(["hdfs dfs " + "-mkdir -p" if recursive else "-mkdir",path])
  cmd_list =[list(cmd_aux)]
  if mode:
    cmd_aux = list(sudo_cmd) 
    cmd_aux.extend(["hdfs dfs " + "-chmod -r" if recursive else "-chmod",mode,path])
    cmd_list.append(cmd_aux)
  if owner or group:
    cmd_aux = list(sudo_cmd) 
    cmd_aux.extend(["hdfs dfs " + "chown -r" if recursive else "-chown",__owner_group(owner,group),path])
    cmd_list.append(cmd_aux)
  for cmd in cmd_list:
    Popen(cmd)

def os_mkdir(directories,owner=None,group=None,mode=0755):
  failed=[]
  for path in directories.split(','):
    status = __mkdir(path,mode)
    status = __chown(path,owner,group) if status else status
    if not status:
      failed.append(path)
  return failed
    
def __mkdir(path,mode):
  exists = False
  try:
    os.makedirs(path,mode)
    exists=True
  except:
    # If raised exception and path exists, it is fine
    exists=os.path.exists(path)
  return exists

def __chown(path,owner,group):
  uid,gid=-1,-1

  if owner:
    from pwd import getpwnam
    try:
      uid = getpwnam(owner).pw_uid
    except:
      return False

  if group:
    from grp import getgrnam
    try:
      gid = getgrnam(group).gr_gid
    except:
      return False

  try:
    os.chown(path,uid,gid)
    return True
  except:
    return False
  
def __chmod(path,mode):
  try:
    os.chmod(path,mode)
    return True
  except:
    return False

def __owner_group(owner,group):
  chown = owner
  if chown:
    chown = chown + ":" + group if group else chown
  else:
    chown = ":" + group
  return chown    

def execute_sudo_krb(cmd,user=None,principal=None,keytab=None,keytab_cache=None,input=None):
  import params
  
  secure = params.security_enabled
  user = user or params.hdfs_user
  principal = principal or params.hdfs_principal_name
  keytab = keytab or params.hdfs_user_keytab
  keytab_cache = keytab_cache or params.kerberos_cache_file
  
  auth_token=None
  
  if secure:
    import kerberosWrapper
    auth_token = kerberosWrapper.krb_wrapper(params.hdfs_principal_name, params.hdfs_user_keytab,params.kerberos_cache_file)
    os.environ['KRB5CCNAME'] = params.kerberos_cache_file
  else:
    cmd_aux = ["su","-s","/bin/bash",params.hdfs_user,"-c"]
    cmd_aux.append(' '.join(cmd))
    cmd = cmd_aux
  Logger.info("Executing %s" % str(cmd)) 
  executed=Popen(cmd,stdin=PIPE,stdout=PIPE,stderr=PIPE)
  out,err=executed.communicate(input=input)
  if secure and auth_token:
    auth_token.destroy()

  return out,err,executed.returncode
    
  
