import pyrebase
import DataModel
import time
from firebase import firebase as fir
from SPR import ScoutPrecision
import multiprocessing

class ScoutRotatorProcess(multiprocessing.Process):
	"""docstring for ScoutRotatorProcess"""
	def __init__(self, spr):
		super(ScoutRotatorProcess, self).__init__()
		self.spr = spr

	def run(self):
		(superSecret, url) = ('qVIARBnAD93iykeZSGG8mWOwGegminXUUGF2q0ee', 'https://1678-scouting-2016.firebaseio.com/') 


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
		cmn = 1
		while True:	
			newcmn = fb.child('currentMatchNum').get().val()
			if cmn != newcmn:
				cmn = fb.child('currentMatchNum').get().val()
				data = fb.child('TempTeamInMatchDatas').get().val()
				available = fb.child('availableScouts').get().val()
				if data == None or cmn == None:
					firstMatchTeams = firb.get('Matches/1', 'redAllianceTeamNumbers') + firb.get('Matches/1', 'blueAllianceTeamNumbers')
					fb.child('currentMatchNum').set(1)
					print firstMatchTeams
					for i in range(1, 21):
						if i <=3:
							fb.child('scouts').child("scout" + str(i)).child('team').set(firstMatchTeams[i - 1])
						elif i >= 4 and i <= 6:
							fb.child('scouts').child("scout" + str(i)).child('team').set(firstMatchTeams[3])
						elif i >= 8 and i <= 10:
							fb.child('scouts').child("scout" + str(i)).child('team').set(firstMatchTeams[4])

						elif i >= 10 and i <= 12:
							fb.child('scouts').child("scout" + str(i)).child('team').set(firstMatchTeams[5])
						else:
							fb.child('scouts').child('scouts' + str(i)).child('mostRecentUser').set('')
					continue
				self.spr.calculateScoutPrecisionScores(data.items())
				teams = firb.get('Matches/' + str(cmn + 1),'redAllianceTeamNumbers') + firb.get('Matches/' + str(cmn + 1),'blueAllianceTeamNumbers')	
				self.spr.organizeScouts()
				sprs = self.spr.getRobotNumbersForScouts(fb.child('scouts').get().val(), teams, cmn)
				fb.child('scouts').update(sprs)
			else:
				print "still match " + str(cmn)

srp = ScoutRotatorProcess(ScoutPrecision())
srp.start()