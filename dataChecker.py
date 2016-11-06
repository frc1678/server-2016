import pyrebase
import numpy as np
import utils
import time

config = {
	"apiKey": "mykey",
	"authDomain": "1678-scouting-2016.firebaseapp.com",
	"databaseURL": "https://1678-scouting-2016.firebaseio.com",
	"storageBucket": "1678-scouting-2016.appspot.com"
}

averageKeys = ["timesFailedCrossedDefensesTele", "timesFailedCrossedDefensesAuto", "timesSuccessfulCrossedDefensesTele",
			   "timesSuccessfulCrossedDefensesAuto"]
listKeys = ["ballsIntakedAuto"]

firebase = pyrebase.initialize_app(config)
firebase = firebase.database()

def commonValue(vals):
	if len(set(map(type, vals))) != 1: return
	if list(set(map(type, vals)))[0] == str:
		if (vals[0] == "true" or vals[0] == "false"):
			return bool(joinList(map(lambda v: int(utils.convertFirebaseBoolean(v)), vals)))
		else: return vals
	else:
		return joinList(map(lambda v: int(utils.convertFirebaseBoolean(v)), vals))

	
def joinList(values):
	a = map(values.count, values)
	mCV = values[a.index(max(a))]
	return mCV if values.count(mCV) > len(values) / 2 else np.mean(values)

def joinValues(key):
	return {k : avgDict(map(lambda tm: tm[k], consolidationGroups[key])) if k in averageKeys else (extendList(map(lambda tm: tm[k], consolidationGroups[key])) if k in listKeys else commonValue(map(lambda tm: tm[k], consolidationGroups[key]))) for k in consolidationGroups[key][0].keys()}	

def extendList(lis):
	a = [v for l in lis for v in l]
	vs = list(set(filter(lambda v: a.count(v) > len(lis) / 2, a)))
	print vs
	return vs if len(vs) > 0 else list(set(a))

def avgDict(dicts):
	return {d : map(np.mean, zip(*map(lambda tm: tm.get(d) if tm.get(d) != None else [0], dicts))) for d in extendList(map(lambda x: x.keys(), dicts))}

while True:
	tempTIMDs = firebase.child("TempTeamInMatchDatas").get().val()
	if tempTIMDs == None:
		print "No data"
		time.sleep(1)
		continue
	consolidationGroups = {}
	for (temptimdKey, temptimd) in tempTIMDs.items():
		actualKey = temptimdKey.split("-")[0]
		if actualKey in consolidationGroups.keys():
			consolidationGroups[actualKey].append(temptimd)
		else:
			consolidationGroups[actualKey] = [temptimd]

	consolidationGroups = utils.makeASCIIFromJSON(consolidationGroups)
	map(lambda key: firebase.child("TeamInMatchDatas").update({key : joinValues(key)}), consolidationGroups.keys())
	print str(map(joinValues, consolidationGroups.keys()))  + " consolidated"
	time.sleep(1)




