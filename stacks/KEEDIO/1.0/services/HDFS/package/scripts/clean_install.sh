#!/bin/bash
ssh ambari1 service hadoop-hdfs-namenode stop
ssh ambari2 service hadoop-hdfs-datanode stop
ssh ambari2 rm -rf /hadoop/hdfs/data/current
ssh ambari3 service hadoop-hdfs-datanode stop
ssh ambari3 rm -rf /hadoop/hdfs/data/current
ssh ambari1 rm -rf /usr/lib/hadoop/namenode/*
ssh ambari1 rm -rf /hadoop/hdfs/namenode/*
mysql -e "drop database ambari;create database ambari; use ambari; source /var/lib/ambari-server/resources/Ambari-DDL-MySQL-CREATE.sql;"
service ambari-server restart
