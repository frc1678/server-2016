import pyrebase
import DataModel
import time
from firebase import firebase as fir
import Math
from SPR import ScoutPrecision
import random

(secret, url) = ('qVIARBnAD93iykeZSGG8mWOwGegminXUUGF2q0ee', 'https://1678-scouting-2016.firebaseio.com/')
auth = fir.FirebaseAuthentication(secret, "1678programming@gmail.com", True, True)
fire = fir.FirebaseApplication(url, auth)
url = '1678-scouting-2016'
config = {
	"apiKey": "mykey",
	"authDomain": url + ".firebaseapp.com",
	"databaseURL": "https://" + url + ".firebaseio.com/",
	"storageBucket": url + ".appspot.com"
}

firebase = pyrebase.initialize_app(config)
fb = firebase.database()
a = {}

while True:	
	scouts = range(20)
	spr = ScoutPrecision()
	spr.calculateScoutPrecisionScores(fb.child('TempTeamInMatchDatas').get().val().items())
	cmn = fire.get('/', 'currentMatchNum')
	teams = fire.get('/Matches/' + str(cmn + 1), 'redAllianceTeamNumbers') + fire.get('/Matches/' + str(cmn + 1), 'blueAllianceTeamNumbers')		
	spr.organizeScouts()
	sprs = spr.getRobotNumbersForScouts(fb.child('scouts').get().val(), teams)
	fb.child('scouts').update(sprs)
	time.sleep(1)
