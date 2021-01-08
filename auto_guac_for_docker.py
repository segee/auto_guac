#!/usr/bin/env python3
## Double # comments are for the 2021 revision
## Triple # comments (###) are lines from the earlier version that were taken out
## BES 12/30/2020
import subprocess
import mysql.connector
import threading
import os,sys,stat
import sys


##################################
# Added by Forrest on 2018-10-04 #
##################################
OSSCRIPTSDIR = "../Openstack_shell_scripts"
if (len(sys.argv) > 1):
    OSSCRIPTSDIR = str(sys.argv[1])
    
##################################


###############################
connections={}  # dictionary to store openstack names and number of active connections
print("*************************************************************");
print("****This program should not be run directly, it should be run");
print("with the tail of the catalina.out log file as stdin.  The ");
print("easiest way to do that is with the script or with the command");
print("docker logs --follow --tail 1 guacamole|./auto_guac_for_docker.py");
print("it assumes that guacamole is running locally in a container");
print("named guacamole.  This script does not need to run as root, ");
print("but the user must be a member of the docker group.");
print("sudo docker add -aG docker username");
print("*************************************************************");
props=subprocess.check_output("docker exec guacamole printenv |grep SQL",shell=True)

mysqlprops = dict(line.strip().split(b'=') for line in props.splitlines())

#logfile=subprocess.Popen(['tail','-n','1','-F','/var/log/tomcat7/catalina.out'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#line = logfile.stdout.readline() # throw away line already in log to look for new lines 
line = sys.stdin.readline() # throw away line already in log to look for new lines 
line = 'x'

# parses guacamole connection number from line
def get_connection_id( line): # from http://mail-archives.apache.org/mod_mbox/guacamole-user/201802.mbox/%3C1519671051084-0.post@n4.nabble.com%3E
# Changed from searching for quotes alone to something slightly more robust
    q1 = line.find("User \"")
    q2 = line.find("\"",q1+6)  # move past User " and find the next quote
    q3 = line.find("connection \"",q2+1)  # 
    q4 = line.find("\"",q3+12)             # 
    user = line[q1+6:q2]
    conn_num = line[q3+12:q4]       # brute force string parsing to get connection number
    return conn_num

## This is actually a simplification, the openstack scripts have been modified to allow ip addresses in addition to 
## machine names.  This incarnation relies on the guacamole "hostname" to be the local (fixed) ip of the machine.
## a nice side feature is that machines that shouldn't be auto_guac'ed can use a dns name, floating ip, or docker ip
## 
# from connection number, looks up hostname, from hostname finds the name of the lowest numbered guacamole connection name to that host
# relies on the convention that the lowest numbered connection name will be the same as the openstack host name
###def get_openstack_name(conn_num):
def get_openstack_ip(conn_num):
#    mysqlprops = dict(line.strip().split(':') for line in open('/etc/guacamole/guacamole.properties') if (":" in line and not line.startswith("#") ))
#    mydb=mysql.connector.connect(host=mysqlprops['mysql-hostname'],user=mysqlprops['mysql-username'],password=mysqlprops['mysql-password'],database=mysqlprops['mysql-database'])

    mydb=mysql.connector.connect(host=mysqlprops[b'MYSQL_HOSTNAME'].decode('utf-8'),user=mysqlprops[b'MYSQL_USER'].decode('utf-8'),password=mysqlprops[b'MYSQL_PASSWORD'].decode('utf-8'),database=mysqlprops[b'MYSQL_DATABASE'].decode('utf-8'))
    mycursor=mydb.cursor()
    sql="select parameter_value from guacamole_connection_parameter where guacamole_connection_parameter.parameter_name = 'hostname' and guacamole_connection_parameter.connection_id= %d" % int(conn_num)
    print (sql)
    mycursor.execute(sql)
    myresult=str(mycursor.fetchone()[0]) # or can use mycursor.fetchall
###    sql="select connection_name from guacamole_connection join guacamole_connection_parameter where guacamole_connection.connection_id = guacamole_connection_parameter.connection_id and  guacamole_connection_parameter.parameter_name = 'hostname' and guacamole_connection_parameter.parameter_value= '%s' order by guacamole_connection.connection_id" % str(myresult)
###    # print (sql)
###    mycursor.execute(sql)
###    myresult=str(mycursor.fetchone()[0]) # or can use mycursor.fetchall
## the hostname (for an auto_guac'ed machine) should be the local ip address
    return myresult

# Increase the connection count, or set to 1 if there are no current connections
def addconnection(line):
      connectionnum=get_connection_id(line)
###      connection_name=str(get_openstack_name(connectionnum))
      connection_name=str(get_openstack_ip(connectionnum))
      # print (connection_name)
      if connection_name not in connections:  # first encounter
            connections[str(connection_name)] = 0 #initialize
      if connections[connection_name] <= 0:
            connections[connection_name] = 1 # we just connected
        #    print("This is where I'd start machine %s" % str(connection_name))
            #rc=subprocess.call("../Openstack_shell_scripts/openstack_start_machine.sh '%s'" %connection_name , shell=True,cwd = '../Openstack_shell_scripts')
###            rc=subprocess.call("%s/openstack_start_machine.sh '%s'" %(OSSCRIPTSDIR,connection_name) , shell=True,cwd = OSSCRIPTSDIR)
            rc=subprocess.call("%s/openstack_start_machine.sh -l '%s'" %(OSSCRIPTSDIR,connection_name) , shell=True,cwd = OSSCRIPTSDIR)
      else:
            connections[connection_name] = connections[connection_name] + 1  # if we have a connection, add one
      # print connections[connection_name]
# Decrease the connection count. Set to -30 if fully disconnected (and time out from there)
def removeconnection(line):
      connectionnum=get_connection_id(line)
###      connection_name=str(get_openstack_name(connectionnum))
      connection_name=str(get_openstack_ip(connectionnum))
      #print (connection_name)
      if connection_name not in connections:  # disconnected from a machine we don't know about??
            connections[str(connection_name)] = -30 #negative numbers mean shut off in the future
      if connections[connection_name] <=1:
            connections[connection_name] = -30 # connections gone
      else:
            connections[connection_name] = connections[connection_name] - 1  # if we have multiple connections, remove one
      #print connections[connection_name]
def every_minute():
    if line == 'x':
       # print('one minute')
        t=threading.Timer(60,every_minute)
        t.start()
        for key in connections:
             if connections[key] == -1:
                connections[key]=0;
        #        print("This is where I'd shut off machine %s" % key)
            #    rc=subprocess.call("../Openstack_shell_scripts/openstack_shelve_machine.sh '%s'" %key, shell=True,cwd='../Openstack_shell_scripts')
                rc=subprocess.call("%s/openstack_shelve_machine.sh -l '%s'" %(OSSCRIPTSDIR,key), shell=True,cwd=OSSCRIPTSDIR)

             if connections[key] < -1 :
                connections[key] = connections[key] + 1   
    else : # if line isn't x we are processing a line so give it 10 seconds and try again
       # print('ten seconds')
        t=threading.Timer(10,every_minute)
        t.start()
    
#################################
# This is the meat of it
# look for connections and disconnections
##################################
t=threading.Timer(60,every_minute)   # checks for timing out connections
t.start()
while True:
#    line = logfile.stdout.readline()
    line = sys.stdin.readline()
    if 'connected to connection' in line:
        addconnection(line)
    if 'disconnected from connection' in line:
        removeconnection(line)
#    print("line was ")
#    print line
    line = "x"
       

