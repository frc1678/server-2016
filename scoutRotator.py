import pyrebase
import DataModel
import time
from firebase import firebase as fir
from SPR import ScoutPrecision

(secret, url) = ('IMXOxXD3FjOOUoMGJlkAK5pAtn89mGIWAEnaKJhP', 'https://1678-strat-dev-2016.firebaseio.com/')
auth = fir.FirebaseAuthentication(secret, "1678programming@gmail.com", True, True)
fire = fir.FirebaseApplication(url, auth)
url = '1678-scout-rotator'
config = {
	"apiKey": "mykey",
	"authDomain": url + ".firebaseapp.com",
	"databaseURL": "https://scout-rotator.firebaseio.com/",
	"storageBucket": url + ".appspot.com"
}
firebase = pyrebase.initialize_app(config)
fb = firebase.database()
scouts = range(20)
spr = ScoutPrecision()
while True:
	spr.cycle += 1
	fb.child("scouts").update(spr.calculateScoutPrecisionScores(fire.get("/TempTeamInMatchDatas", None)))
	time.sleep(2)
