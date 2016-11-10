import pyrebase
import DataModel
import time
from firebase import firebase as fir
from SPR import ScoutPrecision
import multiprocessing
import random

class ScoutRotatorProcess(multiprocessing.Process):
	"""docstring for ScoutRotatorProcess"""
	def __init__(self, spr):
		super(ScoutRotatorProcess, self).__init__()
		self.spr = spr

	def run(self):
		(superSecret, url) = ('qVIARBnAD93iykeZSGG8mWOwGegminXUUGF2q0ee', 'https://1678-scouting-2016.firebaseio.com/') 
		# (superSecret, url) = ('lGufYCifprPw8p1fiVOs7rqYV3fswHHr9YLwiUWh', 'https://1678-extreme-testing.firebaseio.com/')
		scouts = 'westley mx tim jesse sage alex janet livy gemma justin berin aiden rolland rachel zoe ayush jona angela kyle wesley'.split()

		auth = fir.FirebaseAuthentication(superSecret, "1678programming@gmail.com", True, True)

		firb = fir.FirebaseApplication(url, auth)
		url = '1678-scouting-2016'
		config = {
			"apiKey": "mykey",
			"authDomain": url + ".firebaseapp.com",
			"databaseURL": "https://" + url + ".firebaseio.com/",
			"storageBucket": url + ".appspot.com"
		}
		firebase = pyrebase.initialize_app(config)
		fb = firebase.database()
		for i in scouts:
			fb.child("available").child(i).set(1)
		scoutss = fb.child('scouts').get().val()
		for s in range(1,19):
			fb.child("scouts").child("scout" + str(s)).child("scoutStatus").set("Requested")
			fb.child("scouts").child("scout" + str(s)).child("currentUser").set(scouts[s-1])
		cmn = 0
		while True:	
			scouts = fb.child('scouts').get().val()
			newcmn = fb.child('currentMatchNum').get().val()
			if cmn != newcmn:
				for i in scouts.values():
					i['mostRecentUser'] = i.get('currentUser') if i.get('currentUser') != None else ''
				fb.child('scouts').update(scouts)
				cmn = fb.child('currentMatchNum').get().val()
				data = fb.child('TempTeamInMatchDatas').get().val()
				available = fb.child('available').get().val()
				if data == None or cmn == None:
					firstMatchTeams = firb.get('Matches/1', 'redAllianceTeamNumbers') + firb.get('Matches/1', 'blueAllianceTeamNumbers')
					fb.child('currentMatchNum').set(cmn)
					for i in range(1, 19):
						if i <=3:
							fb.child('scouts').child("scout" + str(i)).child('team').set(firstMatchTeams[0])
						elif i >= 4 and i <= 6:
							fb.child('scouts').child("scout" + str(i)).child('team').set(firstMatchTeams[1])
						elif i >= 7 and i <= 9:
							fb.child('scouts').child("scout" + str(i)).child('team').set(firstMatchTeams[2])
						elif i >= 10 and i <= 12:
							fb.child('scouts').child("scout" + str(i)).child('team').set(firstMatchTeams[3])
						elif i >= 13 and i <= 15:
							fb.child('scouts').child("scout" + str(i)).child('team').set(firstMatchTeams[4])
						elif i >= 16 and i <= 18:
							fb.child('scouts').child("scout" + str(i)).child('team').set(firstMatchTeams[5])
						else:
							fb.child('scouts').child("scout" + str(i)).child('team').set(None)
					continue
				self.spr.calculateScoutPrecisionScores(data.items(), available)
				teams = firb.get('Matches/' + str(cmn + 1),'redAllianceTeamNumbers') + firb.get('Matches/' + str(cmn + 1),'blueAllianceTeamNumbers')	
				self.spr.organizeScouts(available)
				availableScouts = available.keys()
				random.shuffle(availableScouts)
				sprs = self.spr.getRobotNumbersForScouts(fb.child('scouts').get().val(), teams)
				for scoutNum, value in sprs.items():
					fb.child("scouts").child(scoutNum).child('currentUser').set(value.get('currentUser'))
					fb.child("scouts").child(scoutNum).child('team').set(value['team'])
			else:
				print "still match " + str(cmn)
			time.sleep(1)

srp = ScoutRotatorProcess(ScoutPrecision())
srp.start()