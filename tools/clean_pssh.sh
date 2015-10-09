#!/bin/bash
service=""
while [ $# -gt 0 ]; do
  case $1 in
    "--service"|"-s")
      service=$2
      shift
      shift
      ;;
    "--full"|"-f")
      full=True
      shift
      ;;
    *)
      echo "Invalid argument $1"
      exit 1
      ;;
  esac
done

host_file="/root/all"

set -xv

if [ "$service" = "cassandra" ]||[ -n "$full" ]; then
  pssh -h $host_file "service cassandra stop"
  pssh -h $host_file "rpm -e cassandra --noscripts"
  pssh -h $host_file "rm -rf /var/lib/cassandra/*"
fi

if [ "$service" = "elasticsearch" ]||[ -n "$full" ]; then
  pssh -h $host_file "service elasticsearch stop"
  pssh -h $host_file "service kibana4 stop"
  pssh -h $host_file "service httpd stop"
  pssh -h $host_file "yum remove -y elasticsearch kibana kibana4"
  pssh -h $host_file "rm -rf /etc/elasticsearch /etc/sysconfig/elasticsearch /etc/httpd/conf.d/kibana* /etc/kibana*"
fi
if [ "$service" = "flume" ]||[ -n "$full" ]; then  
  pssh -h $host_file "service flume-agent stop &>/dev/null"
  pssh -h $host_file "rm -f /etc/flume/conf.d/*"
fi

if [ "$service" = "kafka" ]||[ -n "$full" ]; then
  pssh -h $host_file "service kafka stop"
  pssh -h $host_file "service zookeeper-server stop"
  pssh -h $host_file "service jmxtrans stop"
  pssh -h $host_file "rm -rf /hadoop/zookeeper/*"

  pssh -h $host_file "yum remove -y kafka zookeeper-server zookeeper &>/dev/null"
  pssh -h $host_file "rm -rf /kafka-logs"
fi

if [ "$service" = "oozie" ]||[ -n "$full" ]; then
  pssh -h $host_file "service oozie stop &>/dev/null"
  pssh -h $host_file "yum remove -y oozie oozie-client &>/dev/null"
fi

if [ "$service" = "ganglia" ]||[ -n "$full" ]; then
  pssh -h $host_file "service gmond stop &>/dev/null"
  pssh -h $host_file "service gmond.Slaves stop &>/dev/null"
  pssh -h $host_file "service gmond.DataNode stop &>/dev/null"
  pssh -h $host_file "service gmond.FlumeServer stop &>/dev/null"
  pssh -h $host_file "service gmond.HistoryServer stop &>/dev/null"
  pssh -h $host_file "service gmond.NameNode stop &>/dev/null"
  pssh -h $host_file "service gmond.NodeManager stop &>/dev/null"
  pssh -h $host_file "service gmond.ResourceManager stop &>/dev/null"
  pssh -h $host_file "service gmetad stop &>/dev/null"
  pssh -h $host_file "rm -rf /etc/init.d/gmond.* &>/dev/null"
  pssh -h $host_file "rm -rf /etc/init.d/gmond-* &>/dev/null"
  pssh -h $host_file "rm -rf /etc/ganglia &>/dev/null"
  pssh -h $host_file "yum remove -y ganglia-gmond ganglia-gmetad ganglia-devel ganglia &>/dev/null"
fi

# HUE
if [ "$service" = "hue" ]||[ -n "$full" ]; then
  pssh -h $host_file "service hue stop"
  pssh -h $host_file "yum remove -y hue-common"
  pssh -h $host_file "rm -rf /etc/hue"
  mysql --password=C3d14nt -e "drop database hue;create database hue; grant ALL ON hue.* to 'hue'@'%';"
fi

# HIVE
if [ "$service" = "hive" ]||[ -n "$full" ]; then
  pssh -h $host_file "service hive-server2 stop &>/dev/null"
  pssh -h $host_file "service hive-metastore stop &>/dev/null"
  mysql --password=C3d14nt -e "drop database hive_meta;create database hive_meta; grant ALL ON hive_meta.* to 'hive'@'%';"
fi

if [ "$service" = "hdfs" ]||[ -n "$full" ]; then
  pssh -h $host_file "service hadoop-mapreduce-historyserver stop &>/dev/null"
  pssh -h $host_file "service hadoop-yarn-nodemanager stop &>/dev/null"
  pssh -h $host_file "service hadoop-yarn-resourcemanager stop &>/dev/null"
  pssh -h $host_file "service monit stop &>/dev/null"
  pssh -h $host_file "service hadoop-hdfs-secondarynamenode stop &>/dev/null"
  pssh -h $host_file "service hadoop-hdfs-zkfc stop &>/dev/null"
  pssh -h $host_file "service hadoop-hdfs-namenode stop &>/dev/null"
  pssh -h $host_file "service hadoop-hdfs-journalnode stop &>/dev/null"
  pssh -h $host_file "service hadoop-hdfs-datanode stop &>/dev/null"
  pssh -h $host_file "service zookeeper-rest stop &>/dev/null"
  pssh -h $host_file "service zookeeper-server stop &>/dev/null"
  pssh -h $host_file "rm -rf /var/lib/hadoop-hdfs/formatted"

  if [ -n "$full" ] ; then
    pssh -h $host_file "yum remove -y hadoop zookeeper-server storm hadoop-libhdfs zookeeper hadoop-hdfs-zkfc storm-nimbus hadoop-hdfs zookeeper-rest hadoop-hdfs-datanode hadoop-hdfs-journalnode storm-drcp &>/dev/null"

    pssh -h $host_file "rm -rf /etc/hadoop"
    pssh -h $host_file "rm -rf /etc/zookeeper"
    pssh -h $host_file "rm -rf /etc/storm"

    pssh -h $host_file "rm -rf /var/run/hadoop"
    pssh -h $host_file "rm -rf /var/run/zookeeper"
    pssh -h $host_file "rm -rf /var/run/hadoop-hdfs"

    pssh -h $host_file "rm -rf /var/log/hadoop"
    pssh -h $host_file "rm -rf /var/log/zookeeper"
    pssh -h $host_file "rm -rf /var/log/storm"
    pssh -h $host_file "rm -rf /var/log/hadoop-hdfs"

    pssh -h $host_file "rm -rf /usr/lib/hadoop"
    pssh -h $host_file "rm -rf /usr/lib/oozie"
    pssh -h $host_file "rm -rf /usr/lib/zookeeper"
    pssh -h $host_file "rm -rf /usr/lib/storm"
    pssh -h $host_file "rm -rf /usr/lib/hadoop-hdfs"

    pssh -h $host_file "rm -rf /var/lib/zookeeper"
    pssh -h $host_file "rm -rf /var/lib/hadoop-hdfs"
    pssh -h $host_file "rm -rf /var/lib/hdfs"
    pssh -h $host_file "rm -rf /var/lib/oozie"
  fi

  pssh -h $host_file "rm -rf /tmp/hadoop-hdfs"

  pssh -h $host_file "rm -rf /hadoop/zookeeper/*"
  pssh -h $host_file "rm -rf /hadoop/hdfs/*"
  pssh -h $host_file "rm -rf /etc/default/hadoop*"

fi

mysql -e "drop database ambari;create database ambari; use ambari; source /var/lib/ambari-server/resources/Ambari-DDL-MySQL-CREATE.sql;"
service ambari-server stop &>/dev/null
service ambari-server start &>/dev/null
pssh -h /root/all "service ambari-agent restart"
