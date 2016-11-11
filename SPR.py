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

def sum_to_n(n, size, limit=None):
    """Produce all lists of `size` positive integers in decreasing order
    that add up to `n`."""
    if size == 1:
        yield [n]
        return
    if limit is None:
        limit = n
    start = (n + size - 1) // size
    stop = min(limit, n - size + 1) + 1
    for i in range(start, stop):
        for tail in sum_to_n(n - i, size - 1, i):
            yield [i] + tail

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
		self.k = ["timesSuccessfulCrossedDefensesTele", 'timesSuccessfulCrossedDefensesAuto', 'timesFailedCrossedDefensesTele', 'timesFailedCrossedDefensesAuto']

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
		print key
		defenseKeys = map(lambda t: t.keys(), tempTIMDs)
		finalKeys = self.extendList(defenseKeys)
		for s in range(len(scouts)):
			self.sprs[scouts[s]] = (self.sprs.get(scouts[s]) or 0) + len(set(defenseKeys[s]) & set(finalKeys))
	
	def extendList(self, lis):
		a = self.extendListNoSet(lis)
		vs = list(set(filter(lambda v: a.count(v) > len(lis) / 2, a)))
		return vs if len(vs) > 0 else list(set(a))

	def extendListNoSet(self, lis):
		return [v for l in lis for v in l]

	def calculateScoutPrecisionScores(self, temp, available):
		self.cycle += 1
		consolidationGroups = {}
		for k, c in temp:
			b = k.split('-')[0]
			if b not in consolidationGroups.keys():
				consolidationGroups[b] = [c]
			else:
				consolidationGroups[b] += [c]

		for v in consolidationGroups.values():
			for temp in v:
				for k in temp.keys():
					if k in self.keysToPointValues.keys():
						self.findOddScoutForDataPoint(v, k)
					if k in self.k:
						self.getScoutPrecisionForDefenses(v, k)
		self.sprs = {k:(v/float(self.cycle)/float(self.getTotalTIMDsForScoutName(k))) for (k,v) in self.sprs.items()}
		for a in available.keys()[:17]:
			if a not in self.sprs.keys() and available.get(a) == 1:
				self.sprs[a] = np.mean(self.sprs.values())
	
	def rankScouts(self, available):
		return sorted(self.sprs.keys(), key=lambda k: self.sprs[k])

	def getScoutFrequencies(self, available):
		rankedScouts = self.rankScouts(available)
		return {i:rankedScouts.index(i) * (100/(len(rankedScouts) - 1)) + 1 for i in rankedScouts}

	def organizeLowScouts(self, ls, numScouts):
		b = []
		for i in range(numScouts):
			if len(ls) > 0:
				ind = random.randint(0, len(ls)-1)
				b.append(ls[ind])
				del ls[ind]
		return b

	def organizeScouts(self, available):
		a = self.extendListNoSet([[k] * v for k,v in self.getScoutFrequencies(available).items()])
		b = {}
		scoutsInGrouping = []
		scoutCombos = list(sum_to_n(len(list(set(a))), 6, 3))
		index = random.randint(0, len(scoutCombos) - 1)
		i = 0
		for numScouts in scoutCombos[index]:
			scoutsInGrouping = list(set(a))
			if numScouts == 1:
				index = random.randint(0, len(a) - 1)
				b[i] = [a[index]]
				a = filter(lambda s: s != a[index], a)				
			else:
				b[i] = self.organizeLowScouts(scoutsInGrouping, numScouts)
				a = filter(lambda s: s not in b[i], a)

			i += 1
		self.robotNumToScouts = b

	def robotNumberFromName(self, scoutName, currentTeams):
		return [currentTeams[k] for k,v in self.robotNumToScouts.items() if scoutName in v][0]

	def getRobotNumbersForScouts(self, scoutRotatorDict, currentTeams):
		scoutsInRotation = map(lambda s: s[0], filter(lambda s: s[0] != None and s[1] != None, map(lambda v: (v.get('mostRecentUser'), v.get('team')), scoutRotatorDict.values())))
		emptySlots = filter(lambda m: m.get('mostRecentUser') in [None,''], scoutRotatorDict.values())
		di = {}
		print self.extendListNoSet(self.robotNumToScouts.values())
		scoutNums = [k for k in scoutRotatorDict.keys() if scoutRotatorDict[k].get('currentUser') not in self.extendListNoSet(self.robotNumToScouts.values())]
		for scoutNum in scoutNums:
			di[scoutNum] = {'team' : None}
			di[scoutNum] = {'currentUser' : ''}
		for scout in self.extendListNoSet(self.robotNumToScouts.values()):
			if scout in scoutsInRotation:
				scoutNum = [k for k,v in scoutRotatorDict.items() if v.get('mostRecentUser') == scout][0]
			else:
				if len(emptySlots) > 0:
					scoutNum = scoutRotatorDict.keys()[scoutRotatorDict.values().index(emptySlots[0])]
					del emptySlots[0]
				else:
					scoutNum = [k for k in scoutRotatorDict.keys() if scoutRotatorDict[k]['mostRecentUser'] not in self.extendListNoSet(self.robotNumToScouts.values())][0]
					scoutsInRotation.append(scout)
			di[scoutNum] = {'currentUser' : scout, 'team' : self.robotNumberFromName(scout, currentTeams)}


		return di





