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
import time
import socket

class IPAServiceCheck(Script):
  def service_check(self, env):
    from params import *

    Logger.info("Testing authentication") 
    kinit = '/usr/bin/kinit'
    kinit_args = [ kinit, '%s@%s' % ('admin', ipa_realm) ]
    cmd= Popen(kinit_args, stdin=PIPE, stdout=PIPE, stderr=PIPE) 
    cmd.stdin.write('%s\n' % ipa_password)
    cmd.stdin.flush()
    out,err=cmd.communicate()
    Logger.info("Authenticating to  FreeIPA server") 
    Logger.info(out)
    Logger.info(err)
    if cmd.returncode > 0 :
	raise Fail("IPA Server installation Failed")
    cmd= Popen(['/usr/bin/klist'], stdout=PIPE, stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info(out)
    Logger.info(err)


    if dns and reverse_dns: 
        for host in ipa_client_hosts: 
                hostname_ip_address = str(socket.gethostbyname(host)) 
         	cmd= Popen(['/usr/bin/nslookup', hostname_ip_address], stdout=PIPE, stderr=PIPE)
         	out,err=cmd.communicate()
                Logger.info("Checking reverse name resolution for host"+ host)
                Logger.info("nslookup "+ hostname_ip_address)
                Logger.info(out)
                Logger.info(err) 
                if host not in out: 
                      raise Fail ("Reserve DNS resolution problem for host "+host ) 
                else: 
                        Logger.info("OK") 
            
if __name__ == "__main__":
  IPAServiceCheck().execute()
  
