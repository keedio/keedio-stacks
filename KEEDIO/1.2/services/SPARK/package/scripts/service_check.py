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

from resource_management import *
from functools import partial
from utils import *
from spark import spark

class ServiceCheck(Script):
  def service_check(self, env):
    import params
    env.set_params(params)
    spark(action="config")
    execute_spark = partial(execute_sudo_krb,user=params.spark_user,principal=params.spark_principal,keytab=params.spark_keytab)
    check_spark = [ "source","/etc/profile.d/hadoop-env.sh","&&",params.spark_local_home+"/bin/spark-submit","--class","org.apache.spark.examples.SparkPi",params.spark_local_home+"/lib/"+params.spark_examples_jar,"10"]
    out,err,rc=execute_spark(check_spark)
    check_rc(rc,stdout=out,stderr=err)

if __name__ == "__main__":
  ServiceCheck().execute()
