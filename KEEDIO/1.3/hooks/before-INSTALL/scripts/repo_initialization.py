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
import json

# components_lits = repoName + postfix
_UBUNTU_REPO_COMPONENTS_POSTFIX = ["main"]

def _alter_repo(action, repo_string, repo_template):
  """
  @param action: "delete" or "create"
  @param repo_string: e.g. "[{\"baseUrl\":\"http://public-repo-1.hortonworks.com/HDP/centos6/2.x/updates/2.0.6.0\",\"osType\":\"centos6\",\"repoId\":\"HDP-2.0._\",\"repoName\":\"HDP\",\"defaultBaseUrl\":\"http://public-repo-1.hortonworks.com/HDP/centos6/2.x/updates/2.0.6.0\"}]"
  """
  repo_dicts = json.loads(repo_string)

  if not isinstance(repo_dicts, list):
    repo_dicts = [repo_dicts]

  for repo in repo_dicts:
    if not 'baseUrl' in repo:
      repo['baseUrl'] = None
    if not 'mirrorsList' in repo:
      repo['mirrorsList'] = None
    
    ubuntu_components = [ repo['repoName'] ] + _UBUNTU_REPO_COMPONENTS_POSTFIX
    
    if "keedio" in repo['repoName'].lower(): 
	template='repo_keedio.j2'
    else:
	template=repo_template
 

    Repository(repo['repoId'],
               action = action,
               base_url = repo['baseUrl'],
               mirror_list = repo['mirrorsList'],
               repo_file_name = repo['repoName'],
               #repo_template = repo_template,
               repo_template = template,
               components = ubuntu_components,
    )

def install_repos():
  from params import *
  import os.path
  if os.path.exists('/etc/sysconfig/rhn/systemid'):
      has_external_spacewalk = True
  if has_spacewalk_client :
       Repository('Spacewalk',
               action = 'create',
               base_url = spacewalk_pub_url,
               repo_file_name = 'Spacewalk',
               repo_template = 'spacewalk.j2',
               )
  elif has_external_spacewalk:
      Logger.info ('This machine is registered with a Red Hat satellite server, skipping repo creation') 
  else:  
      template = "repo_suse_rhel.j2" if System.get_instance().os_family in ["suse", "redhat"] else "repo_ubuntu.j2"
      _alter_repo("create", repo_info, template)
      if service_repo_info:
         _alter_repo("create", service_repo_info, template)



