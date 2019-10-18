import os
import time

while(1):
	try:
		os.system('python dailylogin.py')
	except:
		pass
	time.sleep(60*60*10)