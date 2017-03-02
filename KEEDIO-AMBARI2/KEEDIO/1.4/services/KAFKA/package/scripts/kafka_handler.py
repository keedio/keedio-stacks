from resource_management import *
from subprocess import *

def kafka(action):
  import utils
  # FIX: When status is checked params  shouldn't be called
  if action != 'status':
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
        File('/etc/default/kafka-systemd.sh',
          content=StaticFile('kafka-systemd.profiles.d'))
      File('/etc/kafka/conf/server.properties',
        content=kafka_server_properties,
        owner='kafka',
        group='kafka')
      #if params.has_ganglia_server:
      #  File('/etc/jmxtrans/config/jmxtrans.config',
      #    content=Template('jmxtrans.j2')
      #  )
#        File('/etc/jmxtrans/config/KafkaMetrics.json',
      File('/var/lib/jmxtrans/KafkaMetrics.json',
          content=Template('KafkaMetrics.json.j2')
        )
    elif action == 'start' or action == 'stop':
      executed = Popen(["service","kafka",action],stdout=PIPE,stderr=PIPE)
      out,err = executed.communicate()
      Logger.info("Kafka service:")
      Logger.info(action) 
      Logger.info(str(out))
      Logger.info(str(err))
      if params.has_ganglia_server:
        executed2=Popen(["service","jmxtrans",action])
        out,err = executed2.communicate()
        Logger.info("JMXtrans service")
        Logger.info(action)
        Logger.info(str(out))
        Logger.info(str(err))
  elif action == "status":
    executed = Popen(["service","kafka",action],stdout=PIPE,stderr=PIPE)
    out,err = executed.communicate()
    rc = executed.returncode
    utils.check_rc(rc,out,err)

