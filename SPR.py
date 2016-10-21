import utils
import numpy as np
import CacheModel as cache
import itertools
import pdb
from multiprocessing import Process
import TBACommunicator


import pyrebase
import numpy as np
import utils

config = {
	"apiKey": "mykey",
	"authDomain": "1678-strat-dev-2016.firebaseapp.com",
	"databaseURL": "https://1678-strat-dev-2016.firebaseio.com",
	"storageBucket": "1678-strat-dev-2016.appspot.com"
}

averageKeys = ["timesFailedCrossedDefensesTele", "timesFailedCrossedDefensesAuto", "timesSuccessfulCrossedDefensesTele",
			   "timesSuccessfulCrossedDefensesAuto"]
listKeys = ["ballsIntakedAuto"]

firebase = pyrebase.initialize_app(config)
firebase = firebase.database()
tempTIMDs = firebase.child("TempTeamInMatchDatas").get().val()

# Scout Performance Analysis
class ScoutPrecision(object):
	"""docstring for ScoutPerformance"""
	def __init__(self):
		super(ScoutPrecision, self).__init__()
		self.sprs = {}
		self.cycle = 0
		self.TBAC = TBACommunicator.TBACommunicator()
		self.keysToPointValues = {
			"numHighShotsMadeAuto" : 10,
			"numLowShotsMadeAuto" : 5,
			"numHighShotsMadeTele" : 5,
			"numLowShotsMadeTele" : 2,
		}
		self.k = ["timesSuccessfulCrossedDefensesTele"]

	def filterToMultiScoutTIMDs(self):
		return filter(lambda tm: type(tm.scoutName) == list, self.comp.timds)

	def getAllScoutNames(self):
		return list(set([scout for array in map(lambda t: t.scoutName, filterToMultiScoutTIMDs()) for scout in array]))

	def getTotalTIMDsForScoutName(self, scoutName):
		return len(map(lambda v: v["scoutName"] == scoutName, tempTIMDs.values()))

	def findOddScoutForDataPoint(self, tempTIMDs, key):
		scouts = map(lambda k: k["scoutName"], tempTIMDs)
		values = map(lambda t: t[key], tempTIMDs)
		commonValue = max(map(lambda v: values.count(v), values))
		if not values.count(commonValue) > len(values) / 2:
			commonValue = np.mean(values)
		differenceFromCommonValue = map(lambda v: abs(v - commonValue), values)
		for c in range(len(differenceFromCommonValue)):
			self.sprs[scouts[c]] = (self.sprs.get(scouts[c]) or 0) + differenceFromCommonValue[c]

	def getScoutPrecisionForDefenses(self, tempTIMDs, key):
		scouts = map(lambda k: k["scoutName"], tempTIMDs)
		values = map(lambda t: t[key], tempTIMDs)
		defenseKeys = map(lambda t: t.keys(), values)
		finalKeys = self.extendList(defenseKeys)
		for s in range(len(scouts)):
			self.sprs[scouts[s]] = (self.sprs.get(scouts[s]) or 0) + len(set(defenseKeys[s]) & set(finalKeys))
	
	def extendList(self, lis):
		a = [v for l in lis for v in l]
		vs = list(set(filter(lambda v: a.count(v) > len(lis) / 2, a)))
		return vs if len(vs) > 0 else list(set(a))


	def calculateScoutPrecisionScores(self, tempTimds):
		consolidationGroups = {}
		for (temptimdKey, temptimd) in tempTIMDs.items():
			actualKey = temptimdKey.split("-")[0]
			if actualKey in consolidationGroups.keys():
				consolidationGroups[actualKey].append(temptimd)
			else:
				consolidationGroups[actualKey] = [temptimd]

		for v in consolidationGroups.values():
			for temp in v:
				for k in temp.keys():
					if k in self.keysToPointValues.keys():
						self.findOddScoutForDataPoint(v, k)
					if k in self.k:
						self.getScoutPrecisionForDefenses(v, k)
		return {k:(v/float(self.cycle)/float(self.getTotalTIMDsForScoutName(k))) for (k,v) in self.sprs.items()}

	def rankScouts(self):
		return sorted(self.sprs.keys(), key=lambda k: self.sprs[k])
			


