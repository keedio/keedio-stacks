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
from subprocess import *
from utils import check_rc
def freeipa(action=None):
  
  if action == 'start' or action == 'stop' or action == 'status':
    cmd=Popen(['service','ipa',action],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info('IPA server action: %s.\nSTDOUT=%s\nSTDERR=%s' % (action,out,err))
    if action == 'start' or action == 'status':
      check_rc(cmd.returncode,stdout=out,stderr=err)

  if action == 'install':
    from params import *
    cmd=Popen(['/usr/sbin/ipa-server-install','-a',ipa_password,'--hostname='+hostname,'-r',ipa_realm,'-p',ipa_password,'-n',domain,'-U'],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info("installing FreeIPA server")
    Logger.info(out)
    Logger.info(err)
    if cmd.returncode > 0 : 
       Logger.info("IPA Server installation Failed")       
 

  if action == 'config':
    from params import *
    if manual_configuration != True:
    	Logger.info("configuring ipa using ipa CLI")
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
 

    	command=['/usr/bin/ipa','krbtpolicy-mod','--maxlife='+maxlife,'--maxrenew='+maxrenew]

    	Logger.info(command)
    	cmd=Popen(command,stdout=PIPE,stderr=PIPE)
    	out,err=cmd.communicate()
    	Logger.info("Setting tickets lifetime policy")
    	Logger.info(out)
    	Logger.info(err)

        command=['/usr/bin/ipa','krbtpolicy-show']

        Logger.info(command)
        cmd=Popen(command,stdout=PIPE,stderr=PIPE)
        out,err=cmd.communicate()
        Logger.info(out)
        Logger.info(err)
        

    	command="/usr/bin/kdestroy"
        Logger.info(command)
    	cmd=Popen([command],stdout=PIPE,stderr=PIPE)
    	out,err=cmd.communicate()
    	Logger.info("Destroying temporary tickets")
    	Logger.info(out)
    	Logger.info(err)
    	if cmd.returncode > 0 :
       		raise Fail("IPA Server  configuration Failed")
    
    else:
        Logger.info("Manual configuration enabled for Free IPA")
   

def freeipaclient(action=None):


  if action == 'install':
    from params import *
    if is_ipa_server == True:
        Logger.info("This is the IPA server, the client is already installed!")
    else:
    	cmd=Popen(['/usr/sbin/ipa-client-install','-U','--server='+ipa_server_host,'--domain='+domain,'-p','admin','-w',ipa_password],stdout=PIPE,stderr=PIPE)
    	out,err=cmd.communicate()
    	Logger.info("installing FreeIPA client")
    	Logger.info(out)
    	Logger.info(err)
    	if cmd.returncode > 0 :
       		Logger.info("IPA Server installation Failed")


  if action == 'config':
    Logger.info("config not yet impelemented!")
