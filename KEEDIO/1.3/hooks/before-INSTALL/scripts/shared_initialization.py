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

def setup_java():
  """
  Installs jdk using specific params, that comes from ambari-server
  """
  import params
  
  jdk_name = format("{jdk_name}")
  
  #jdk_curl_target = format("{artifact_dir}/{jdk_name}")
  java_dir = os.path.dirname(params.java_home)
  java_exec = format("{java_home}/bin/java")

  if not params.jdk_name:
    return

  #environment = {
  #  "no_proxy": format("{ambari_server_hostname}")
  #}

  #Execute(format("mkdir -p {artifact_dir} ; \
  #curl -kf -x \"\" \
  #--retry 10 {jdk_location}/{jdk_name} -o {jdk_curl_target}"),
  #        path = ["/bin","/usr/bin/"],
  #        not_if = format("test -e {java_exec}"),
  #        environment = environment)

  #if params.jdk_name.endswith(".bin"):
  #  install_cmd = format("mkdir -p {java_dir} ; chmod +x {jdk_curl_target}; cd {java_dir} ; echo A | {jdk_curl_target} -noregister > /dev/null 2>&1")
  #elif params.jdk_name.endswith(".gz"):
  #  install_cmd = format("mkdir -p {java_dir} ; cd {java_dir} ; tar -xf {jdk_curl_target} > /dev/null 2>&1")
  
  Package([jdk_name])
  #Execute(install_cmd,
  #        path = ["/bin","/usr/bin/"],
  #        not_if = format("test -e {java_exec}")
  #)
  #File(params.task_log4j_properties_location,
  File(params.java_profile_location,
    content=StaticFile("java.sh"),
    mode=0755
  )


def install_packages():
  import params 
  packages = ['unzip', 'curl']
  if params.stack_is_hdp22_or_further:
    packages.append('hdp-select')

  if params.has_spacewalk_client:
     packages.append('rhn-client-tools')
     packages.append('rhn-setup')
     packages.append('rhnsd')
     packages.append('m2crypto')
     packages.append('yum-rhn-plugin')
  Package(packages)

def install_spacewalk_client():
   from params import *
   if has_spacewalk_client:
      cmd=Popen(['/bin/rpm','-Uvh',spacewalk_certificate],stdout=PIPE,stderr=PIPE)
      out,err= cmd.communicate() 
      Logger.info("Installing certificate for the Spacewalk client")
      Logger.info(out)
      Logger.info(err)
      if cmd.returncode > 0:
         raise Exception ("Cannot retrieve spacewalk certificate, check the address in the configuration!")

      cmd=Popen(['/usr/sbin/rhnreg_ks','--serverUrl='+spacewalk_server,'--sslCACert=/usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT','--activationkey='+activation_key],stdout=PIPE,stderr=PIPE)
      out,err= cmd.communicate()
      Logger.info("Installing Spacewalk client")
      Logger.info(out)
      Logger.info(err)
      if cmd.returncode == 1:
         raise Exception ("Invalid Spacewalk activation key, stopping")         

      Logger.info("Configuring Spacewalk client")
      File('/etc/yum/pluginconf.d/rhnplugin.conf',
      content=Template("rhnplugin.j2"),
      mode=0755
  )
   else:
      Logger.info("Spacewalk not installed")
 

