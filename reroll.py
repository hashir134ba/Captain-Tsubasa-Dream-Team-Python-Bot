from main import API
import time

while(1):
	try:
		a=API()
		a.reroll()
	except:
		time.sleep(5)
		pass