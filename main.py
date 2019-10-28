# -*- coding: utf-8 -*-
import requests
import time
import json
import random
import base64
import os
import sys
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from hashlib import sha1
import hmac
import re
import io
import hashlib
from db import Database
import units

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class API(object):
	def __init__(self):
		self.s=requests.Session()
		self.s.headers.update({'Accept-Encoding':'gzip, deflate','Content-Type':'application/json','Expect':'100-continue','User-Agent':None})
		self.s.verify=False
		if 'win' in sys.platform:
			self.s.proxies.update({'http': 'http://127.0.0.1:8888','https': 'https://127.0.0.1:8888',})
		self.game_api='https://gl-game.tsubasa-dreamteam.com/ep73/'
		self.language_code=2
		self.platform_type=0
		self.auth_count=1
		self.locale_identifer='en_DE'
		self.publicKey='''-----BEGIN PUBLIC KEY-----
						MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCp0fjPgtnWaWq2LGfLzR9HraEX
						D9M76SXhJH2ld1oE/U6kVfggpfwXI42SEVmEQytOPn6RjVdBATYaBgKsMbPee1pR
						8Tk1sQD6bA+8IBPoSogqZYSNdRPnAaASCNEVOd+29hjS0mMCLUu7XezctkAjkW8a
						WsRwn+8fvXuU2pSg9wIDAQAB
						-----END PUBLIC KEY-----'''
		self.db=Database()
		
	def getUnitName(self,id):
		id=str(id)
		if id in units.data:
			return units.data[id]['name']
		return None
	
	def getUnitRarity(self,id):
		id=str(id)
		if id in units.data:
			return int(units.data[id]['rarity'])
		return None
		
	def setproxy(self,prox=None):
		self.s.proxies.update({'http': 'http://127.0.0.1:8888','https': 'https://127.0.0.1:8888',})

	def rndHex(self,n):
		res= ''.join([random.choice('0123456789ABCDEF') for x in range(n)]).lower()
		if n==32:
			self.log('rndHex called %s'%(res))
		return res

	def rndBytes(self,n):
		return os.urandom(n)
		
	def generateMaskData(self):
		key = RSA.importKey(self.publicKey)
		cipher = PKCS1_OAEP.new(key)
		self.rndkey=self.rndBytes(32)
		self.log('rndkey:%s'%(self.rndkey.encode('hex')))
		return base64.encodestring(cipher.encrypt(self.rndkey)).replace('\n','')

	def xor(self,v1,v2):
		#self.log('xor v1:%s v2:%s'%(len(v1),len(v2)))
		return ''.join([chr(ord(a) ^ ord(b)).encode('hex') for (a,b) in zip(v1, v2)]).decode('hex')

	def md5(self,s):
		m = hashlib.md5()
		m.update(s)
		return m.hexdigest()
		
	def resemara_id(self):
		return self.md5('?%s-%s-%s-%s-%s com.klab.captain283.global'%(self.rndHex(8).upper(),self.rndHex(4).upper(),self.rndHex(4).upper(),self.rndHex(4).upper(),self.rndHex(12).upper())).upper()
		
	def calcDigest(self,raw,key=None):
		if not key:
			key=self.key
		raw=raw.replace('https://gl-game.tsubasa-dreamteam.com/ep68','')
		hashed = hmac.new(key, raw, sha1)
		return hashed.digest().encode("hex").rstrip('\n')
		
	def log(self,msg):
		print '[%s]%s'%(time.strftime('%H:%M:%S'),msg.encode('utf-8'))
				
	def callAPI(self,url,data,key=None):
		uris=[]
		uris.append('p=i')
		if hasattr(self,'mv'):
			uris.append('mv=%s'%(self.mv))
		uris.append('id=%s'%self.rndHex(17))
		if hasattr(self,'user_id'):
			uris.append('u=%s'%(self.user_id))
			uris.append('t=%s'%(int(time.time())))
			uris.append('lang=En')
		finurl=self.game_api+url+'?'+'&'.join(uris)
		data='[%s,"%s"]'%(data,self.calcDigest('%s %s'%(re.sub('.*ep[0-9]*','',finurl),data),key))
		r=self.s.post(finurl,data=data)
		if r.status_code<>200:
			self.log('bad status code:%s'%(r.status_code))
			return None
		jdata=json.loads(r.content)
		if 'update_info' in jdata[3] and 'user' in jdata[3]['update_info']:
			self.userid=jdata[3]['update_info']['user']['id']
			self.log('welcome %s:%s'%(jdata[3]['update_info']['user']['id'],jdata[3]['update_info']['user']['name']))
		if 'authorization_count' in r.content:
			return self.callAPI(url,'{"user_id":%s,"auth_count":%s,"mask":"%s","asset_state":"","resemara_id":"%s"}'%(self.user_id,jdata[3]['invalid_auth_count']['authorization_count']+1,self.generateMaskData(),self.resemara_id()))
		if 'user_id' in jdata[3]:
			self.user_id=jdata[3]['user_id']
		if 'authorization_key' in r.content:
			self.log('authorization_key:%s'%(base64.b64decode(jdata[3]['authorization_key']).encode('hex')))
			self.key=self.xor(self.rndkey,base64.b64decode(jdata[3]['authorization_key']))
			self.pw=self.key
		if 'session_key' in jdata[3]:
			self.log('session_key:%s'%(base64.b64decode(jdata[3]['session_key']).encode('hex')))
			self.key=self.xor(self.rndkey,base64.b64decode(jdata[3]['session_key']))
		if 'master_version' in jdata[3]:
			self.mv=jdata[3]['master_version']['version']
		return jdata
		
	def login_startup(self):
		return self.callAPI('login/startup','{"language_code":%s,"platform_type":%s,"mask":"%s","locale_identifer":"en_DE"}'%(self.language_code,self.platform_type,self.generateMaskData()),'Sqm+kQWVo679raYK')
		
	def login_login(self):
		res= self.callAPI('login/login','{"user_id":%s,"auth_count":%s,"mask":"%s","asset_state":"","resemara_id":"%s"}'%(self.user_id,self.auth_count,self.generateMaskData(),self.resemara_id()))
		self.playable_card_by_id=res[3]['update_info']['playable_card_by_id']
		return res
		
	def dataLink_getDataLinkStatusList(self):
		return self.callAPI('dataLink/getDataLinkStatusList','null')
	
	def user_updateGdprConsents(self):
		return self.callAPI('user/updateGdprConsents','{"consents":[{"consent_type":2,"has_consented":true},{"consent_type":3,"has_consented":true},{"consent_type":4,"has_consented":true}]}')

	def tutorial_download(self):
		return self.callAPI('tutorial/download','null')	
		
	def user_checkAdIdentifier(self):
		return self.callAPI('user/checkAdIdentifier','{"consents":[{"consent_type":2,"has_consented":false,"ad_identifier":"00000000-0000-0000-0000-000000000000"}]}')	
		
	def tutorial_kickoff(self):
		return self.callAPI('tutorial/kickoff','null')
		
	def tutorial_matchResult(self):
		return self.callAPI('tutorial/matchResult','null')
		
	def user_fetchHomeInfo(self):
		res= self.callAPI('user/fetchHomeInfo','null')
		userinfo=res
		self.userinfo=userinfo
		self.db.addAccount(self.user_id,base64.b64encode(self.pw) if hasattr(self,'pw') else base64.b64encode(self.key),userinfo[3]['update_info']['user']['coin'],userinfo[3]['update_info']['user_billing_info']['free_stone'],self.total_login_days if hasattr(self,'total_login_days') else 1)
		return res
		
	def notification_updateNotificationSetting(self):
		return self.callAPI('notification/updateNotificationSetting','{"device_token":"eM06C_hzOi8:APA91bGVb4RdFnOZcQ7ai64PS1J9uhLnlB33HTg8GshI7pUO-mclrh8IPbsjgZCyE6F7mN58HAQEozxLu-v2O-5_oME_iNJOLnKveZYstXg_tPQRj25Yp97ZyD2Q5_054cMwQSSwBmxb","is_admin_notice":true,"is_ap_max":true,"is_league_result":true,"is_event_reservation":true,"is_coop_recruitment":true}')
		
	def gacha_fetch(self):
		return self.callAPI('gacha/fetch','null')	
		
	def gacha_play(self,gacha_product_info_id=99,play_count=1):
		return self.callAPI('gacha/play','{"gacha_product_info_id":%s,"play_count":%s,"selected_category":1,"mixer_materials":[]}'%(gacha_product_info_id,play_count))
		
	def gacha_fixRetry(self):
		return self.callAPI('gacha/fixRetry','null')	
		
	def formation_updateDeckList(self,card_ids,captain_card_id):
		return self.callAPI('formation/updateDeckList','{"deck_list":[{"id":1,"user_id":%s,"formation_id":1,"name":"Deck 1","is_gvg_deck":false,"expiration_date":0,"card_ids":[%s],"team_effect_card_ids":[0,0,0],"captain_card_id":%s,"uniform_numbers":[1,3,4,5,2,7,6,8,10,9,11,12,13,14,15,16]}]}'%(self.user_id,','.join(str(x) for x in card_ids),captain_card_id))
		
	def user_setProfile(self,name='Aguilero',team_name='FC.Aguilo'):
		return self.callAPI('user/setProfile','{"name":"%s","team_name":"%s","comment":"Nice to meet ya!"}'%(name,team_name))
		
	def tutorial_end(self):
		return self.callAPI('tutorial/end','null')
		
	def loginBonus_fetchBonus(self):
		return self.callAPI('loginBonus/fetchBonus','null')
		
	def present_fetch(self):
		return self.callAPI('present/fetch','null')
		
	def present_receiveMultiple(self,present_ids):
		return self.callAPI('present/receiveMultiple','{"present_ids":[%s]}'%(','.join(str(x) for x in present_ids)))
		
	def mission_fetch(self):
		return self.callAPI('mission/fetch','null')

	def mission_receiveMultiple(self,mission_ids):
		return self.callAPI('mission/receiveMultiple','{"mission_ids":[%s]}'%(','.join(str(x) for x in mission_ids)))

	def profile_getOne(self):
		res= self.callAPI('profile/getOne','{"user_id":%s}'%(self.user_id))
		self.total_login_days=res[3]['profile']['total_login_days']
		return res

	def reroll(self):
		self.login_startup()
		team=self.login_login()
		card_ids=[]
		for c in team[3]['update_info']['playable_card_by_id']:
			if type(c)==long:
				if len(card_ids)==15:	break
				card_ids.append(c)
		time.sleep(6)
		self.dataLink_getDataLinkStatusList()
		self.user_updateGdprConsents()
		self.tutorial_download()
		self.user_checkAdIdentifier()
		self.tutorial_kickoff()
		self.tutorial_matchResult()
		self.user_fetchHomeInfo()
		self.gacha_fetch()
		self.gacha_play()
		card=self.gacha_fixRetry()
		self.gacha_fetch()
		self.user_fetchHomeInfo()
		captain_card_id=card[3]['update_info']['playable_card_by_id'][0]
		card_ids.append(captain_card_id)
		self.formation_updateDeckList(card_ids,captain_card_id)
		self.user_fetchHomeInfo()
		self.user_setProfile()
		self.tutorial_end()
		self.user_fetchHomeInfo()
		self.loginBonus_fetchBonus()
		self.getAllGifts()
		self.user_fetchHomeInfo()
		
	def getAllGifts(self):
		present_list=self.present_fetch()[3]['present_response']['present_list']
		presents=[]
		for p in present_list:
			presents.append(p['id'])
		if len(presents)>=1:
			self.present_receiveMultiple(presents)

	def getAllGacha(self):
		elements=self.gacha_fetch()[3]['elements']
		for p in elements:
			if 'product_info_list' not in p:	continue
			for q in p['product_info_list']:
				for t in q:
					for e in q[t]:
						if e['cost']<=0:
							self.gacha_play(e['id'],e['play_count'])
			
	def getAllMissions(self):
		present_list=self.mission_fetch()[3]['mission_list']
		missions=[]
		for p in present_list:
			if p['is_complete'] and p['is_reward']:
				missions.append(p['mission_id'])
		if len(missions)>=1:
			self.mission_receiveMultiple(missions)
		
	def setUserId(self,id):
		self.user_id=id
		
	def setPassword(self,pw):
		self.key=pw
		
	def save(self,d,f):
		with io.open(f, 'a', encoding='utf8') as the_file:
			the_file.write('%s\n'%(unicode(d)))
		
	def exportPlayers(self):
		cards=[]
		cards.append('player id:%s'%(self.userid))
		good=[13100131,4200181,13700181,40300081]
		for p in self.playable_card_by_id:
			if type(p) != long:
				cardid=p['master_id']
				if cardid not in good:	continue
				rarity=self.getUnitRarity(cardid)
				if rarity>=40:
					self.log('card id:%s name:%s rarity:%s'%(cardid,self.getUnitName(cardid),rarity))
					cards.append(str(cardid))
		if len(cards)>1:
			self.save(','.join(cards),'accounts_0_01.txt')
		
	def dailylogin(self):
		self.login_login()
		time.sleep(1)
		self.dataLink_getDataLinkStatusList()
		self.loginBonus_fetchBonus()
		self.getAllGifts()
		self.getAllMissions()
		self.getAllGacha()
		self.profile_getOne()
		self.user_fetchHomeInfo()

if __name__ == "__main__":
	a=API()
	a.reroll()