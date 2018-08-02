#!/usr/bin/env python2

import subprocess
import mysql.connector

def get_connection_id( line):
    q1 = line.find("\"")
    q2 = line.find("\"",q1+1)
    q3 = line.find("\"",q2+1)
    q4 = line.find("\"",q3+1)
    user = line[q1+1:q2]
    conn_num = line[q3+1:q4]
    return conn_num
def get_openstack_name(conn_num):
    mydb=mysql.connector.connect(host="localhost",user="root",password="lame",database="guacamole_db")
    mycursor=mydb.cursor()
    sql="select parameter_value from guacamole_connection_parameter where guacamole_connection_parameter.parameter_name = 'hostname' and guacamole_connection_parameter.connection_id='$conn_num'"
    print (sql)
    mycursor.execute(sql)
    myresult=mycursor.fetchone() # or can use mycursor.fetchall
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
    connectionnum=get_connection_id(line)
    print (get_openstack_name(connectionnum))

