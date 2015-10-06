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
from utils import *
from subprocess import *

class CassandraServiceCheck(Script):
  def service_check(self, env):
    import params
    env.set_params(params)
    
    status_cmd = ["source /etc/default/cassandra && /usr/lib/cassandra/bin/nodetool status -r"]
    cmd = Popen(status_cmd,stdout=PIPE,stderr=PIPE,shell=True)
    out,err=cmd.communicate()
    rc=cmd.returncode
    # out,err,rc=execute_sudo_krb(status_cmd,user=params.cassandra_user,principal=params.cassandra_principal_name,keytab=params.cassandra_keytab_file)
    check_rc(rc,stdout=out,stderr=err)
    status = self.parse_status(out)
    error_servers=""
    for server,value in status.iteritems():
      if value['status']=='UN':
        continue
      else:
        error_servers+="Server %s is in state %s\n" % (server,value['status'])
    if error_servers:
      raise Fail(error_servers)
    Logger.info("Cassandra cluster is OK")

  def parse_status(self,input):
    lines = input.split('\n')
    output=dict()
    for line in lines:
      cutted = line.split()
      if len(cutted) == 8 and cutted[0] != '--':
        status,server,load,unit,tokens,owns,id,rack=cutted
        output[server]={"status":status,"load":load,"tokens":tokens,"owns":owns,"id":id,"rack":rack}
    return output
    

if __name__ == "__main__":
  CassandraServiceCheck().execute()
  
