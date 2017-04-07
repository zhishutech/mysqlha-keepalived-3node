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


dbhost=config.dbhost
dbport=config.dbport
dbuser=config.dbuser
dbpassword=config.dbpassword


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='/tmp/kp_check.log',
                    filemode='a')


def checkMySQL():
	global dbhost
	global dbport
	global dbuser
	global dbpassword

	shortargs='h:P:'
	opts, args=getopt.getopt(sys.argv[1:],shortargs)
	for opt, value in opts:
		if opt=='-h':
			dbhost=value
		elif opt=='-P':
			dbport=value
	#print "host : %s, port: %d, user: %s, password: %s" % (dbhost, int(dbport), dbuser, dbpassword)
	db = instanceMySQL(dbhost, dbport, dbuser, dbpassword)
	st = db.ishaveMySQL()
	#if ( db.connect() != 0 ):
	#	return 1
	#db.disconnect()
	return st

class instanceMySQL:
	conn = None
	def __init__(self, host=None,port=None, user=None, passwd=None):
		self.dbhost= host
		self.dbport = int(port)
		self.dbuser = user
		self.dbpassword = passwd

	def ishaveMySQL(self):
		cmd="ps -ef | egrep -i \"mysqld\" | grep %s | egrep -iv \"mysqld_safe\" | grep -v grep | wc -l" % self.dbport
		mysqldNum = os.popen(cmd).read()
		cmd ="netstat -tunlp | grep \":%s\" | wc -l" % self.dbport
		mysqlPortNum= os.popen(cmd).read()
		#print mysqldNum, mysqlPortNum
		if ( int(mysqldNum) <= 0):
			print "error"
			return 1
		if ( int(mysqldNum) > 0 and  mysqlPortNum <= 0):
			return 1
		return 0

	def connect(self):
	#	print "in db conn"
#		print "host : %s, port: %d, user: %s, password: %s" % (self.dbhost, self.dbport, self.dbuser, self.dbpassword)
		try:
			self.conn=MySQLdb.connect(host="%s"%self.dbhost, port=self.dbport,user="%s"%dbuser, passwd="%s"%self.dbpassword)
		except Exception, e:
#			print " Error"
			print e
			return 1
		return 0
	def disconnect(self):
		if (self.conn):
			self.conn.close()
			self.conn = None


if __name__== "__main__":
	lock = filelock.FileLock("/tmp/kpc.txt")
	if lock:
		logging.info("ZST Get Lock.start!!!")
	try:
		with lock.acquire(timeout=5):
			pass
	except filelock.timeout:
		print "timeout"	        
		logging.warning("get file lock timeout")
		
	st=checkMySQL()
	sys.exit(st)
