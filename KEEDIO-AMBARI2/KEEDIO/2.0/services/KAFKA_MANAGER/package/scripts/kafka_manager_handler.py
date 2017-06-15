from resource_management import *
from subprocess import *


def kafka_manager(action):
    import utils
    # FIX: When status is checked params  shouldn't be called
    if action != 'status':
        import params
        if action == 'config':
            File('/etc/kafka-manager/conf/application.conf',
                 content=Template('application.conf.j2'))
        elif action == 'start' or action == 'stop':
            executed = Popen(["service", "kafka-manager", action], stdout=PIPE, stderr=PIPE)
            out, err = executed.communicate()
            Logger.info("Kafka Manager service:")
            Logger.info(action)
            Logger.info(str(out))
            Logger.info(str(err))
    elif action == "status":
        executed = Popen(["service", "kafka-manager", action], stdout=PIPE, stderr=PIPE)
        out, err = executed.communicate()
        rc = executed.returncode
        utils.check_rc(rc, out, err)
