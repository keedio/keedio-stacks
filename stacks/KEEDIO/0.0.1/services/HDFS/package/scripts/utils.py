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

def service(action=None, name=None, user=None, create_pid_dir=False,
            create_log_dir=False):
  import params

  pid_dir = format("{hadoop_pid_dir_prefix}/{user}")
  pid_file = format("{pid_dir}/hadoop-{user}-{name}.pid")
  log_dir = format("{hdfs_log_dir_prefix}/{user}")
  check_process = format(
    "ls {pid_file} >/dev/null 2>&1 &&"
    " ps `cat {pid_file}` >/dev/null 2>&1")

  if create_pid_dir:
    Directory(pid_dir,
              owner=user,
              recursive=True)
  if create_log_dir:
    Directory(log_dir,
              owner=user,
              recursive=True)

  hadoop_env_exports = {
    'HADOOP_LIBEXEC_DIR': params.hadoop_libexec_dir
  }

  if params.security_enabled and name == "datanode":
    ## The directory where pid files are stored in the secure data environment.
    hadoop_secure_dn_pid_dir = format("{hadoop_pid_dir_prefix}/{hdfs_user}")
    hadoop_secure_dn_pid_file = format("{hadoop_secure_dn_pid_dir}/hadoop_secure_dn.pid")

    # At Champlain stack and further, we may start datanode as a non-root even in secure cluster
    if not params.stack_is_hdp22_or_further or params.secure_dn_ports_are_in_use:
      user = "root"
      pid_file = format(
        "{hadoop_pid_dir_prefix}/{hdfs_user}/hadoop-{hdfs_user}-{name}.pid")

    if action == 'stop' and params.stack_is_hdp22_or_further and \
      os.path.isfile(hadoop_secure_dn_pid_file):
        # We need special handling for this case to handle the situation
        # when we configure non-root secure DN and then restart it
        # to handle new configs. Otherwise we will not be able to stop
        # a running instance
        user = "root"
        try:
          with open(hadoop_secure_dn_pid_file, 'r') as f:
            pid = f.read()
          os.kill(int(pid), 0)

          custom_export = {
            'HADOOP_SECURE_DN_USER': params.hdfs_user
          }
          hadoop_env_exports.update(custom_export)
        except IOError:
          pass  # Can not open pid file
        except ValueError:
          pass  # Pid file content is invalid
        except OSError:
          pass  # Process is not running


  hadoop_env_exports_str = ''
  for exp in hadoop_env_exports.items():
    hadoop_env_exports_str += "export {0}={1} && ".format(exp[0], exp[1])

  hadoop_daemon = format(
    "{hadoop_env_exports_str}"
    "{hadoop_bin}/hadoop-daemon.sh")
  cmd = format("{hadoop_daemon} --config {hadoop_conf_dir}")

  daemon_cmd = format("{ulimit_cmd} su -s /bin/bash - {user} -c '{cmd} {action} {name}'")

  service_is_up = check_process if action == "start" else None
  #remove pid file from dead process
  File(pid_file,
       action="delete",
       not_if=check_process,
  )
  Execute(daemon_cmd,
          not_if=service_is_up
  )
  if action == "stop":
    File(pid_file,
         action="delete",
    )

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
  if rc == 2 :
    Logger.error("Code 2: Invalid argument\n%s" % stderr)
    raise InvalidArgument(stderr)
  if rc == 3 :
    Logger.error("Code 3: Component is Not Running\n%s" % stderr)
    raise ComponentIsNotRunning(stderr)
  if rc > 0 :
    Logger.error("Code 0: Undefined error\n%s" % stderr)
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

def executeSudoKrb(cmd,user=None,principal=None,keytab=None,keytab_cache=None,input=None):
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
 
  executed=Popen(cmd,stdin=PIPE,stdout=PIPE,stderr=PIPE)
  out,err=executed.communicate(input=input)

  if secure and auth_token:
    auth_token.destroy()

  return out,err,executed.returncode
    
  
