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
import os

def config():
  import params

  File("/etc/init.d/gmond",
            content=StaticFile("gmond.init"),
            mode=0755
  )

def generate_daemon(ganglia_service,
                    name=None,
                    role=None,
                    owner=None,
                    group=None):
  import params
  import functions
  for gmond_server in params.ganglia_clusters:
    Logger.info(gmond_server) 
    if gmond_server[0] == name:
      gmond_port = gmond_server[1]
      break
  params.gmond_server=gmond_server[0]
  params.gmond_port=gmond_server[1]
  cmd = ""
  if ganglia_service == "gmond":
    # When multi daemon gmond where packaged, should be changeb by only a synbolic link with service name
    File("/etc/init.d/gmond." + name,
      content=StaticFile("gmond.init"),
      mode=0755 )
    functions.turn_off_autostart("gmond."+name)
    if name == "ElasticSearch":
      File("/etc/ganglia/conf.d/elasticsearch.pyconf",
        content=Template("elasticsearch.pyconf.j2"),
        mode=0644)
      File("/usr/lib64/ganglia/python_modules/elasticsearch.py",
        content=StaticFile("elasticsearch.py"),
          mode=0644)
      File("/etc/ganglia/gmond.ElasticSearch.conf",
        content=Template("gmond.ElasticSearch.j2",
          clusterName=name,
          gmond_server=params.ganglia_server_host,
          gmond_port=gmond_port,
          is_master_server=role=="server"),
        mode=0644)
    else:
      File("/etc/ganglia/gmond."+name+".conf",
        content=Template("gmond.conf.j2",
          clusterName=name,
          gmond_server=params.ganglia_server_host,
          gmond_port=gmond_port,
          is_master_server=role=="server"),
        mode=0644)
    Directory("/var/run/gmond",
      owner="root",
      group="root",
      recursive=True
    )
    
  elif ganglia_service == "gmetad":
    File("/etc/ganglia/gmetad.conf",
      content=Template("gmetad.conf.j2",gridName="KEEDIO"),
      mode=0644 )
    functions.turn_off_autostart("gmetad")
    """
    Directory("/var/lib/ganglia-web/dwoo/compiled",
      owner="apache",
      group="apache",
      recursive=True
    )
    Directory("/var/lib/ganglia-web/dwoo/cache",
      owner="apache",
      group="apache",
      recursive=True
    )
    Directory("/var/lib/ganglia-web/conf/",
      owner="apache",
      group="apache",
      recursive=True
    )
    """
  else:
    raise Fail("Unexpected ganglia service")
  Execute(format(cmd),
          path=[params.ganglia_shell_cmds_dir, "/usr/sbin",
                "/sbin:/usr/local/bin", "/bin", "/usr/bin"]
  )

