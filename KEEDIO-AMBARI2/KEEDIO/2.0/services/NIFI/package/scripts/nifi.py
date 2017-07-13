import sys, os, pwd, grp, signal, time, glob, socket
from resource_management import *
from subprocess import *

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
      Execute('echo "'+params.nifi_user+'    ALL=(ALL)       NOPASSWD: ALL" >> /etc/sudoers.d/nifi')
      Execute('echo Creating ' +  params.nifi_log_dir +  ' ' +  status_params.nifi_pid_dir)

    #create the log dir if it not already present
    Directory([status_params.nifi_pid_dir, params.nifi_log_dir],
            owner=params.nifi_user,
            group=params.nifi_group,
            create_parents=True
    )

    Execute('touch ' +  params.nifi_log_file, user=params.nifi_user)
    # Not sure why they want to delete this
    #Execute('rm -rf ' + params.nifi_dir, ignore_failures=True)
    #Execute('mkdir -p '+params.nifi_dir)
    
    Directory([params.nifi_dir],
            owner=params.nifi_user,
            group=params.nifi_group,
            create_parents=True
    )

    # Create Nifi data dir
    Directory([params.nifi_data_dir],
              owner=params.nifi_user,
              group=params.nifi_group,
              create_parents=True
    )

    # Create Nifi conf & resources dir
    Directory([params.nifi_conf_resources],
              owner=params.nifi_user,
              group=params.nifi_group,
              create_parents=True
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
    
    params.conf_dir = os.path.join(*[params.nifi_dir,'conf'])
    params.bin_dir = os.path.join(*[params.nifi_dir,'bin'])
    
    #write out nifi.properties
    params.nifi_properties_content=params.nifi_properties_content.replace("{{nifi_host}}",socket.getfqdn())
    File(format("{params.conf_dir}/nifi.properties"), content=InlineTemplate(params.nifi_properties_content), owner=params.nifi_user, group=params.nifi_group) # , mode=0777)

    #write out boostrap.conf
    bootstrap_content=InlineTemplate(params.nifi_boostrap_content)
    File(format("{params.conf_dir}/bootstrap.conf"), content=bootstrap_content, owner=params.nifi_user, group=params.nifi_group) 

    #write out logback.xml
    logback_content=InlineTemplate(params.nifi_logback_content)
    File(format("{params.conf_dir}/logback.xml"), content=logback_content, owner=params.nifi_user, group=params.nifi_group) 
    
    
  def start(self, env):
    import utils
    import params
    self.configure(env, isInstall=False)
    executed = Popen(["service", "nifi", "start"], stdout=PIPE, stderr=PIPE)
    out, err = executed.communicate()
    Logger.info("Nifi: starting")
    Logger.info(str(out))
    Logger.info(str(err))

  def stop(self, env):
    import utils
    import params
    executed = Popen(["service", "nifi", "stop"], stdout=PIPE, stderr=PIPE)
    out, err = executed.communicate()
    Logger.info("Nifi: stopping")
    Logger.info(str(out))
    Logger.info(str(err))



  def status(self, env):
    import utils
    executed = Popen(["service", "nifi", "status"], stdout=PIPE, stderr=PIPE)
    out, err = executed.communicate()
    rc = executed.returncode
    utils.check_rc(rc, out, err)
    
    


      
if __name__ == "__main__":
  Master().execute()
