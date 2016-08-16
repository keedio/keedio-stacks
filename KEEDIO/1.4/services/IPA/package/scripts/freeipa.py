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
import os.path
import socket

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
    dns_cmd=[]
    if dns: 
       Logger.info("Installing IPA DNS service")
       dns_cmd=["--setup-dns"]
       if reverse_dns:
          Logger.info("Enabling reverse name resolution")
       else:
          Logger.info("Disabling reverse name resolution")
          dns_cmd.append("--no-reverse")
       if dns_forwarders == 'none':
          Logger.info("Disabling forwarders")
          dns_cmd.append("--no-forwarders")
       else: 
          forwarderlist=dns_forwarders.split(',') 
          Logger.info("The list of forwarders")
          Logger.info(dns_forwarders)
          
          for forwarder in forwarderlist:
             dns_cmd.append("--forwarder")
             dns_cmd.append(forwarder)
          

    cmd=Popen(['/usr/sbin/ipa-server-install','-a',ipa_password,'--hostname='+hostname,'-r',ipa_realm,'-p',ipa_password,'-n',domain,'-U']+dns_cmd,stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info("installing FreeIPA server")
    Logger.info(out)
    Logger.info(err)
    if cmd.returncode > 0 : 
       Logger.info("IPA Server installation Failed")       
 

  if action == 'config':
    print "cacadelavaca"
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
      
        # This is fro replication
        #prepare_replicas()       
 

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
   


def prepare_replicas():
    import os.path
    for host in ipa_replica_hosts:
        if not os.path.exists("/var/lib/ipa/replica-info-"+host+".gpg"):
            Logger.info("Preparing replica cartificate for host "+host)
            cmd=Popen(['/usr/sbin/ipa-replica-prepare',host,'-p',ipa_password],stdout=PIPE,stderr=PIPE)
            out,err=cmd.communicate()
            Logger.info(out)
            Logger.info(err)
     
    for host in ipa_replica_hosts:
        certificate="/var/lib/ipa/replica-info-"+host+".gpg"
        destination="root@"+host+":/var/lib/ipa/."
        print certificate, destination
        if os.path.exists(certificate):
            Logger.info("Sending replica cartificate  to host "+host)
            cmd=Popen(["/usr/bin/rsync","-aR",certificate,destination ],stdout=PIPE,stderr=PIPE)
            out,err=cmd.communicate()
            Logger.info(out)
            Logger.info(err)


def freeipaclient(action=None):

  print "AlessioCCC",action

  if action == 'install':
    from params import *
    if is_ipa_server == True:
        Logger.info("This is the IPA server, the client is already installed!")
    else:
        File('/etc/resolv.conf',
             content=Template('resolvconf.j2'),
             owner='root',
             group='root')
        if dns: 
           dns_cmd=["--enable-dns-updates"]
        else:
           dns_cmd=[]

    	cmd=Popen(['/usr/sbin/ipa-client-install','-U','--server='+ipa_server_host,'--domain='+domain,'-p','admin','-w',ipa_password]+dns_cmd,stdout=PIPE,stderr=PIPE)
    	out,err=cmd.communicate()
    	Logger.info("installing FreeIPA client")
    	Logger.info(out)
    	Logger.info(err)
    	if cmd.returncode > 0 :
       		Logger.info("IPA Server installation Failed")


  if action == 'config':
    from params import *
    if manual_configuration != True and not os.path.exists("/var/lib/ipa-client/ambari-lock"):
          Logger.info("configuring ipa client  using ipa CLI")
          if dns and reverse_dns: 
		# Authentication with KDC
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
			raise Fail("IPA Client Configuration Failed")
		cmd= Popen(['/usr/bin/klist'], stdout=PIPE, stderr=PIPE)
		out,err=cmd.communicate()
		Logger.info(out)
		Logger.info(err)

		# Getting reverse DNS zones, assuming that the first is the good one
		# If you have more zones, you should probably ise manual configuration 
		Logger.info("getting list of reverse DNS zones") 
		cmd= Popen(['/usr/bin/ipa','dnszone-find'], stdout=PIPE, stderr=PIPE)
		out,err=cmd.communicate()
		Logger.info("Authenticating to  FreeIPA server")
		Logger.info(out)
		Logger.info(err)
		for line in out.splitlines(): 
		    if 'arpa' in line: 
			dns_zone=line.split(':')[1].strip() 
			break
		try: 
                     Logger.info("DNS zone"+dns_zone)
		except:
                     raise Fail("DNS zone parsing error:")

		#registering reverse DNS record
		hostname_ip_address = str(socket.gethostbyname(hostname))

		cmd= Popen(['/usr/bin/ipa','dnsrecord-add',dns_zone,hostname_ip_address.split('.')[3],'--ptr-hostname',hostname], stdout=PIPE, stderr=PIPE)
		out,err=cmd.communicate()
		Logger.info("Registering reverse DNS record for host "+ hostname)
		Logger.info(out)
		Logger.info(err)
	       
		cmd= Popen(['/usr/bin/nslookup', hostname_ip_address], stdout=PIPE, stderr=PIPE)
		out,err=cmd.communicate()
		Logger.info("Checking reverse name resolution for host"+ hostname)
		Logger.info("nslookup "+ hostname_ip_address)
		Logger.info(out)
		Logger.info(err)
	       
		#Destroy Kerberos tickets
		command="/usr/bin/kdestroy"
		Logger.info(command)
		cmd=Popen([command],stdout=PIPE,stderr=PIPE)
		out,err=cmd.communicate()
		Logger.info("Destroying temporary tickets")
		Logger.info(out)
		Logger.info(err)
		if cmd.returncode > 0 :
			raise Fail("IPA Client configuration Failed")
               
                # Creating lockfile 
                File('/var/lib/ipa-client/ambari-lock',
                content="lock",
                owner='root',
                group='root')
                

    else:
        Logger.info("Skipping configuration, either the client has been already configured or the manual configuration has been chosen") 
