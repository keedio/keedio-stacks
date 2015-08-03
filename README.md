keedio-stacks
=============

Ambari Stacks made by keedio
Currently deploying a cluster without HDFS is only possible if are modified javascript codo in order to dissable FS check. It can be done modifiying:

app.js.gz
--    this.fileSystemServiceValidation();
++    //this.fileSystemServiceValidation();

As our flume agent is a little bit different than standard, it can lunch as many agent as configuration files in /etc/flume/conf.d, we need also deploy
flume-env.sh files (which have been renamed to [agent-name].sh). To do so, in flume-env configuration content we can introduce 
### agentname ### 
to separate personalized flume-env, if ommited default will be used. Default is considered the first block in the context before any "magical tag".
If magical tag default is introduced it will override the initial one if exists.
If a magical tag is declared more than once, last one will take precedence.

It is possible to deploy extra files with flume. TO do it, in section "Custom flume-extra"->Add Property-> key=IGNORED, VALUE="json with schema https://github.com/keedio/keedio-stacks/tree/development/stacks/FLUME/1.1/services/FLUME/package/files/flume_schema.schema"
