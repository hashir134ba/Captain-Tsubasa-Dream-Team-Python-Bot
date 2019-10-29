# -*- coding: utf-8 -*-
import sqlite3
import os.path

class Database(object):
	def __init__(self):
		self.sqlite_file='accounts.db'
		if not os.path.isfile(self.sqlite_file):
			self.createDb()
		
	def createDb(self):
		conn = sqlite3.connect(self.sqlite_file)
		c = conn.cursor()
		c.execute('''CREATE TABLE "accounts" (`id` INTEGER PRIMARY KEY AUTOINCREMENT,`password`	TEXT,`coin` INTEGER,`free_stone` INTEGER,`total_login_days`	INTEGER DEFAULT 1)''')
		conn.commit()
		conn.close()
		
	def addAccount(self,id,pw,coin,free_stone,total_login_days=1):
		conn = sqlite3.connect(self.sqlite_file)
		c = conn.cursor()
		c.execute("INSERT OR REPLACE INTO accounts (id,password,coin,free_stone,total_login_days) VALUES (%s,'%s',%s,%s,%s)"%(id,pw,coin,free_stone,total_login_days))
		conn.commit()
		conn.close()

	def updateAccount(self,id,coin,free_stone,total_login_days):
		conn = sqlite3.connect(self.sqlite_file)
		c = conn.cursor()
		c.execute("UPDATE accounts SET coin=%s,free_stone=%s,total_login_days=%s where id=%s"%(coin,free_stone,total_login_days,id))
		conn.commit()
		conn.close()

	def rmAccount(self,id):
		return
		conn = sqlite3.connect(self.sqlite_file)
		c = conn.cursor()
		c.execute("delete from accounts where id=%s"%(id))
		conn.commit()
		conn.close()

	def getAllAccounts(self,limit=None):
		conn = sqlite3.connect(self.sqlite_file)
		c = conn.cursor()
		if limit:
			c.execute("select id,password from accounts where free_stone>%s"%(limit))
		else:
			c.execute("select id,password from accounts")
		all_rows = c.fetchall()
		conn.close()
		return all_rows
		
if __name__ == '__main__':
	db=Database()
	db.createDb()