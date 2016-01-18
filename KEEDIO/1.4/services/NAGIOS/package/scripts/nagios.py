from resource_management import *
from subprocess import *

def nagios(action):
  import utils
  # FIX: When status is checked params  shouldn't be called
  if action != 'config':
    executed = Popen(["service","nagios",action],stdout=PIPE,stderr=PIPE)
    out,err = executed.communicate()
    if action == 'status':
      rc = executed.returncode
      utils.check_rc(rc,out,err)
  else:
    import params

    Directory("/etc/nagios/servers",
      owner="nagios",
      group="nagios",
      recursive=True
    )
    File('/etc/nagios/nagios.cfg',
      content=StaticFile('nagios.cfg')
    )

    Directory("/etc/nagios/services",
      owner="nagios",
      group="nagios",
      recursive=True
    )

    Directory("/etc/nagios/objects",
      owner="nagios",
      group="nagios",
      recursive=True
    )

    File('/etc/nagios/objects/commands.cfg',
      content=StaticFile('objects/commands.cfg')
    )
 
    File('/etc/nagios/servers/groups.cfg',
      content=StaticFile('servers/groups.cfg')
    )

    File('/etc/nagios/services/groups.cfg',
      content=StaticFile('services/groups.cfg')
    )

    File('/etc/nagios/services/services.cfg',
      content=Template('services/services.j2')
    )
    File('/etc/nagios/servers/hosts.cfg',
      content=Template('servers/hosts.j2')
    )

