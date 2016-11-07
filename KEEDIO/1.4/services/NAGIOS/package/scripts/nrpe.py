from resource_management import *
from subprocess import *

def nrpe(action):
  import utils
  if action != 'config':
    executed = Popen(["service","nrpe",action],stdout=PIPE,stderr=PIPE)
    out,err = executed.communicate()
    if action == 'status':
      rc = executed.returncode
      utils.check_rc(rc,out,err)
  else:
    import params

    Directory("/etc/nagios",
      owner="nagios",
      group="nagios",
      recursive=True
    )

    File('/etc/nagios/nrpe.cfg',
      content=Template('nrpe.j2')
    )

    File("/etc/sudoers.d/91-nrpe",
      content=StaticFile('91-nrpe'))
  
