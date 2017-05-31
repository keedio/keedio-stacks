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
import time
from resource_management import *
from subprocess import *
from utils import check_rc
def couchbase(action=None):
  
  if action == 'start' or action == 'stop' or action == 'status':
    cmd=Popen(['service','couchbase-server',action],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info('Couchbase action: %s.\nSTDOUT=%s\nSTDERR=%s' % (action,out,err))
    if action == 'start' or action == 'status':
      check_rc(cmd.returncode,stdout=out,stderr=err)
  if action == 'rebalance' :
    import params
    cmd=Popen(['/usr/lib/couchbase/bin/couchbase-cli','rebalance','-c',params.creator+':8091','-u',params.username,'-p',params.password],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info('Couchbase rebalance: STDOUT=%s\nSTDERR=%s' % (out,err))
    Logger.info(cmd.returncode)

    if cmd.returncode > 0 :
        raise Fail('CB Cluster rebalance failed')
    #File('/etc/couchbase/conf/custom.ini',
    #  content=Template('custom.ini.j2'),
    #  owner='couchbase',
    #  group='couchbase',
    #  mode=0550
    #)
   
  if action == 'install' :
    import params
    string=''.join(str(params.cb_clustercreator_host))
    Logger.info(string)
    services="--services="
    Directory(params.datadir,
    owner="couchbase",
    group="couchbase",
    create_parents = True
    )
    datadircmd="--node-init-data-path="+params.datadir 
    Directory(params.indexdir,
    owner="couchbase", 
    group="couchbase",
    create_parents = True
    )
    indexdircmd="--node-init-index-path="+params.indexdir


    if params.is_cb_datanode:
       services+='data,'

    if params.is_cb_indexnode:
        services+='index,'

    if params.is_cb_querynode:
        services+='query,'

    if services[-1]==',':
       services = services[:-1]
    string=''.join(str(services)) 
    Logger.info(string)

    ramsizecmd="--cluster-ramsize="+params.dataram 
    indexramsizecmd="--cluster-index-ramsize="+params.indexram 
    time.sleep(60)
    cmd=Popen(['/usr/lib/couchbase/bin/couchbase-cli','node-init','-c',params.hostname+':8091',datadircmd,indexdircmd,'-u',params.username,'-p',params.password],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info('Couchbase Node Init: STDOUT=%s\nSTDERR=%s' % (out,err))
    
    if params.is_cb_creator:
        time.sleep(60)
    	cmd=Popen(['/usr/lib/couchbase/bin/couchbase-cli','cluster-init','-c',params.hostname+':8091','--cluster-port=8091',ramsizecmd,indexramsizecmd,'--cluster-username='+params.username,'--cluster-password='+params.password,'-u',params.username,'-p',params.password,services],stdout=PIPE,stderr=PIPE)
        out,err=cmd.communicate()
        Logger.info('Couchbase Cluster Init: STDOUT=%s\nSTDERR=%s' % (out,err))
        Logger.info(str(cmd.returncode))

        if cmd.returncode > 0 :
           raise Fail('CB CXlouster initialization failed')  

    else:
        time.sleep(60)
    	cmd=Popen(['/usr/lib/couchbase/bin/couchbase-cli','server-add','-c',params.creator+':8091','--server-add='+params.hostname,'--server-add-username='+params.username,'--server-add-password='+params.password,'-u',params.username,'-p',params.password,services],stdout=PIPE,stderr=PIPE)
        out,err=cmd.communicate()
        Logger.info('Couchbase Add server: STDOUT=%s\nSTDERR=%s' % (out,err))
        Logger.info(str(cmd.returncode))

        if cmd.returncode > 0 :
           raise Fail('CB Cluster initialization failed')  
