import utils
import numpy as np
import CacheModel as cache
import itertools
import TBACommunicator
import Math
import random

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
		self.robotNumToScouts = {}
		self.TBAC = TBACommunicator.TBACommunicator()
		self.keysToPointValues = {
			"numHighShotsMadeAuto" : 1,
			"numLowShotsMadeAuto" : 1,
			"numHighShotsMadeTele" : 1,
			"numLowShotsMadeTele" : 1,
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


	def calculateScoutPrecisionScores(self, temp):
		self.cycle += 1
		consolidationGroups = {}
		for k, c in temp:
			b = k.split('-')[0]
			if b not in consolidationGroups.keys():
				consolidationGroups[b] = [c]
			else:
				consolidationGroups[b] += [c]
		print consolidationGroups.keys()

		for v in consolidationGroups.values():
			for temp in v:
				for k in temp.keys():
					if k in self.keysToPointValues.keys():
						self.findOddScoutForDataPoint(v, k)
					if k in self.k:
						self.getScoutPrecisionForDefenses(v, k)
		print self.sprs.keys()
		self.sprs = {k:(v/float(self.cycle)/float(self.getTotalTIMDsForScoutName(k))) for (k,v) in self.sprs.items()}

	def rankScouts(self):
		return sorted(self.sprs.keys(), key=lambda k: self.sprs[k])

	def getScoutFrequencies(self):
		rankedScouts = self.rankScouts()
		return {i:rankedScouts.index(i) * (100/(len(rankedScouts) - 1)) + 1 for i in rankedScouts}
	
	def organizeLowScouts(self, ls):
		b = []
		rankedScouts = self.rankScouts()	
		for i in range(3):
			array = []
			for i in range(len(ls)):
				ind = random.randint(0, len(ls)-1)
				array.append(ls[ind])
				del ls[ind]
			b.append(array)
			if len(ls) == 0:
				break
		return b



	def organizeScouts(self):
		a = []
		for k,v in self.getScoutFrequencies().items():
			a += [k] * v
		b = {}
		scoutsInGrouping = []
		for i in range(3):
			index = random.randint(0, len(a) - 1)
			b[i] = a[index]
			a = filter(lambda s: s != a[index], a)				
			scoutsInGrouping = list(set(a))
		
		groupScouts = self.organizeLowScouts(scoutsInGrouping)
		for i in range(3, 3 + len(groupScouts)):
			b[i] = groupScouts[i-3]
		self.robotNumToScouts = b

	def robotNumberFromName(self, scoutName, currentTeams):
		for k,v in self.robotNumToScouts.items():
			if scoutName in v:
				return currentTeams[k]

	def getRobotNumbersForScouts(self, scoutRotatorDict, currentTeams):
		di = {}
		for scoutNum, value in scoutRotatorDict.items():
			if value.get('mostRecentUser') in self.sprs.keys():
				di[scoutNum] = {}
				di[scoutNum]['mostRecentUser'] = value['mostRecentUser']
				di[scoutNum]['team'] = self.robotNumberFromName(value['mostRecentUser'], currentTeams)
		return di





