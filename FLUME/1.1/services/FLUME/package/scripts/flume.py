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

import glob
import json
import os
import re
from resource_management import *
from subprocess import *

def flume(action = None):
  import params
  import flume_extra 

  
  if action == 'config':
    # remove previously defined meta's
    for n in find_expected_agent_names():
      os.unlink(os.path.join(params.flume_conf_dir, n, 'ambari-meta.json'))

    Directory(params.flume_conf_dir, recursive=True)
    Directory(params.flume_log_dir, owner=params.flume_user)

    File(os.path.join(params.flume_conf_dir, 'log4j.properties'),
      content=StaticFile("log4j.properties"))

    flume_agents = {}
    if params.flume_conf_content is not None:
      flume_agents = build_flume_topology(params.flume_conf_content)

    if params.flume_env_content is not None:
      flume_agents_env = build_flume_env(params.flume_env_content)

    for agent in flume_agents.keys():
      flume_meta_file = os.path.join(params.flume_conf_dir, 'ambari-meta_%s.json' % agent )
      File(flume_meta_file,
        content = json.dumps(ambari_meta(agent, flume_agents[agent])),
        mode = 0644)
      flume_env = flume_agents_env[agent] if flume_agents_env.has_key(agent) else flume_agents_env['default']
      File(os.path.join(params.flume_agent_conf_dir,'%s.sh' % agent),
        content = InlineTemplate(flume_env),
        mode = 0644)
      flume_agent_conf_file = os.path.join(params.flume_agent_conf_dir, '%s.conf' % agent)

      PropertiesFile(flume_agent_conf_file,
        properties=flume_agents[agent],
        mode = 0644)

    if params.flume_extra is not None:
      #import jsonschema
      #File('/tmp/flume_extra.schema',
      #  content=StaticFile("flume_extra.schema"))
      #flume_extra_schema = json.loads(open('/tmp/flume_extra.schema').read())

      for extra_file_raw in params.flume_extra.values():
        extra_file=json.loads(extra_file_raw)
        if not extra_file.has_key('path'):
          raise Exception("path field is required")
        File(extra_file['path'],
          mode = int(extra_file['mode'],8),
          owner = extra_file['owner'],
          group = extra_file['group'],
          content=extra_file['content']
        )

  if action == "start" or action == "stop" or action == "status":
    executed = Popen(["service","flume-agent",action],stdout=PIPE,stderr=PIPE)
    out,err = executed.communicate()
    if action == "status":
      from utils import check_rc
      rc = executed.returncode
      check_rc(rc,out,err)
    if action == "stop":
      filelist = glob.glob(params.flume_agent_conf_dir+"/*.conf")
      for f in filelist:
        os.remove(f)


def ambari_meta(agent_name, agent_conf):
  res = {}

  sources = agent_conf[agent_name + '.sources'].split(' ')
  res['sources_count'] = len(sources)

  sinks = agent_conf[agent_name + '.sinks'].split(' ')
  res['sinks_count'] = len(sinks)


  sources = agent_conf[agent_name + '.sources'].split(' ')
  res['sources_count'] = len(sources)

  sinks = agent_conf[agent_name + '.sinks'].split(' ')
  res['sinks_count'] = len(sinks)

  channels = agent_conf[agent_name + '.channels'].split(' ')
  res['channels_count'] = len(channels)

  return res

# define a map of dictionaries, where the key is agent name
# and the dictionary is the name/value pair
def build_flume_topology(content):

  result = {}
  agent_names = []

  for line in content.split('\n'):
    rline = line.strip()
    if 0 != len(rline) and not rline.startswith('#'):
      pair = rline.split('=')
      lhs = pair[0].strip()
      rhs = pair[1].strip()

      part0 = lhs.split('.')[0]

      if lhs.endswith(".sources"):
        agent_names.append(part0)

      if not result.has_key(part0):
        result[part0] = {}

      result[part0][lhs] = rhs

  # trim out non-agents
  for k in result.keys():
    if not k in agent_names:
      del result[k]


  return result

def build_flume_env(flume_env_content):
  all_env=dict()
  pattern = re.compile('###\s*(\w[\-\w]*)\s*###')
  agent="default"
  current_env=""
  for line in flume_env_content.split('\n'):
    match = pattern.match(line)
    if match is not None:
      all_env[agent]=current_env
      agent=match.group(1)
      current_env=""
    else:
      current_env+="\n"+line
  all_env[agent]=current_env
  return all_env

def is_live(pid_file):
  live = False

  try:
    check_process_status(pid_file)
    live = True
  except ComponentIsNotRunning:
    pass

  return live

def live_status(pid_file):
  import params

  pid_file_part = pid_file.split(os.sep).pop()

  res = {}
  res['name'] = pid_file_part
  
  if pid_file_part.endswith(".pid"):
    res['name'] = pid_file_part[:-4]

  res['status'] = 'RUNNING' if is_live(pid_file) else 'NOT_RUNNING'
  res['sources_count'] = 0
  res['sinks_count'] = 0
  res['channels_count'] = 0

  flume_agent_conf_dir = params.flume_conf_dir + os.sep + res['name']
  flume_agent_meta_file = flume_agent_conf_dir + os.sep + 'ambari-meta.json'

  try:
    with open(flume_agent_meta_file) as fp:
      meta = json.load(fp)
      res['sources_count'] = meta['sources_count']
      res['sinks_count'] = meta['sinks_count']
      res['channels_count'] = meta['channels_count']
  except:
    pass

  return res
  
def flume_status():
  import params

  meta_files = find_expected_agent_names()
  pid_files = []
  for agent_name in meta_files:
    pid_files.append(os.path.join(params.flume_run_dir, agent_name + '.pid'))

  procs = []
  for pid_file in pid_files:
    procs.append(live_status(pid_file))

  return procs

# these are what Ambari believes should be running
def find_expected_agent_names():
  import params

  files = glob.glob(params.flume_conf_dir + os.sep + "*/ambari-meta.json")
  expected = []

  for f in files:
    expected.append(os.path.dirname(f).split(os.sep).pop())

  return expected

def cmd_target_names():
  import params

  if len(params.flume_command_targets) > 0:
    return params.flume_command_targets
  else:
    return find_expected_agent_names()

def _set_desired_state(state):
  import params
  try:
    with open(os.path.join(params.flume_run_dir, 'ambari-state.txt'), 'w') as fp:
      fp.write(state)
  except:
    pass

def get_desired_state():
  import params
