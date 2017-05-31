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

import requests

try:
    import simplejson as json
    assert json
except ImportError:
    import json

from resource_management import *

class ServiceCheck(Script):
  def service_check(self, env):
    import params
    for host in params.es_master_hosts:
      url = "http://" + host + ":" + str(params.es_port) + "/_cluster/health"
      response = requests.get(url)
      if response.ok:
        break
    response.raise_for_status()
    parsed = json.loads(response.content)
    if not str(parsed['status']) == 'green':
      raise Fail(response.content)
    Logger.info(response.content)

if __name__ == "__main__":
  ServiceCheck().execute()
