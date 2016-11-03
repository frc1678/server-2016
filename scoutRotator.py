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
url = '1678-scout-rotator'
config = {
	"apiKey": "mykey",
	"authDomain": url + ".firebaseapp.com",
	"databaseURL": "https://scout-rotator.firebaseio.com/",
	"storageBucket": url + ".appspot.com"
}


while True:
	
	cmn = fire.get('/', 'currentMatchNum')
	print fire.get('/Matches/' + str(cmn + 1), 'redAllianceTeamNumbers')
	firebase = pyrebase.initialize_app(config)
	fb = firebase.database()
	scouts = range(20)
	spr = ScoutPrecision()
	spr.calculateScoutPrecisionScores(fire.get("/TempTeamInMatchDatas", None))
	try:
		cmn = fire.get('/', 'currentMatchNum')
		teams = fire.get('/Matches/' + str(cmn + 1), 'redAllianceTeamNumbers') + fire.get('/Matches/' + str(cmn + 1), 'blueAllianceTeamNumbers')
		spr.organizeScouts(teams)
	except:
		continue
	time.sleep(2)
