# -*- coding: utf-8 -*-
from db import Database
from main import API
import base64
import random
import threading
import Queue

def login(i):
	i=i.rstrip().strip()
	id,pw=i.split(';')
	try:
		a=API()
		#a.setproxy()
		a.setUserId(int(id))
		a.setPassword(base64.b64decode(pw))
		a.dailylogin()
	except:
		return

def wrapper_targetFunc(q):
	while True:
		try:
			work = q.get()
		except Queue.Empty:
			return
		login(work)
		q.task_done()

if __name__ == "__main__":
	db=Database()
	data=set(['%s;%s'%(x[0],x[1]) for x in db.getAllAccounts()])
	print len(data)
	q = Queue.Queue()
	for i in data:
		q.put_nowait(i)
	for _ in range(400):
		threading.Thread(target=wrapper_targetFunc,args=(q,)).start()
	q.join()