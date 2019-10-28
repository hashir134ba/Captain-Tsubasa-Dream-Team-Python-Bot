# -*- coding: utf-8 -*-
from db import Database
from main import API
import base64

def login(i):
	id,pw=i.split(';')
	try:
		a=API()
		a.setproxy()
		a.setUserId(id)
		a.setPassword(base64.b64decode(pw))
		a.dailylogin()
	except:
		return

if __name__ == "__main__":
	login('100007994;wG4WogpClJEfWJtHQgcdLq1WHOhS67EOU4hun2gW5/o=')