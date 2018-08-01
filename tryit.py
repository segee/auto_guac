#!/usr/bin/env python2

import subprocess, mysql.connector

logfile=subprocess.Popen(['tail','-n','1','-F','/var/log/tomcat7/catalina.out'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
mydb=mysql.connector.connect(host="localhost",user="root",password="lame",database="guacamole_db")

mycursor=mydb.cursor()

mycursor.execute("select connection_name from guacamole_connection where connection_id=1")
myresult=mycursor.fetchone();
print myresult
print ""
print myresult[0]

