import sys, os, pwd, grp, signal, time, glob, socket
from resource_management import *
from subprocess import call

reload(sys)
sys.setdefaultencoding('utf8')

class Master(Script):
  def install(self, env):

    import params
    import status_params

    Execute('echo master config dump: ' + str(', '.join(params.master_configs)))

    #Create user and group if they don't exist
    self.create_linux_user(params.nifi_user, params.nifi_group)
    if params.nifi_user != 'root':
      Execute('cp /etc/sudoers /etc/sudoers.bak')        
      Execute('echo "'+params.nifi_user+'    ALL=(ALL)       NOPASSWD: ALL" >> /etc/sudoers')
      Execute('echo Creating ' +  params.nifi_log_dir +  ' ' +  status_params.nifi_pid_dir)

    #create the log dir if it not already present
    Directory([status_params.nifi_pid_dir, params.nifi_log_dir],
            owner=params.nifi_user,
            group=params.nifi_group,
            recursive=True
    )

    Execute('touch ' +  params.nifi_log_file, user=params.nifi_user)
    Execute('rm -rf ' + params.nifi_dir, ignore_failures=True)
    Execute('mkdir -p '+params.nifi_dir)
    
    Directory([params.nifi_dir],
            owner=params.nifi_user,
            group=params.nifi_group,
            recursive=True
    )          
    
    Execute('echo Installing packages')

    # Install packages listed in metainfo.xml
    self.install_packages(env)

    #update the configs specified by user
    self.configure(env, True)

    
  def create_linux_user(self, user, group):
    try: pwd.getpwnam(user)
    except KeyError: Execute('adduser ' + user)
    try: grp.getgrnam(group)
    except KeyError: Execute('groupadd ' + group)

  

  def configure(self, env, isInstall=False):
    import params
    import status_params
    env.set_params(params)
    env.set_params(status_params)
    
    self.set_conf_bin(env)
    
    #write out nifi.properties
    params.nifi_properties_content=params.nifi_properties_content.replace("{{nifi_host}}",socket.getfqdn())
    File(format("{params.conf_dir}/nifi.properties"), content=InlineTemplate(params.nifi_properties_content), owner=params.nifi_user, group=params.nifi_group) # , mode=0777)

    #write out boostrap.conf
    bootstrap_content=InlineTemplate(params.nifi_boostrap_content)
    File(format("{params.conf_dir}/bootstrap.conf"), content=bootstrap_content, owner=params.nifi_user, group=params.nifi_group) 

    #write out logback.xml
    logback_content=InlineTemplate(params.nifi_logback_content)
    File(format("{params.conf_dir}/logback.xml"), content=logback_content, owner=params.nifi_user, group=params.nifi_group) 
    
    
    
  def stop(self, env):
    import params
    import status_params    
    self.set_conf_bin(env)    
    Execute (params.bin_dir+'/nifi.sh stop >> ' + params.nifi_log_file, user=params.nifi_user)
    Execute ('rm ' + status_params.nifi_pid_file)
 
      
  def start(self, env):
    import params
    import status_params
    self.configure(env) 
    self.set_conf_bin(env)    
    Execute('echo nifi nodes: ' + params.nifi_hosts)
    Execute('echo pid file ' + status_params.nifi_pid_file)
    Execute('echo JAVA_HOME=' + params.jdk64_home)

    Execute ('export JAVA_HOME='+params.jdk64_home+';'+params.bin_dir+'/nifi.sh start >> ' + params.nifi_log_file, user=params.nifi_user)

    Execute('cat '+params.bin_dir+'/nifi.pid'+" | grep pid | sed 's/pid=\(\.*\)/\\1/' > " + status_params.nifi_pid_file)
    Execute('chown '+params.nifi_user+':'+params.nifi_group+' ' + status_params.nifi_pid_file)
    
  def status(self, env):
    import status_params       
    check_process_status(status_params.nifi_pid_file)

  def install_mvn_repo(self):
    #for centos/RHEL 6/7 maven repo needs to be installed
    distribution = platform.linux_distribution()[0].lower()
    if distribution in ['centos', 'redhat'] and not os.path.exists('/etc/yum.repos.d/epel-apache-maven.repo'):
      Execute('curl -o /etc/yum.repos.d/epel-apache-maven.repo https://repos.fedorapeople.org/repos/dchen/apache-maven/epel-apache-maven.repo')

  def set_conf_bin(self, env):
    import params
  
    if params.setup_prebuilt:
      params.conf_dir = os.path.join(*[params.nifi_dir,'conf'])
      params.bin_dir = os.path.join(*[params.nifi_dir,'bin'])

    else:
      params.conf_dir =  glob.glob(params.nifi_install_dir + '/' + params.nifi_dirname + '/nifi-assembly/target/nifi-*/nifi-*/conf')[0]
      params.bin_dir =  glob.glob(params.nifi_install_dir + '/' + params.nifi_dirname + '/nifi-assembly/target/nifi-*/nifi-*/bin')[0]

      
if __name__ == "__main__":
  Master().execute()
