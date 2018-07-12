import psutil
import os
import time

user = "set"
cnt = 0
def chxpids(user):
	cnt = 0
	for proc in psutil.process_iter():
		p = proc.as_dict(attrs=['pid', 'username'])
		if p['username'] == user:
			cnt=cnt + 1
		if cnt >= 5:
			os.kill(p['pid'], 9)

while 1:
	chxpids(user)
	time.sleep(1)
