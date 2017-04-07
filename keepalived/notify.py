#!/usr/bin/python
#coding: utf-8
#http://zhishuedu.com 
#Copyriht(c) 2017 - wubx(wubx@zhishuedu.com)  

import sys
import os
import getopt
import MySQLdb
import logging
import filelock
import config

preSlaveSQL="set global super_read_only=1; set global read_only=1;"
preMasterSQL="set global super_read_only=0; set global read_only=0;"

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/kp.log',
                filemode='a')

class DBase:
	conn = None
	def __init__(self, host=None,port=None, user=None, passwd=None):
		self.dbhost= host
		self.dbport = port
		self.dbuser = user
		self.dbpassword = passwd
		self.conn=MySQLdb.connect(host="%s"%self.dbhost, port=3309,user="%s"%dbuser, passwd="%s"%self.dbpassword)
		#self.cur = self.conn.cursor()
		

	def makeMaster(self):
		cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
		
		if  preMasterSQL.strip() != '' :
			cursor.execute(preMasterSQL)
			for r in cursor.fetchall():
				print r
		cursor.close()
		self.conn.commit()
		cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
		
		query="show slave status"
		
		cursor.execute(query)
		for row in cursor.fetchall():
			
			if row['Slave_IO_Running'] == 'Yes':
				#print "stop slave io_thread for channel '%s'" %row['Channel_Name']
				cursor.execute("stop slave io_thread for channel  '%s'" % row['Channel_Name']) 
				logging.warning("stop slave io_thread for channel '%s'" % row['Channel_Name'])
			
		cursor.close()
			
	def makeSlave(self):
		cursor = self.conn.cursor()
		
		if preSlaveSQL.strip() !='' :
			cursor.execute(preSlaveSQL) 
			for r in cursor.fetchall():
				print r			
		cursor.close()
		self.conn.commit()
		cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
		query="show slave status"
		
		cursor.execute(query)
		for row in cursor.fetchall():
			#print row
			if row['Slave_IO_Running'] == 'No':
				cursor.execute("start slave for channel '%s'" % row['Channel_Name']) 
				logging.warning("start slave for channel '%s'" % row['Channel_Name'])
			
		cursor.close()		
	

	def disconnect(self):
		if (self.conn):
			self.conn.close()
			self.conn = None


if __name__== "__main__":
	#st=checkMySQL()
	#sys.exit(st)
	lock = filelock.FileLock("/tmp/kps.txt")
	if lock:
		logging.info("ZST Get Lock.start!!!")
        try:
		with lock.acquire(timeout=5):
			pass
        except filelock.timeout:
		print "timeout"	        
		logging.warning("get file lock timeout")

       
       #logging.info("abcd")
        logging.info(sys.argv)
        dbhost = config.dbhost
	dbport = config.dbport
	dbuser = config.dbuser
	dbpassword = config.dbpassword
	db = DBase(dbhost,dbport,dbuser,dbpassword)
	if sys.argv[3].upper() == 'MASTER':
		logging.warning("Current become Master!!!")
		db.makeMaster()
	if sys.argv[3].upper() == "BACKUP":
		logging.warning("Current become Slave!!!")
		db.makeSlave()
		
 	db.disconnect()
