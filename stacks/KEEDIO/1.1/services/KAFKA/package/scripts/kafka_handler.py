from resource_management import *
from subprocess import *

def kafka(action):
  import utils
  import params
  if action == 'config':
    utils.os_mkdir(params.log_dirs,owner='kafka')
    kafka_server_properties = "broker.id=" + str(params.kafka_id) + "\n"
    for param in params.kafka_conf.keys():
      value=params.kafka_conf[param]
      if type(value)==bool:
        value=str(params.kafka_conf[param]).lower()+"\n"
      else:
        value=str(params.kafka_conf[param])+"\n"
      kafka_server_properties+=param+"="+value
    if params.has_ganglia_server:
      File('/etc/profile.d/kafka.sh',
        content=StaticFile('kafka.profiles.d')
      )
    File('/etc/kafka/conf/server.properties',
      content=kafka_server_properties,
      owner='kafka',
      group='kafka')
    if params.has_ganglia_server:
      File('/etc/jmxtrans/config/jmxtrans.config',
        content=Template('jmxtrans.j2')
      )
      File('/etc/jmxtrans/config/KafkaMetrics.json',
        content=StaticFile('KafkaMetrics.json')
      )
  elif action == 'start' or action == 'stop' or action == 'status' :
    executed = Popen(["service","kafka",action],stdout=PIPE,stderr=PIPE)
    if params.has_ganglia_server:
        Popen(["service","jmxtrans",action])

  if action == "status":
    out,err = executed.communicate()
    rc = executed.returncode
    utils.check_rc(rc,out,err)

