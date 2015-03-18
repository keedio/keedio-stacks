from resource_management import *
from subprocess import *

def kafka(action):
  import utils
  import params
  if action == 'config':
    utils.os_mkdir(params.log_dirs,owner='kafka')
    kafka_server_properties = "broker.id=" + str(params.kafka_id) + "\n"
    for param in params.kafka_conf.keys():
      kafka_server_properties+=param+"="+str(params.kafka_conf[param])+"\n"
    File('/etc/kafka/conf/server.properties',
      content=kafka_server_properties)
    #  owner='kafka',
    #  group='kafka')
  elif action == 'start' or action == 'stop' or action == 'status' :
    executed = Popen(["service","kafka",action],stdout=PIPE,stderr=PIPE)    
    out,err = executed.communicate()

    if action == "status":
      rc = executed.returncode
      utils.check_rc(rc,out,err)

