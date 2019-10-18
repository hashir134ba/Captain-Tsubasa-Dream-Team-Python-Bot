# -*- coding: utf-8 -*-
from multiprocessing import Pool
from db import Database
from main import API
import base64

def login(i):
	id,pw=i.split(';')
	try:
		a=API()
		#a.setproxy()
		a.setUserId(id)
		a.setPassword(base64.b64decode(pw))
		a.dailylogin()
		a.getAllMissions()
		#if a.userinfo[3]['update_info']['user_billing_info']['free_stone']>=90:
			#a.gacha_play(1042201,10)
			#a.gacha_play(1042202,10)
			#a.gacha_play(1042203,10)
			#a.gacha_play(1042204,10)
			#a.gacha_play(1042205,10)
			#a.gacha_play(41,10)
			#a.gacha_play(101,1)
			#a.gacha_play(121,1)
		a.user_fetchHomeInfo()
		a.exportPlayers()
	except:
		return

if __name__ == "__main__":
	db=Database()
	data=['%s;%s'%(x[0],x[1]) for x in db.getAllAccounts()]
	print len(data)
	p= Pool(5)
	try:
		list(p.imap_unordered(login, data))
	except Exception:
		print("a worker failed, aborting...")
		p.close()
		p.terminate()
	else:
		p.close()
		p.join()
	print "job done"