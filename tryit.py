#!/usr/bin/env python2

import subprocess
import mysql.connector
import threading
import os,sys,stat

####################################
#start of dbpassword code to read password from a local file
#two alternatives (commented out) follow
####################################
filename="./dbpassword"
os.chmod(filename, stat.S_IREAD)
with open(filename) as fp:
    dbpassword=fp.readline()
    fp.close()
os.chmod(filename,0)

##################################
#end
#################################

################################
#prompt user for password
###############################
#dbpassword=raw_input("Please enter the mysql root password:  ")
###############################
#end
###############################
###############################
#hard code password
###############################
#dbpassword="password"
###############################
#end
###############################
connections={}  # dictionary to store openstack names and number of active connections
logfile=subprocess.Popen(['tail','-n','1','-F','/var/log/tomcat7/catalina.out'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
line = logfile.stdout.readline() # throw away line already in log to look for new lines 
line = 'x'

# parses guacamole connection number from line
def get_connection_id( line): # from http://mail-archives.apache.org/mod_mbox/guacamole-user/201802.mbox/%3C1519671051084-0.post@n4.nabble.com%3E
    q1 = line.find("\"")
    q2 = line.find("\"",q1+1)
    q3 = line.find("\"",q2+1)
    q4 = line.find("\"",q3+1)
    user = line[q1+1:q2]
    conn_num = line[q3+1:q4]       # brute force string parsing to get connection number
    return conn_num
# from connection number, looks up hostname, from hostname finds the name of the lowest numbered guacamole connection name to that host
# relies on the convention that the lowest numbered connection name will be the same as the openstack host name
def get_openstack_name(conn_num):
    mydb=mysql.connector.connect(host="localhost",user="root",password=str(dbpassword),database="guacamole_db")
    mycursor=mydb.cursor()
    sql="select parameter_value from guacamole_connection_parameter where guacamole_connection_parameter.parameter_name = 'hostname' and guacamole_connection_parameter.connection_id= %d" % int(conn_num)
    # print (sql)
    mycursor.execute(sql)
    myresult=str(mycursor.fetchone()[0]) # or can use mycursor.fetchall
    sql="select connection_name from guacamole_connection join guacamole_connection_parameter where guacamole_connection.connection_id = guacamole_connection_parameter.connection_id and  guacamole_connection_parameter.parameter_name = 'hostname' and guacamole_connection_parameter.parameter_value= '%s' order by guacamole_connection.connection_id" % str(myresult)
    # print (sql)
    mycursor.execute(sql)
    myresult=str(mycursor.fetchone()[0]) # or can use mycursor.fetchall
    return myresult

# Increase the connection count, or set to 1 if there are no current connections
def addconnection(line):
      connectionnum=get_connection_id(line)
      connection_name=str(get_openstack_name(connectionnum))
      print (connection_name)
      if connection_name not in connections:  # first encounter
            connections[str(connection_name)] = 0 #initialize
      if connections[connection_name] <= 0:
            connections[connection_name] = 1 # we just connected
            print("This is where I'd start machine %s" % str(connection_name))
      else:
            connections[connection_name] = connections[connection_name] + 1  # if we have a connection, add one
      print connections[connection_name]
# Decrease the connection count. Set to -5 if fully disconnected (and time out from there)
def removeconnection(line):
      connectionnum=get_connection_id(line)
      connection_name=str(get_openstack_name(connectionnum))
      print (connection_name)
      if connection_name not in connections:  # disconnected from a machine we don't know about??
            connections[str(connection_name)] = -5 #negative numbers mean shut off in the future
      if connections[connection_name] <=1:
            connections[connection_name] = -5 # connections gone
      else:
            connections[connection_name] = connections[connection_name] - 1  # if we have multiple connections, remove one
      print connections[connection_name]
def every_minute():
    if line == 'x':
        print('one minute')
        t=threading.Timer(60,every_minute)
        t.start()
        for key in connections:
             if connections[key] == -1:
                connections[key]=0;
                print("This is where I'd shut off machine %s" % key)
             if connections[key] < -1 :
                connections[key] = connections[key] + 1   
    else : # if line isn't x we are processing a line so give it 10 seconds and try again
        print('ten seconds')
        t=threading.Timer(10,every_minute)
        t.start()
    
#################################
# This is the meat of it
# look for connections and disconnections
##################################
t=threading.Timer(60,every_minute)   # checks for timing out connections
t.start()
while True:
    line = logfile.stdout.readline()
    if 'connected to connection' in line:
        addconnection(line)
    if 'disconnected from connection' in line:
        removeconnection(line)
#    print("line was ")
#    print line
    line = "x"
       

