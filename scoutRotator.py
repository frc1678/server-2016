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
		url = '1678-scouting-2016'
		config = {
			"apiKey": "mykey",
			"authDomain": url + ".firebaseapp.com",
			"databaseURL": "https://" + url + ".firebaseio.com/",
			"storageBucket": url + ".appspot.com"
		}
		firebase = pyrebase.initialize_app(config)
		fb = firebase.database()

		while True:	
			scouts = range(20)
			self.spr.calculateScoutPrecisionScores(fb.child('TempTeamInMatchDatas').get().val().items())
			cmn = fb.child('currentMatchNum').get().val()
			teams = fb.child('Matches').child(str(cmn + 1)).get('redAllianceTeamNumbers').val() + fb.child('Matches').child(str(cmn + 1)).get('blueAllianceTeamNumbers').val()		
			self.spr.organizeScouts()
			sprs = self.spr.getRobotNumbersForScouts(fb.child('scouts').get().val(), teams)
			fb.child('scouts').update(sprs)
			time.sleep(50)
