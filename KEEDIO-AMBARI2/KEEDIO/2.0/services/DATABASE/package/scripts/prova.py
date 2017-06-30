import pexpect
child = pexpect.spawn ('/bin/mysql_secure_installation')
child.logfile = open("/tmp/mylog", "w")
print "Enter current password for root (enter for none):"
child.expect('.*current.*')
print "except: sending current password"
i=child.send('root\r')
if i==1:
   print "root password already set, configure mysql manually"
   exit() 
child.expect('.*Change the root password.*')
child.send('y\r')
print "except: setting new password"
child.expect('.*New password:.*')
child.send('prova\r')
child.expect('.*Re-enter new password:.*')
child.send('prova\r')
print "except: removing security risks"
child.expect('.*Remove anonymous users?.*')
child.send('y\r')
child.expect('.*Disallow root login remotely?.*')
child.send('y\r')
child.expect('.*Remove test database and access to it?.*')
child.send('y\r')
child.expect('.*Reload privilege tables now?.*')
child.send('y\r')

