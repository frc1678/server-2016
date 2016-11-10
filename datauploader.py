import pyrebase
import time
import random


config = {
	"apiKey": "mykey",
	"authDomain": "1678-scouting-2016.firebaseapp.com",
	"databaseURL": "https://1678-scouting-2016.firebaseio.com",
	"storageBucket": "1678-scouting-2016.appspot.com"
}

firebase = pyrebase.initialize_app(config)
firebase = firebase.database()
a = ["A", "B", "C"]
cycle = 0
while True:
	if cycle == 3:
		cycle = 0
	key = raw_input("key for match and scoutname: ").split()
	name = key[1]
	key = key[0]
	basicTIMD = {
 		 "alliance" : "blue",
 		 "didChallengeTele" : False,
 		 "didGetDisabled" : False,
		  "didGetIncapacitated" : False,
		  "didReachAuto" : False,
		  "didScaleTele" : False,
		  "matchNumber" : int(key.split("Q")[1]),
		  "numBallsKnockedOffMidlineAuto" : random.randint(0,2),
		  "numGroundIntakesTele" : random.randint(0,2),
		  "numHighShotsMadeAuto" : random.randint(0,2),
		  "numHighShotsMadeTele" : random.randint(0,2),
		  "numHighShotsMissedAuto" : random.randint(0,2),
		  "numHighShotsMissedTele" : random.randint(0,2),
		  "numLowShotsMadeAuto" : random.randint(0,2),
		  "numLowShotsMadeTele" : random.randint(0,2),
		  "numLowShotsMissedAuto" : random.randint(0,2),
		  "numLowShotsMissedTele" : random.randint(0,2),
		  "numShotsBlockedTele" : random.randint(0,2),
		  "timesFailedCrossedDefensesAuto": {
				"rp": [1.163],
				"rw": [1, 2.234]
			},
		  "scoutName" : name,
		  "teamNumber" : int(key.split("Q")[0])
		}
	superDict = {
		"rankSpeed": 1,
		"rankDefense": 2,
		"rankAgility": 1,
		"rankTorque": 1,
		"rankBallControl": 1,
	}
	firebase.child('TempTeamInMatchDatas').child(key +  "-" + a[cycle]).set(basicTIMD)
	firebase.child('TeamInMatchDatas').child(key).update(superDict)
	cycle += 1
	time.sleep(2)
