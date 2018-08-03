#!/usr/bin/env python2

import subprocess
import mysql.connector

dbpassword=raw_input("Please enter the mysql root password:  ")
connections={}  # dictionary to store openstack names and number of active connections
line='x'

def get_connection_id( line): # from http://mail-archives.apache.org/mod_mbox/guacamole-user/201802.mbox/%3C1519671051084-0.post@n4.nabble.com%3E
    q1 = line.find("\"")
    q2 = line.find("\"",q1+1)
    q3 = line.find("\"",q2+1)
    q4 = line.find("\"",q3+1)
    user = line[q1+1:q2]
    conn_num = line[q3+1:q4]
    return conn_num
def get_openstack_name(conn_num):
    mydb=mysql.connector.connect(host="localhost",user="root",password=str(dbpassword),database="guacamole_db")
    mycursor=mydb.cursor()
    sql="select parameter_value from guacamole_connection_parameter where guacamole_connection_parameter.parameter_name = 'hostname' and guacamole_connection_parameter.connection_id= %d" % int(conn_num)
    print (sql)
    mycursor.execute(sql)
    myresult=str(mycursor.fetchone()[0]) # or can use mycursor.fetchall
    sql="select connection_name from guacamole_connection join guacamole_connection_parameter where guacamole_connection.connection_id = guacamole_connection_parameter.connection_id and  guacamole_connection_parameter.parameter_name = 'hostname' and guacamole_connection_parameter.parameter_value= '%s' order by guacamole_connection.connection_id" % str(myresult)
    print (sql)
    mycursor.execute(sql)
    myresult=str(mycursor.fetchone()[0]) # or can use mycursor.fetchall
    return myresult
def addconnection(line):
      connectionnum=get_connection_id(line)
      connection_name=str(get_openstack_name(connectionnum))
      print (connection_name)
      if connection_name not in connections:  # first encounter
            connections[str(connection_name)] = 0 #initialize
      if connections[connection_name] <= 0:
            connections[connection_name] = 1 # we just connected
      else:
            connections[connection_name] = connections[connection_name] + 1  # if we have a connection, add one
      print connections[connection_name]
def removeconnection(line):
      connectionnum=get_connection_id(line)
      connection_name=str(get_openstack_name(connectionnum))
      print (connection_name)
      if connection_name not in connections:  # disconnected from a machine we don't know about??
            connections[str(connection_name)] = -5 #negative numbers mean shut off in the future
      if connections[connection_name] <=1:
            connections[connection_name] = -5 # connections gone
      else:
            connections[connection_name] = connections[connection_name] - 1  # if we have a connection, add one
      print connections[connection_name]
def every_minute():
    if line = 'x':
        print('one minute')
        t=Timer(60,every_minute)
    else :
        print('ten seconds')
        t=Timer(10,every_minute)
    



logfile=subprocess.Popen(['tail','-n','1','-F','/var/log/tomcat7/catalina.out'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
line = logfile.stdout.readline()
line = 'x'
t=Timer(60,every_minute)
while True:
    line = logfile.stdout.readline()
    if 'connected to connection' in line:
        addconnection(line)
    if 'disconnected from connection' in line:
        removeconnection(line)
    print("line was ")
    print line
    line = "x"
       

