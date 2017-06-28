from resource_management import *
from subprocess import *
import os

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
      for param in params.kafka_topic_conf.keys():
        value=params.kafka_topic_conf[param]
        if type(value)==bool:
          value=str(params.kafka_topic_conf[param]).lower()+"\n"
        else:
          value=str(params.kafka_topic_conf[param])+"\n"
        kafka_server_properties+=param+"="+value

      if params.has_metric_collector:
          kafka_server_properties+="kafka.metrics.reporters=org.apache.hadoop.metrics2.sink.kafka.KafkaTimelineMetricsReporter\n"
          kafka_server_properties+="kafka.timeline.metrics.reporter.enabled=true\n"
          kafka_server_properties+="kafka.timeline.metrics.hosts="+params.ams_collector_hosts+"\n"
          kafka_server_properties+="kafka.timeline.metrics.port="+params.metric_collector_port+"\n"
          kafka_server_properties+="kafka.timeline.metrics.protocol="+params.metric_collector_protocol+"\n"

      File('/etc/default/kafka-systemd.sh',
          content=StaticFile('kafka-systemd.profiles.d'))
      File('/etc/kafka/conf/server.properties',
        content=kafka_server_properties,
        owner='kafka',
        group='kafka')
      #Create symlinks in Kafka lib dir to include ambari-metrics jars
      # Temporary until the links will be created in rpm
      if os.path.exists("/usr/lib/ambari-metrics-kafka-sink") and params.has_metric_collector:
         Link("/usr/lib/kafka/libs/ambari-metrics-kafka-sink.jar",
            to="/usr/lib/ambari-metrics-kafka-sink/ambari-metrics-kafka-sink.jar",
             )
         Link("/usr/lib/kafka/libs/commons-collections-3.2.2.jar",
            to="/usr/lib/ambari-metrics-kafka-sink/lib/commons-collections-3.2.2.jar",
             )
	 Link("/usr/lib/kafka/libs/commons-lang-2.6.jar",
            to="/usr/lib/ambari-metrics-kafka-sink/lib/commons-lang-2.6.jar",
             )
         Link("/usr/lib/kafka/libs/commons-logging-1.1.1.jar",
            to="/usr/lib/ambari-metrics-kafka-sink/lib/commons-logging-1.1.1.jar",
             )
      if params.has_ganglia_server:
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

