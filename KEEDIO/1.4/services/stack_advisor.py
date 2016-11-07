#!/usr/bin/env ambari-python-wrap
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

import re
import sys
from math import ceil

from stack_advisor import DefaultStackAdvisor

class KEEDIO14StackAdvisor(DefaultStackAdvisor):

  def createComponentLayoutRecommendations(self, services, hosts):

    recommendations = {
      "blueprint": {
        "host_groups": [ ]
      },
      "blueprint_cluster_binding": {
        "host_groups": [ ]
      }
    }

    hostsList = [host["Hosts"]["host_name"] for host in hosts["items"]]

    hostsComponentsMap = {}
    for hostName in hostsList:
      if hostName not in hostsComponentsMap:
        hostsComponentsMap[hostName] = []
    couchbaseHosts=[]
    #extend 'hostsComponentsMap' with MASTER components
    for service in services["services"]:
      masterComponents = [component for component in service["components"] if self.isMasterComponent(component)]
      for component in masterComponents:
        componentName = component["StackServiceComponents"]["component_name"]

        if self.isComponentHostsPopulated(component):
          hostsForComponent = component["StackServiceComponents"]["hostnames"]
        else:

          if len(hostsList) > 1 and self.isMasterComponentWithMultipleInstances(component):
            hostsCount = self.getMinComponentCount(component)
            if hostsCount > 1: # get first 'hostsCount' available hosts
              hostsForComponent = []
              hostIndex = 0
              while hostsCount > len(hostsForComponent) and hostIndex < len(hostsList):
                currentHost = hostsList[hostIndex]
                if self.isHostSuitableForComponent(currentHost, component):
                  hostsForComponent.append(currentHost)
                hostIndex += 1
            else:
              hostsForComponent = [self.getHostForComponent(component, hostsList)]
          else:
            hostsForComponent = [self.getHostForComponent(component, hostsList)]
        if componentName=="COUCHBASE_SERVER" or componentName=="COUCHBASE_CLUSTERCREATOR":
           print hostsForComponent 
           print "ALESSIO "
           couchbaseHosts=couchbaseHosts+hostsForComponent
        #extend 'hostsComponentsMap' with 'hostsForComponent'
        for hostName in hostsForComponent:
          hostsComponentsMap[hostName].append( { "name":componentName } )
    #extend 'hostsComponentsMap' with Slave and Client Components
    componentsListList = [service["components"] for service in services["services"]]
    componentsList = [item for sublist in componentsListList for item in sublist]
    usedHostsListList = [component["StackServiceComponents"]["hostnames"] for component in componentsList if not self.isComponentNotValuable(component)]
    utilizedHosts = [item for sublist in usedHostsListList for item in sublist]
    freeHosts = [hostName for hostName in hostsList if hostName not in utilizedHosts]

    for service in services["services"]:
      slaveClientComponents = [component for component in service["components"]
                               if self.isSlaveComponent(component) or self.isClientComponent(component)]
      for component in slaveClientComponents:
        componentName = component["StackServiceComponents"]["component_name"]

        if self.isComponentHostsPopulated(component):
          hostsForComponent = component["StackServiceComponents"]["hostnames"]
        elif component["StackServiceComponents"]["cardinality"] == "ALL":
          hostsForComponent = hostsList
        elif componentName=="COUCHBASE_DATA" or componentName=="COUCHBASE_INDEXER" or componentName=="COUCHBASE_QUERY":
          hostsForComponent = couchbaseHosts
        else:
          if len(freeHosts) == 0:
            hostsForComponent = hostsList[-1:]
          else: # len(freeHosts) >= 1
            hostsForComponent = freeHosts
            if self.isClientComponent(component):
              hostsForComponent = freeHosts[0:1]

        #extend 'hostsComponentsMap' with 'hostsForComponent'
        for hostName in hostsForComponent:
          if hostName not in hostsComponentsMap:
            hostsComponentsMap[hostName] = []
          hostsComponentsMap[hostName].append( { "name": componentName } )

    #prepare 'host-group's from 'hostsComponentsMap'
    host_groups = recommendations["blueprint"]["host_groups"]
    bindings = recommendations["blueprint_cluster_binding"]["host_groups"]
    index = 0
    for key in hostsComponentsMap.keys():
      index += 1
      host_group_name = "host-group-{0}".format(index)
      host_groups.append( { "name": host_group_name, "components": hostsComponentsMap[key] } )
      bindings.append( { "name": host_group_name, "hosts": [{ "fqdn": key }] } )

    return recommendations
  pass
  def getComponentLayoutValidations(self, services, hosts):
    """Returns array of Validation objects about issues with hostnames components assigned to"""
    items = []

    # Validating NAMENODE and SECONDARY_NAMENODE are on different hosts if possible
    hostsList = [host["Hosts"]["host_name"] for host in hosts["items"]]
    hostsCount = len(hostsList)

    componentsListList = [service["components"] for service in services["services"]]
    componentsList = [item for sublist in componentsListList for item in sublist]
    nameNodeHosts = [component["StackServiceComponents"]["hostnames"] for component in componentsList if component["StackServiceComponents"]["component_name"] == "NAMENODE"]
    secondaryNameNodeHosts = [component["StackServiceComponents"]["hostnames"] for component in componentsList if component["StackServiceComponents"]["component_name"] == "SECONDARY_NAMENODE"]
    if hostsCount > 1 and len(nameNodeHosts) > 0 and len(secondaryNameNodeHosts) > 0:
      nameNodeHosts = nameNodeHosts[0]
      secondaryNameNodeHosts = secondaryNameNodeHosts[0]
      commonHosts = list(set(nameNodeHosts).intersection(secondaryNameNodeHosts))
      for host in commonHosts:
        items.append( { "type": 'host-component', "level": 'WARN', "message": 'NameNode and Secondary NameNode should not be hosted on same machine', "component-name": 'NAMENODE', "host": str(host) } )
        items.append( { "type": 'host-component', "level": 'WARN', "message": 'NameNode and Secondary NameNode should not be hosted on same machine', "component-name": 'SECONDARY_NAMENODE', "host": str(host) } )

    # Validation COUCHBASE_CLUSTERSTARTER and COUCHBASE_SERVER are on different hosts if possible
    cbClustercreatorHosts = [component["StackServiceComponents"]["hostnames"] for component in componentsList if component["StackServiceComponents"]["component_name"] == "COUCHBASE_CLUSTERCREATOR"]
    cbServerHosts = [component["StackServiceComponents"]["hostnames"] for component in componentsList if component["StackServiceComponents"]["component_name"] == "COUCHBASE_SERVER"]
    cbDataHosts = [component["StackServiceComponents"]["hostnames"] for component in componentsList if component["StackServiceComponents"]["component_name"] == "COUCHBASE_DATA"]
    cbIndexerHosts = [component["StackServiceComponents"]["hostnames"] for component in componentsList if component["StackServiceComponents"]["component_name"] == "COUCHBASE_INDEXER"]
    cbQueryHosts = [component["StackServiceComponents"]["hostnames"] for component in componentsList if component["StackServiceComponents"]["component_name"] == "COUCHBASE_QUERY"]
    if hostsCount > 1 and len(cbClustercreatorHosts) > 0 and len(cbServerHosts) > 0:
      cbClustercreatorHosts = cbClustercreatorHosts[0]
      cbServerHosts = cbServerHosts[0]
      cbDataHosts = cbDataHosts[0]
      cbIndexerHosts = cbIndexerHosts[0]
      cbQueryHosts = cbQueryHosts[0]
      commonHosts = list(set(cbClustercreatorHosts).intersection(cbServerHosts))
      for host in commonHosts:
        items.append( { "type": 'host-component', "level": 'ERROR', "message": 'Couchbase Cluster starter and Couchbase server must not be hosted on same machine', "component-name": 'COUCHBASE_CLUSTERSTARTER', "host": str(host) } )
        items.append( { "type": 'host-component', "level": 'ERROR', "message": 'Couchbase Cluster starter and Couchbase server must not be hosted on same machine', "component-name": 'COUCHBASE_SERVER', "host": str(host) } )
      for host in cbDataHosts: 
         if host not in cbServerHosts and host not in cbClustercreatorHosts:
            items.append( { "type": 'host-component', "level": 'ERROR', "message": 'Couchbase Data node must be hosted on the same machine of a Couchbase server', "component-name": 'COUCHBASE_DATA', "host": str(host) } )
      for host in cbIndexerHosts: 
         if host not in cbServerHosts and host not in cbClustercreatorHosts:
            items.append( { "type": 'host-component', "level": 'ERROR', "message": 'Couchbase Indexer node must be hosted on the same machine of a Couchbase server', "component-name": 'COUCHBASE_INDEXER', "host": str(host) } )
      for host in cbQueryHosts: 
         if host not in cbServerHosts and host not in cbClustercreatorHosts:
            items.append( { "type": 'host-component', "level": 'ERROR', "message": 'Couchbase Query node must be hosted on the same machine of a Couchbase server', "component-name": 'COUCHBASE_QUERY', "host": str(host) } )

      ClientHosts = [component["StackServiceComponents"]["hostnames"] for component in componentsList if component["StackServiceComponents"]["component_name"] == "SPACEWALK_CLIENT"]
      ClientHosts = ClientHosts[0]
      for host in hostsList: 
         if host not in ClientHosts:
            items.append( { "type": 'host-component', "level": 'ERROR', "message": 'Client component must be hosted on all the hosts', "component-name": 'SPACEWALK_CLIENT', "host": str(host) } )
            continue

    # Validating cardinality
    for component in componentsList:
      if component["StackServiceComponents"]["cardinality"] is not None:
         componentName = component["StackServiceComponents"]["component_name"]
         componentDisplayName = component["StackServiceComponents"]["display_name"]
         componentHostsCount = 0
         if component["StackServiceComponents"]["hostnames"] is not None:
           componentHostsCount = len(component["StackServiceComponents"]["hostnames"])
         cardinality = str(component["StackServiceComponents"]["cardinality"])
         # cardinality types: null, 1+, 1-2, 1, ALL
         message = None
         if "+" in cardinality:
           hostsMin = int(cardinality[:-1])
           if componentHostsCount < hostsMin:
             message = "At least {0} {1} components should be installed in cluster.".format(hostsMin, componentDisplayName)
         elif "-" in cardinality:
           nums = cardinality.split("-")
           hostsMin = int(nums[0])
           hostsMax = int(nums[1])
           if componentHostsCount > hostsMax or componentHostsCount < hostsMin:
             message = "Between {0} and {1} {2} components should be installed in cluster.".format(hostsMin, hostsMax, componentDisplayName)
         elif "ALL" == cardinality:
           if componentHostsCount != hostsCount:
             message = "{0} component should be installed on all hosts in cluster.".format(componentDisplayName)
         else:
           if componentHostsCount != int(cardinality):
             message = "Exactly {0} {1} components should be installed in cluster.".format(int(cardinality), componentDisplayName)

         if message is not None:
           items.append({"type": 'host-component', "level": 'ERROR', "message": message, "component-name": componentName})

    # Validating host-usage
    usedHostsListList = [component["StackServiceComponents"]["hostnames"] for component in componentsList if not self.isComponentNotValuable(component)]
    usedHostsList = [item for sublist in usedHostsListList for item in sublist]
    nonUsedHostsList = [item for item in hostsList if item not in usedHostsList]
    for host in nonUsedHostsList:
      items.append( { "type": 'host-component', "level": 'ERROR', "message": 'Host is not used', "host": str(host) } )

    return items

  def getServiceConfigurationRecommenderDict(self):
    return {
      "YARN": self.recommendYARNConfigurations,
      "MAPREDUCE2": self.recommendMapReduce2Configurations
    }

  def putProperty(self, config, configType):
    if configType not in config or "properties" not in config[configType]:
      config[configType] = {"properties": {}}
    def appendProperty(key, value):
      config[configType]["properties"][key] = str(value)
    return appendProperty

  def recommendYARNConfigurations(self, configurations, clusterData):
    putYarnProperty = self.putProperty(configurations, "yarn-site")
    putYarnProperty('yarn.nodemanager.resource.memory-mb', int(round(clusterData['containers'] * clusterData['ramPerContainer'])))
    putYarnProperty('yarn.scheduler.minimum-allocation-mb', int(clusterData['ramPerContainer']))
    putYarnProperty('yarn.scheduler.maximum-allocation-mb', int(round(clusterData['containers'] * clusterData['ramPerContainer'])))

  def recommendMapReduce2Configurations(self, configurations, clusterData):
    putMapredProperty = self.putProperty(configurations, "mapred-site")
    putMapredProperty('yarn.app.mapreduce.am.resource.mb', int(clusterData['amMemory']))
    putMapredProperty('yarn.app.mapreduce.am.command-opts', "-Xmx" + str(int(round(0.8 * clusterData['amMemory']))) + "m")
    putMapredProperty('mapreduce.map.memory.mb', clusterData['mapMemory'])
    putMapredProperty('mapreduce.reduce.memory.mb', int(clusterData['reduceMemory']))
    putMapredProperty('mapreduce.map.java.opts', "-Xmx" + str(int(round(0.8 * clusterData['mapMemory']))) + "m")
    putMapredProperty('mapreduce.reduce.java.opts', "-Xmx" + str(int(round(0.8 * clusterData['reduceMemory']))) + "m")
    putMapredProperty('mapreduce.task.io.sort.mb', min(int(round(0.4 * clusterData['mapMemory'])), 1024))

  def getConfigurationClusterSummary(self, servicesList, hosts, components):

    hBaseInstalled = False
    if 'HBASE' in servicesList:
      hBaseInstalled = True

    cluster = {
      "cpu": 0,
      "disk": 0,
      "ram": 0,
      "hBaseInstalled": hBaseInstalled,
      "components": components
    }

    if len(hosts["items"]) > 0:
      host = hosts["items"][0]["Hosts"]
      cluster["cpu"] = host["cpu_count"]
      cluster["disk"] = len(host["disk_info"])
      cluster["ram"] = int(host["total_mem"] / (1024 * 1024))

    ramRecommendations = [
      {"os":1, "hbase":1},
      {"os":2, "hbase":1},
      {"os":2, "hbase":2},
      {"os":4, "hbase":4},
      {"os":6, "hbase":8},
      {"os":8, "hbase":8},
      {"os":8, "hbase":8},
      {"os":12, "hbase":16},
      {"os":24, "hbase":24},
      {"os":32, "hbase":32},
      {"os":64, "hbase":64}
    ]
    index = {
      cluster["ram"] <= 4: 0,
      4 < cluster["ram"] <= 8: 1,
      8 < cluster["ram"] <= 16: 2,
      16 < cluster["ram"] <= 24: 3,
      24 < cluster["ram"] <= 48: 4,
      48 < cluster["ram"] <= 64: 5,
      64 < cluster["ram"] <= 72: 6,
      72 < cluster["ram"] <= 96: 7,
      96 < cluster["ram"] <= 128: 8,
      128 < cluster["ram"] <= 256: 9,
      256 < cluster["ram"]: 10
    }[1]
    cluster["reservedRam"] = ramRecommendations[index]["os"]
    cluster["hbaseRam"] = ramRecommendations[index]["hbase"]

    cluster["minContainerSize"] = {
      cluster["ram"] <= 4: 256,
      4 < cluster["ram"] <= 8: 512,
      8 < cluster["ram"] <= 24: 1024,
      24 < cluster["ram"]: 2048
    }[1]

    totalAvailableRam = cluster["ram"] - cluster["reservedRam"]
    if cluster["hBaseInstalled"]:
      totalAvailableRam -= cluster["hbaseRam"]
    cluster["totalAvailableRam"] = max(2048, totalAvailableRam * 1024)
    '''containers = max(3, min (2*cores,min (1.8*DISKS,(Total available RAM) / MIN_CONTAINER_SIZE))))'''
    cluster["containers"] = round(max(3,
                                min(2 * cluster["cpu"],
                                    min(ceil(1.8 * cluster["disk"]),
                                            cluster["totalAvailableRam"] / cluster["minContainerSize"]))))

    '''ramPerContainers = max(2GB, RAM - reservedRam - hBaseRam) / containers'''
    cluster["ramPerContainer"] = abs(cluster["totalAvailableRam"] / cluster["containers"])
    '''If greater than 1GB, value will be in multiples of 512.'''
    if cluster["ramPerContainer"] > 1024:
      cluster["ramPerContainer"] = int(cluster["ramPerContainer"] / 512) * 512

    cluster["mapMemory"] = int(cluster["ramPerContainer"])
    cluster["reduceMemory"] = cluster["ramPerContainer"]
    cluster["amMemory"] = max(cluster["mapMemory"], cluster["reduceMemory"])

    return cluster

  def getConfigurationsValidationItems(self, services, hosts):
    """Returns array of Validation objects about issues with configuration values provided in services"""
    items = []

    recommendations = self.recommendConfigurations(services, hosts)
    recommendedDefaults = recommendations["recommendations"]["blueprint"]["configurations"]

    configurations = services["configurations"]
    for service in services["services"]:
      serviceName = service["StackServices"]["service_name"]
      validator = self.validateServiceConfigurations(serviceName)
      if validator is not None:
        siteName = validator[0]
        method = validator[1]
        if siteName in recommendedDefaults:
          siteProperties = getSiteProperties(configurations, siteName)
          if siteProperties is not None:
            resultItems = method(siteProperties, recommendedDefaults[siteName]["properties"], configurations)
            items.extend(resultItems)
    return items

  def getServiceConfigurationValidators(self):
    return {
      "MAPREDUCE2": ["mapred-site", self.validateMapReduce2Configurations],
      "YARN": ["yarn-site", self.validateYARNConfigurations]
    }

  def validateServiceConfigurations(self, serviceName):
    return self.getServiceConfigurationValidators().get(serviceName, None)

  def toConfigurationValidationProblems(self, validationProblems, siteName):
    result = []
    for validationProblem in validationProblems:
      validationItem = validationProblem.get("item", None)
      if validationItem is not None:
        problem = {"type": 'configuration', "level": validationItem["level"], "message": validationItem["message"],
                   "config-type": siteName, "config-name": validationProblem["config-name"] }
        result.append(problem)
    return result

  def getWarnItem(self, message):
    return {"level": "WARN", "message": message}

  def getErrorItem(self, message):
    return {"level": "ERROR", "message": message}

  def validatorLessThenDefaultValue(self, properties, recommendedDefaults, propertyName):
    if not propertyName in properties:
      return self.getErrorItem("Value should be set")
    value = to_number(properties[propertyName])
    if value is None:
      return self.getErrorItem("Value should be integer")
    defaultValue = to_number(recommendedDefaults[propertyName])
    if defaultValue is None:
      return None
    if value < defaultValue:
      return self.getWarnItem("Value is less than the recommended default of {0}".format(defaultValue))
    return None

  def validateXmxValue(self, properties, recommendedDefaults, propertyName):
    if not propertyName in properties:
      return self.getErrorItem("Value should be set")
    value = properties[propertyName]
    defaultValue = recommendedDefaults[propertyName]
    if defaultValue is None:
      return self.getErrorItem("Config's default value can't be null or undefined")
    if not checkXmxValueFormat(value):
      return self.getErrorItem('Invalid value format')
    valueInt = formatXmxSizeToBytes(getXmxSize(value))
    defaultValueXmx = getXmxSize(defaultValue)
    defaultValueInt = formatXmxSizeToBytes(defaultValueXmx)
    if valueInt < defaultValueInt:
      return self.getWarnItem("Value is less than the recommended default of -Xmx" + defaultValueXmx)
    return None

  def validateMapReduce2Configurations(self, properties, recommendedDefaults, configurations):
    validationItems = [ {"config-name": 'mapreduce.map.java.opts', "item": self.validateXmxValue(properties, recommendedDefaults, 'mapreduce.map.java.opts')},
                        {"config-name": 'mapreduce.reduce.java.opts', "item": self.validateXmxValue(properties, recommendedDefaults, 'mapreduce.reduce.java.opts')},
                        {"config-name": 'mapreduce.task.io.sort.mb', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'mapreduce.task.io.sort.mb')},
                        {"config-name": 'mapreduce.map.memory.mb', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'mapreduce.map.memory.mb')},
                        {"config-name": 'mapreduce.reduce.memory.mb', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'mapreduce.reduce.memory.mb')},
                        {"config-name": 'yarn.app.mapreduce.am.resource.mb', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'yarn.app.mapreduce.am.resource.mb')},
                        {"config-name": 'yarn.app.mapreduce.am.command-opts', "item": self.validateXmxValue(properties, recommendedDefaults, 'yarn.app.mapreduce.am.command-opts')} ]
    return self.toConfigurationValidationProblems(validationItems, "mapred-site")

  def validateYARNConfigurations(self, properties, recommendedDefaults, configurations):
    validationItems = [ {"config-name": 'yarn.nodemanager.resource.memory-mb', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'yarn.nodemanager.resource.memory-mb')},
                        {"config-name": 'yarn.scheduler.minimum-allocation-mb', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'yarn.scheduler.minimum-allocation-mb')},
                        {"config-name": 'yarn.scheduler.maximum-allocation-mb', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'yarn.scheduler.maximum-allocation-mb')} ]
    return self.toConfigurationValidationProblems(validationItems, "yarn-site")

  def getMastersWithMultipleInstances(self):
    return ['ZOOKEEPER_SERVER', 'HBASE_MASTER', 'COUCHBASE_SERVER']

  def getNotValuableComponents(self):
    return ['JOURNALNODE', 'ZKFC', 'GANGLIA_MONITOR']

  def getNotPreferableOnServerComponents(self):
    return ['GANGLIA_SERVER', 'NAGIOS_SERVER']

  def getCardinalitiesDict(self):
    return {
      'ZOOKEEPER_SERVER': {"min": 3},
      'HBASE_MASTER': {"min": 1},
      }

  def getComponentLayoutSchemes(self):
    return {
     'NAMENODE': {"else": 0},
      'SECONDARY_NAMENODE': {"else": 1},
      'COUCHBASE_CLUSTERCREATOR': {3: 0, 6: 1,"else": 0},
      'COUCHBASE_SERVER': {3: 1, 6: 2,"else": 2},
      'HBASE_MASTER': {6: 0, 31: 2, "else": 3},

      'HISTORYSERVER': {31: 3, "else": 2},
      'RESOURCEMANAGER': {31: 3, "else": 2},

      'OOZIE_SERVER': {6: 1, 31: 8, "else": 3},

      'HIVE_SERVER': {6: 1, 31: 2, "else": 4},
      'HIVE_METASTORE': {6: 1, 31: 2, "else": 4},
      'WEBHCAT_SERVER': {6: 1, 31: 2, "else": 4},
      }

# Validation helper methods
def getSiteProperties(configurations, siteName):
  siteConfig = configurations.get(siteName)
  if siteConfig is None:
    return None
  return siteConfig.get("properties")

def to_number(s):
  try:
    return int(re.sub("\D", "", s))
  except ValueError:
    return None

def checkXmxValueFormat(value):
  p = re.compile('-Xmx(\d+)(b|k|m|g|p|t|B|K|M|G|P|T)?')
  matches = p.findall(value)
  return len(matches) == 1

def getXmxSize(value):
  p = re.compile("-Xmx(\d+)(.?)")
  result = p.findall(value)[0]
  if len(result) > 1:
    # result[1] - is a space or size formatter (b|k|m|g etc)
    return result[0] + result[1].lower()
  return result[0]

def formatXmxSizeToBytes(value):
  value = value.lower()
  if len(value) == 0:
    return 0
  modifier = value[-1]

  if modifier == ' ' or modifier in "0123456789":
    modifier = 'b'
  m = {
    modifier == 'b': 1,
    modifier == 'k': 1024,
    modifier == 'm': 1024 * 1024,
    modifier == 'g': 1024 * 1024 * 1024,
    modifier == 't': 1024 * 1024 * 1024 * 1024,
    modifier == 'p': 1024 * 1024 * 1024 * 1024 * 1024
    }[1]
  return to_number(value) * m

def getPort(address):
  """
  Extracts port from the address like 0.0.0.0:1019
  """
  if address is None:
    return None
  m = re.search(r'(?:http(?:s)?://)?([\w\d.]*):(\d{1,5})', address)
  if m is not None:
    return int(m.group(2))
  else:
    return None

def isSecurePort(port):
  """
  Returns True if port is root-owned at *nix systems
  """
  if port is not None:
    return port < 1024
  else:
    return False
