#!/usr/bin/env python

'''
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
'''

import optparse
import subprocess
import json

RESOURCEMANAGER = 'rm'
NODEMANAGER = 'nm'
HISTORYSERVER = 'hs'

STARTED_STATE = 'STARTED'
RUNNING_STATE = 'RUNNING'

#Return reponse for given path and address
def get_response(path, address, ssl_enabled):

  command = "curl"
  httpGssnegotiate = "--negotiate"
  userpswd = "-u:"
  insecure = "-k"# This is smoke test, no need to check CA of server
  if ssl_enabled:
    url = 'https://' + address + path
  else:
    url = 'http://' + address + path
      
  command_with_flags = [command,httpGssnegotiate,userpswd,insecure,url]

  proc = subprocess.Popen(command_with_flags, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  (stdout, stderr) = proc.communicate()
  response = json.loads(stdout)
  if response == None:
    print 'There is no response for url: ' + str(url)
    raise Exception('There is no response for url: ' + str(url))
  return response

#Verify that REST api is available for given component
def validate_availability(component, path, addresses, ssl_enabled):
  responses = {}
  for address in addresses.split(','):
    try:
      responses[address] = get_response(path, address, ssl_enabled)
    except Exception as e:
      print 'Error checking availability status of component.', e

  if not responses:
    exit(1)

  is_valid = validate_availability_response(component, responses.values()[0])
  if not is_valid:
    exit(1)

#Validate component-specific response
def validate_availability_response(component, response):
  rc = False
  try:
    if component == RESOURCEMANAGER:
      rc = response['clusterInfo']['state'] == STARTED_STATE
    elif component == NODEMANAGER:
      rc = bool(response['nodeInfo']['nodeHealthy'])
    elif component == HISTORYSERVER:
      rc = response['historyInfo']['startedOn'] > 0
  except Exception as e:
    print 'Error validation of availability response for ' + str(component), e
  return rc

#Verify that component has required resources to work
def validate_ability(component, path, addresses, ssl_enabled):
  responses = {}
  for address in addresses.split(','):
    try:
      responses[address] = get_response(path, address, ssl_enabled)
    except Exception as e:
      print 'Error checking ability of component.', e

  if not responses:
    exit(1)

  is_valid = validate_ability_response(component, responses.values()[0])
  if not is_valid:
    exit(1)

#Validate component-specific response that it has required resources to work
def validate_ability_response(component, response):
  try:
    if component == RESOURCEMANAGER:
      nodes = []
      if response.has_key('nodes') and not response['nodes'] == None and response['nodes'].has_key('node'):
        nodes = response['nodes']['node']
      connected_nodes_count = len(nodes)
      if connected_nodes_count == 0:
        print 'There is no connected nodemanagers to resourcemanager'
        return False
      active_nodes = filter(lambda x: x['state'] == RUNNING_STATE, nodes)
      active_nodes_count = len(active_nodes)

      if connected_nodes_count == 0:
        print 'There is no connected active nodemanagers to resourcemanager'
        return False
      else:
        return True
    else:
      return False
  except Exception as e:
    print 'Error validation of ability response', e
    return False

#
# Main.
#
def main():
  parser = optparse.OptionParser(usage="usage: %prog [options] component ")
  parser.add_option("-p", "--port", dest="address", help="Host:Port for REST API of a desired component")
  parser.add_option("-s", "--ssl", dest="ssl_enabled", help="Is SSL enabled for UI of component")

  (options, args) = parser.parse_args()

  component = args[0]
  
  address = options.address
  ssl_enabled = (options.ssl_enabled) in 'true'
  if component == RESOURCEMANAGER:
    path = '/ws/v1/cluster/info'
  elif component == NODEMANAGER:
    path = '/ws/v1/node/info'
  elif component == HISTORYSERVER:
    path = '/ws/v1/history/info'
  else:
    parser.error("Invalid component")

  validate_availability(component, path, address, ssl_enabled)

  if component == RESOURCEMANAGER:
    path = '/ws/v1/cluster/nodes'
    validate_ability(component, path, address, ssl_enabled)

if __name__ == "__main__":
  main()
