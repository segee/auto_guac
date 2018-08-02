#!/usr/bin/env python2

import subprocess
import mysql.connector

dbpassword=raw_input("Please enter the mysql root password:  ")
connections={}  # dictionary to store openstack names and number of active connections

def get_connection_id( line):
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




logfile=subprocess.Popen(['tail','-n','1','-F','/var/log/tomcat7/catalina.out'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#mydb=mysql.connector.connect(host="localhost",user="root",password="lame",database="guacamole_db")

#mycursor=mydb.cursor()

#mycursor.execute("select connection_name from guacamole_connection where connection_id=1")
#myresult=mycursor.fetchone();
#print myresult
#print ""
#print myresult[0]
line = logfile.stdout.readline()                                 
while True:
    line = logfile.stdout.readline()
    if 'connected to connection' in line:
        connectionnum=get_connection_id(line)
        connection_name=get_openstack_name(conectionnum)
        print (connection_name)
        if connection[connection_name] is NULL:
            connection[connection_name] = 0
        if connection[connection_name] <= 0:
            connection[connection_name] = 1
        else:
            connection[connection_name] = connection[connection_name] + 1
        print connection[connection_name]

