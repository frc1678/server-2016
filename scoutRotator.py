import pyrebase
import DataModel
import time
from firebase import firebase as fir
import SPR
import multiprocessing
import random

beg = False
class ScoutRotatorProcess(multiprocessing.Process):
	"""docstring for ScoutRotatorProcess"""
	def __init__(self, spr):
		super(ScoutRotatorProcess, self).__init__()
		self.spr = spr

	def getScoutNameAndKeyForTempTIMD(self, scoutNum, value, cmn):
		if cmn == None: cmn = 0
		if value.get('team') != None and value.get('currentUser') not in [None, '']:
			return (str(value.get('team')) + "Q" + str(int(cmn) + 1) + "-" + scoutNum.replace('scout', ''), value.get('currentUser'))

	def uploadScoutNamesToTempTIMDs(self, scoutDict, cmn):
		scoutNamesAndTempTIMDs = {}
		for k,v in scoutDict.items():
			keyAndTIMD = self.getScoutNameAndKeyForTempTIMD(k, v, cmn)
			if keyAndTIMD != None:
				scoutNamesAndTempTIMDs[keyAndTIMD[0]] = {'scoutName' : keyAndTIMD[1]}
		return scoutNamesAndTempTIMDs

	def run(self):
		(superSecret, url) = ('qVIARBnAD93iykeZSGG8mWOwGegminXUUGF2q0ee', 'https://1678-scouting-2016.firebaseio.com/') 
		# (superSecret, url) = ('lGufYCifprPw8p1fiVOs7rqYV3fswHHr9YLwiUWh', 'https://1678-extreme-testing.firebaseio.com/')
		scoutNames = 'westley mx tim jesse sage alex janet livy gemma justin berin aiden rolland rachel zoe ayush jona angela kyle wesley'.split()

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
		for i in scoutNames:
			if beg:
				fb.child("available").child(i).set(1)
		cmn = 0
		while True:	
			scouts = fb.child('scouts').get().val()
			newcmn = fb.child('currentMatchNum').get().val()
			if cmn != newcmn:
				if scouts != None:
					for i in scouts.values():
						i['mostRecentUser'] = i.get('currentUser') if i.get('currentUser') != None else ''
				fb.child('scouts').update(scouts)
				cmn = fb.child('currentMatchNum').get().val()
				data = fb.child('TempTeamInMatchDatas').get().val()
				print data
				available = fb.child('available').get().val()
				if data == None or cmn == None:
					print "NOne"
					firstMatchTeams = firb.get('Matches/1', 'redAllianceTeamNumbers') + firb.get('Matches/1', 'blueAllianceTeamNumbers')
					n = len(filter(lambda k: available.get(k) == 1, available.keys())[:17])
					scoutCombos = list(SPR.sum_to_n(n,6,3))[random.randint(0, len(list(SPR.sum_to_n(n,6,3))) - 1)]
					scoutNum = 1
					i = 0
					print scoutCombos
					for scoutAssignment in scoutCombos:
						for s in range(scoutAssignment):
							fb.child("scouts").child("scout" + str(scoutNum)).child("currentUser").set(scoutNames[scoutNum-1])
							fb.child("scouts").child("scout" + str(scoutNum)).child("team").set(firstMatchTeams[i])
							scoutNum += 1
						i += 1

					continue
				self.spr.calculateScoutPrecisionScores(data.items(), available)
				print cmn
				teams = firb.get('Matches/' + str(cmn + 1),'redAllianceTeamNumbers') + firb.get('Matches/' + str(cmn + 1),'blueAllianceTeamNumbers')	
				self.spr.organizeScouts(available)
				availableScouts = available.keys()
				random.shuffle(availableScouts)
				sprs = self.spr.getRobotNumbersForScouts(fb.child('scouts').get().val(), teams)
				print sprs
				for scoutNum, value in sprs.items():
					fb.child("scouts").child(scoutNum).child('currentUser').set(value.get('currentUser'))
					fb.child("scouts").child(scoutNum).child('team').set(value.get('team'))
			else:
				print "still match " + str(cmn)
			time.sleep(1)

srp = ScoutRotatorProcess(SPR.ScoutPrecision())
srp.start()