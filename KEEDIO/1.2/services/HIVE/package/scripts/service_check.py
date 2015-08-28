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
from functools import partial
from utils import *

class ServiceCheck(Script):
  def service_check(self, env):
    import params
    env.set_params(params)
    execute_smoke = partial(execute_sudo_krb,user=params.smoke_user,principal=params.smoke_user,keytab=params.smoke_user_keytab)
    connection_url = 'jdbc:hive2://'+params.hive_server2_host+':'+str(params.hive_server2_port)+'/default'
    if params.security_enabled:
      connection_url += ';principal='+params.hive_server2_principal
    check_hiveserver2 = ['beeline','-u',connection_url,'-n',params.smoke_user,'-e',' ']
    out,err,rc=execute_smoke(check_hiveserver2)
    print out
    print err
    if 'Error' in out or 'Error' in err:
      raise Exception(out+err)

if __name__ == "__main__":
  ServiceCheck().execute()
