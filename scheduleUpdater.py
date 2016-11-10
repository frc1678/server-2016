import multiprocessing
from firebase import firebase as fb
import time

class ScheduleUpdater(multiprocessing.Process):
	"""docstring for ScheduleUpdater"""
	def __init__(self):
		super(ScheduleUpdater, self).__init__()
	def run(self):
		while True:
			(superSecret, url) = ('qVIARBnAD93iykeZSGG8mWOwGegminXUUGF2q0ee', 'https://1678-scouting-2016.firebaseio.com/') 
			auth = fb.FirebaseAuthentication(superSecret, "1678programming@gmail.com", True, True)
			firebase = fb.FirebaseApplication(url, auth)
			matches = firebase.get('/Matches', None)
			while True:
				matches = firebase.get('/Matches', None)[1:]
				notCompleted = filter(lambda m: m.get("redScore") == None or m.get("blueScore") == None, matches)
				print "current match is " + str(min(map(lambda m: m['number'], notCompleted)))
				firebase.put('/', 'currentMatchNum', min(map(lambda m: m['number'], notCompleted)))
				time.sleep(5)

s = ScheduleUpdater()
s.start()

