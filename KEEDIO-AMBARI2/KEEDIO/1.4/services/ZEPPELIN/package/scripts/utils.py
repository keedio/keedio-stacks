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
    auth_token = kerberosWrapper.krb_wrapper(principal,keytab,keytab_cache)
    os.environ['KRB5CCNAME'] = keytab_cache
  else:
    cmd_aux = ["su","-s","/bin/bash",user,"-c"]
    cmd_aux.append(' '.join(cmd))
    cmd = cmd_aux
  Logger.info("Executing %s" % str(cmd)) 
  executed=Popen(cmd,stdin=PIPE,stdout=PIPE,stderr=PIPE)
#  out,err=executed.communicate(input=input)
  out,err=executed.communicate()
  if secure and auth_token:
    auth_token.destroy()

  return out,err,executed.returncode
