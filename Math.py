
# Math.py
import utils
import DataModel
import firebaseCommunicator
import math
import numpy as np
import dmutils
import scipy as sp
from operator import attrgetter
import scipy.stats as stats
import sys, traceback


class Calculator(object):
	"""docstring for Calculator"""
	def __init__(self, competition):
		super(Calculator, self).__init__()
		self.comp = competition
		self.categories = ['a', 'b', 'c', 'd', 'e']
		self.ourTeamNum = 1678
		self.defenseKeys = ['pc', 'cdf', 'mt', 'rt', 'rw', 'lb', 'rp', 'sp', 'db']
		self.defenseDictionary = {'a' : ['pc', 'cdf'],
			'b' : ['mt', 'rp'],
			'c' : ['sp', 'db'],
			'd' : ['rw', 'rt'],
			'e' : ['lb']
		}
	
	def bToI(self, boolean):
		if boolean: return 1
		if not boolean: return 0

	# Calculated Team Data
	def getAverageForDataFunctionForTeam(self, team, dataFunction):
		return np.mean(map(dataFunction, dmutils.getCompletedTIMDsForTeam(team)))

	def getStandardDeviationForDataFunctionForTeam(self, team, dataFunction):
		return np.std(map(dataFunction, dmutils.getCompletedTIMDsForTeam(team)))	

	def averageTIMDObjectOverMatches(self, team, key, coefficient = 1):
		return np.mean([utils.makeDictFromTIMD(timd)[key] for timd in dmutils.getCompletedTIMDsForTeam(team)])

	def getTIMDHighShotAccuracyTele(self, timd):
		return timd.numHighShotsMadeTele / (timd.numHighShotsMadeTele + timd.numHighShotsMissedTele)

	def getTIMDHighShotAccuracyAuto(self, timd):
		return timd.numHighShotsMadeAuto / (timd.numHighShotsMadeAuto + timd.numHighShotsMissedAuto)

	def getTIMDLowShotAccuracyTele(self, timd):
		return timd.numLowShotsMadeTele / (timd.numLowShotsMadeTele + timd.numLowShotsMissedTele)

	def getTIMDLowShotAccuracyAuto(self, timd):
		if timd.numLowShotsMadeAuto + timd.numLowShotsMissedAuto > 0:
			return timd.numLowShotsMadeAuto / (timd.numLowShotsMadeAuto + timd.numLowShotsMissedAuto)
		else:
			return 0

	def flattenDictionary(self, dictionary):
		flattenedDict = {}
		for categoryDict in dictionary.values():
			for defense, dictionary in categoryDict.items():
				flattenedDict[defense] = dictionary
		return flattenedDict


	def makeArrayOfDictionaries(self, team, key): 
 		timds = dmutils.getCompletedTIMDsForTeam(team)
 		arrayOfDictionaries = [] 
 		for timd in timds:
 			dictionary = utils.makeDictFromTIMD(timd)[key]
 			dictionary = self.flattenDictionary(dictionary)
 			for d in dictionary:
 				if dictionary[d] > None:
 					arrayOfDictionaries.append(dictionary) 
  		return arrayOfDictionaries 

  	def averageDefenseCrossesTele(self, team):
  		avgDefenseCrosses = 0
  		timds = dmutils.getCompletedTIMDsForTeam(team)
  		for timd in timds:
  			defenses = self.flattenDictionary(timd.timesSuccessfulCrossedDefensesTele)
  			avgDefenseCrosses += sum(defenses.values())
  		return avgDefenseCrosses / len(timds)

  	def averageDefenseCrossesAuto(self, team):
  		avgDefenseCrosses = 0
  		timds = dmutils.getCompletedTIMDsForTeam(team)
  		for timd in timds:
  			defenses = self.flattenDictionary(timd.timesSuccessfulCrossedDefensesAuto)
  			avgDefenseCrosses += sum(defenses.values())
  		return avgDefenseCrosses / len(timds)


 	def averageDictionaries(self, array):
 		subOutputDict = {}
 		outputDict = {'a' : {}, 'b' : {}, 'c' : {}, 'd': {}, 'e' : {}}
 		#print array
 		for dic in array:
			for key, value in dic.items():
				avg = 0.0
				#print "val " + str(value)
				for dictionary in array:
					# print key
					if key in dictionary.keys():
						avg += len(dictionary[key]) - 1
					#print "avg for " + str(key) + " is " + str(avg)
				avg /= len(array) 
				subOutputDict[key] = avg
		for key in subOutputDict:
			if key == 'cdf' or key == 'pc':
				outputDict['a'][key] = subOutputDict[key]
			elif key == 'mt' or key == 'rp':
				outputDict['b'][key] = subOutputDict[key]
			elif key == 'sp' or key == 'db':
				outputDict['c'][key] = subOutputDict[key]
			elif key == 'rw' or key == 'rw':
				outputDict['d'][key] = subOutputDict[key]
			elif key == 'lb':
				outputDict['e'][key] = subOutputDict[key]
 		#print outputDict
 		return outputDict

 	def twoBallAutoAccuracy(self, team):
 		timds = dmutils.getCompletedTIMDsForTeam(team)
 		twoBallAutoCompleted = 0
 		for timd in timds:
 			totalNumShots = timd.numHighShotsMadeAuto + timd.numLowShotsMadeAuto + timd.numHighShotsMissedAuto + timd.numLowShotsMissedAuto
 			if totalNumShots > 2:
 				twoBallAutoCompleted += 1
 		return twoBallAutoCompleted / len(timds)

	def blockingAbility(self, team):
		allHighShotsAccuracies = 0
		numTeams = 0
		for team in self.comp.teams:
			if team.calculatedData.highShotAccuracyTele != None: 
				allHighShotsAccuracies += team.calculatedData.highShotAccuracyTele 
				numTeams += 1
		avgHighShotAccuracy = allHighShotsAccuracies / numTeams
		if team.calculatedData.avgShotsBlocked != None:
			return 5 * avgHighShotAccuracy * team.calculatedData.avgShotsBlocked

	def autoAbility(self, team): 
		t = team.calculatedData
		if t.avgHighShotsAuto != None:
			if sum(self.flattenDictionary(t.avgSuccessfulTimesCrossedDefensesAuto).values()) >= 1:
				return 10 + (10 * t.avgHighShotsAuto) + (5 * t.avgLowShotsAuto) + (2 * t.reachPercentage)
			return (10 * t.avgHighShotsAuto) + (5 * t.avgLowShotsAuto) + (2 * t.reachPercentage)

	def teleopShotAbility(self, team): return (5 * team.calculatedData.avgHighShotsTele + 2 * team.calculatedData.avgLowShotsTele)

	def siegeAbility(self, team): 
		if team.calculatedData.scalePercentage != None and team.calculatedData.challengePercentage != None:
			return (15 * team.calculatedData.scalePercentage + 5 * team.calculatedData.challengePercentage)

	def singleSiegeAbility(self, timd): return (15 * self.bToI(timd.didScaleTele) + 5 * self.bToI(timd.didChallengeTele))

	def siegeConsistency(self, team): 
		if team.calculatedData.scalePercentage != None and team.calculatedData.challengePercentage != None:
			return team.calculatedData.scalePercentage + team.calculatedData.challengePercentage

	def siegePower(self, team): 
		return (team.calculatedData.siegeConsistency * team.calculatedData.siegeAbility)


	def numAutoPointsForTIMD(self, timd):
		defenseCrossesInAuto = 0
		for defense, value in timd.timesSuccessfulCrossedDefensesAuto.items():
			defenseCrossesInAuto += len(value)
		if defenseCrossesInAuto > 1: defenseCrossesInAuto = 1
		return 10 * int(timd.numHighShotsMadeAuto) + 5 * int(timd.numLowShotsMadeAuto) + 2 * (1 if timd.didReachAuto else 0) + 10 * int(defenseCrossesInAuto)

	def numRPsForTeam(self, team):
		totalRPsForTeam = 0
		for m in dmutils.getCompletedMatchesForTeam(team):
			RPs = self.RPsGainedFromMatch(m)
			if team.number in m.blueAllianceTeamNumbers:
				totalRPsForTeam += RPs['blue']
			elif team.number in m.redAllianceTeamNumbers:
				totalRPsForTeam += RPs['red']
			else:
				print "ERROR: team not in match."
		return totalRPsForTeam

	def totalAvgDefenseCategoryCrossingsForAlliance(self, alliance, defenseCategory):
		totalAvgDefenseCategoryCrossings = 0
		for team in alliance:
			categoryCrossings = self.avgDefenseCategoryCrossingsForTeam(team, 'avgSuccessfulTimesCrossedDefensesTele', defenseCategory)
			if categoryCrossings != None:
				totalAvgDefenseCategoryCrossings += categoryCrossings
		return totalAvgDefenseCategoryCrossings / (len(alliance))

	def totalAvgDefenseCategoryCrossingsForAllianceWithExclusion(self, alliance, teamWithMatchesToExclude, timd, defenseCategory):
		totalAvgDefenseCategoryCrossings = 0
		for team in alliance:
			if team.number == teamWithMatchesToExclude.number:
				t = 0
				defenses = timd.timesSuccessfulCrossedDefensesTele[defenseCategory]
				for defense, value in defenses.items():
					t += len(value) 
				totalAvgDefenseCategoryCrossings += t / len(defenses)
			else:
				totalAvgDefenseCategoryCrossings += (self.avgDefenseCategoryCrossingsForTeam(team, 'avgSuccessfulTimesCrossedDefensesTele', defenseCategory))
		
		return totalAvgDefenseCategoryCrossings / (len(alliance))


	def avgDefenseCategoryCrossingsForTeam(self, team, key, defenseCategory):	#Use in standard deviation calculation for each defenseCategory
		#print utils.makeDictFromTeam(team)['calculatedData']['avgSuccessfulTimesCrossedDefensesAuto'][defenseCategory]
		#print team.calculatedData
		#print team.calculatedData
		if defenseCategory in team.__dict__['calculatedData'].__dict__[key].keys():
			category = team.__dict__["calculatedData"].__dict__[key][defenseCategory]
		else:
			return None
		#print team.calculatedData
		total = 0
		for defense in category:
			#print "TESTING" + str(value)
			if category[defense] != None:
				total += category[defense]
		if defenseCategory == 'e':
			return total
		if len(category) > 0:
			return total / len(category)
		

	def stanDevSumForDefenseCategory(self, alliance, defenseCategory): #CLEAN UP
		varianceValues = []			#add variance for each data point to array
		stanDevSum = 0
		for team in alliance:
			timds = dmutils.getCompletedTIMDsForTeam(team)
			if len(timds) == 0:
				return None
			else:
				difOfAvgSquaresTele = 0
				difOfAvgSquaresAuto = 0
				for timd in timds:	#find the variances for a team's crosses in the specified category in auto, and then the same in tele
					numCrossesForDefenseCategoryInMatchTele = 0
					numCrossesForDefenseCategoryInMatchAuto = 0
					if defenseCategory in timd.timesSuccessfulCrossedDefensesTele.keys():
						for value in timd.timesSuccessfulCrossedDefensesTele[defenseCategory].values():
							numCrossesForDefenseCategoryInMatchTele += len(value) - 1
					if defenseCategory in timd.timesSuccessfulCrossedDefensesAuto.keys():
						for value in timd.timesSuccessfulCrossedDefensesAuto[defenseCategory].values():
							if value != None:
								numCrossesForDefenseCategoryInMatchAuto += len(value) - 1
					difOfAvgSquaresTele += (self.avgDefenseCategoryCrossingsForTeam(team, 'avgSuccessfulTimesCrossedDefensesTele',  defenseCategory) - numCrossesForDefenseCategoryInMatchTele)**2 
					difOfAvgSquaresAuto += (self.avgDefenseCategoryCrossingsForTeam(team, 'avgSuccessfulTimesCrossedDefensesAuto',  defenseCategory) - numCrossesForDefenseCategoryInMatchAuto)**2 
				difOfAvgSquaresTele /= (len(timds))			#divide difference from average squared by n
				difOfAvgSquaresAuto /= (len(timds))
				varianceValues.append(difOfAvgSquaresTele)
				varianceValues.append(difOfAvgSquaresAuto)
			for i in varianceValues:	
				stanDevSum += i
			return math.sqrt(stanDevSum)

	def stanDevSumForDefenseCategoryWithExclusion(self, alliance, teamWithMatchesToExclude, sTIMD, defenseCategory): #CLEAN UP
		varianceValues = []			#add variance for each data point to array
		stanDevSum = 0
		for team in alliance:
			if team.number == teamWithMatchesToExclude.number:
				numCrossesForDefenseCategoryInMatchTele = 0
				numCrossesForDefenseCategoryInMatchAuto = 0
				for value in sTIMD.timesSuccessfulCrossedDefensesTele[defenseCategory].values():
					numCrossesForDefenseCategoryInMatchTele += len(value) - 1
				for value in sTIMD.timesSuccessfulCrossedDefensesAuto[defenseCategory].values():
					numCrossesForDefenseCategoryInMatchAuto += len(value) - 1
				varianceValues.append(difOfAvgSquaresTele)
				varianceValues.append(difOfAvgSquaresAuto)
			else:
				timds = dmutils.getCompletedTIMDsForTeam(team)
				if len(timds) == 0:
					return None
				else:
					difOfAvgSquaresTele = 0
					difOfAvgSquaresAuto = 0
					for timd in timds:	#find the variances for a team's crosses in the specified category in auto, and then the same in tele
						numCrossesForDefenseCategoryInMatchTele = 0
						numCrossesForDefenseCategoryInMatchAuto = 0
						if defenseCategory in timd.timesSuccessfulCrossedDefensesTele.keys():
							for value in timd.timesSuccessfulCrossedDefensesTele[defenseCategory].values():
								numCrossesForDefenseCategoryInMatchTele += len(value) - 1
						if defenseCategory in timd.timesSuccessfulCrossedDefensesAuto.keys():
							for value in timd.timesSuccessfulCrossedDefensesAuto[defenseCategory].values():
								numCrossesForDefenseCategoryInMatchAuto += len(value) - 1
						difOfAvgSquaresTele += (self.avgDefenseCategoryCrossingsForTeam(team, 'avgSuccessfulTimesCrossedDefensesTele',  defenseCategory) - numCrossesForDefenseCategoryInMatchTele)**2 
						difOfAvgSquaresAuto += (self.avgDefenseCategoryCrossingsForTeam(team, 'avgSuccessfulTimesCrossedDefensesAuto',  defenseCategory) - numCrossesForDefenseCategoryInMatchAuto)**2 
					difOfAvgSquaresTele /= (len(timds))			#divide difference from average squared by n
					difOfAvgSquaresAuto /= (len(timds))
					varianceValues.append(difOfAvgSquaresTele)
					varianceValues.append(difOfAvgSquaresAuto)
				for i in varianceValues:	
					stanDevSum += i
			return math.sqrt(stanDevSum)

	def numScaleAndChallengePointsForTeam(self, team): 
		if team.calculatedData.siegeAbility != None:
			return team.calculatedData.siegeAbility * len(dmutils.getCompletedTIMDsForTeam(team))

	def numSiegePointsForTIMD(self, timd):
		total = 0
		if timd.didChallengeTele: total += 5
		if timd.didScaleTele: total += 15
		return total

	def totalAvgNumShotPointsForTeam(self, team):
		#print "TESTING" + str(team.calculatedData)
		if team.calculatedData.avgHighShotsTele != None:
			return 5 * (team.calculatedData.avgHighShotsTele) + 10 * team.calculatedData.avgHighShotsAuto + 5 * team.calculatedData.avgLowShotsAuto + 2 * team.calculatedData.avgLowShotsTele
	
	def totalSDShotPointsForTeam(self, team):
		return 5 * team.calculatedData.sdHighShotsTele + 10 * team.calculatedData.sdHighShotsAuto + 5 * team.calculatedData.sdLowShotsAuto + 2 * team.calculatedData.sdLowShotsTele

	def shotDataPoints(self, team):
		return [team.calculatedData.avgHighShotsAuto, team.calculatedData.avgLowShotsTele, team.calculatedData.avgHighShotsTele, team.calculatedData.avgLowShotsAuto]

	def totalAvgNumShotsForAlliance(self, alliance):
		totalAvgNumShots = []
		[totalAvgNumShots.extend(self.shotDataPoints(team)) for team in alliance if team.calculatedData.avgHighShotsTele != None]
		return sum(totalAvgNumShots) / len(alliance)

	def totalAvgNumShotsForAllianceWithExclusion(self, alliance, teamWithMatchesToExclude, timd):
		totalAvgNumShots = 0
		for team in alliance:
			if team.number == teamWithMatchesToExclude.number:
				totalAvgNumShots += timd.numHighShotsMadeAuto + timd.numHighShotsMadeTele + timd.numLowShotsMadeAuto + timd.numLowShotsMadeTele
			else:
				totalAvgNumShots += team.calculatedData.avgHighShotsAuto + team.calculatedData.avgHighShotsTele + team.calculatedData.avgLowShotsTele + team.calculatedData.avgLowShotsAuto
		return totalAvgNumShots / len(alliance)

	def highShotAccuracyForAlliance(self, alliance):
		overallHighShotAccuracy = []
		[overallHighShotAccuracy.extend([team.calculatedData.highShotAccuracyTele, team.calculatedData.highShotAccuracyAuto]) for team in alliance if team.calculatedData.highShotAccuracyAuto != None]
		return sum(overallHighShotAccuracy) / len(overallHighShotAccuracy)

	def blockedShotPointsForAlliance(self, alliance, opposingAlliance):
		blockedShotPoints = 0
		for team in opposingAlliance:
			if team.calculatedData.avgShotsBlocked != None:
				blockedShotPoints += (self.highShotAccuracyForAlliance(alliance) * team.calculatedData.avgShotsBlocked)
		return blockedShotPoints

	def blockedShotPointsForAllianceSD(self, alliance, opposingAlliance):
		blockedShotPoints = 0.0
		for team in opposingAlliance:
			blockedShotPoints += (self.highShotAccuracyForAlliance(alliance) * team.calculatedData.sdShotsBlocked)
		return 5 * blockedShotPoints

	def reachPointsForAlliance(self, alliance):
		reachPoints = 0.0
		for team in alliance:
			if team.calculatedData.reachPercentage != None:
				reachPoints += 2 * team.calculatedData.reachPercentage
			return reachPoints

	def probabilityDensity(self, x, u, o):
		if x != None and u != None and o != None: return stats.norm.cdf(x, u, o) 

	def sumOfStandardDeviationsOfShotsForAlliance(self, alliance):
		sumOfStanDev = 0.0
		for team in alliance:
			# for timd in dmutils.getCompletedTIMDsForTeam(team):
			for key in ['numHighShotsMadeAuto', 'numLowShotsMadeAuto', 'numHighShotsMadeTele', 'numLowShotsMadeTele']:
				dataPoints = [utils.makeDictFromTIMD(timd)[key] for timd in dmutils.getCompletedTIMDsForTeam(team)]
				if len(dataPoints) > 0:
					sumOfStanDev += sp.var(dataPoints)
		return math.sqrt(sumOfStanDev / (len(alliance) * 4))

	def sumOfStandardDeviationsOfShotsForAllianceWithExclusion(self, alliance, teamWithMatchesToExclude, sTIMD):
		sumSD = 0.0
		sumVar = 0.0
		shotVariances = []
		for team in alliance:
			aHS = np.array([])
			tHS = np.array([])
			aLS = np.array([])
			tLS = np.array([])
			timds = dmutils.getCompletedTIMDsForTeam(team)
			if len(timds) == 0:
				return None
			else:
				if(team.number == teamWithMatchesToExclude.number):
					for timd in timds:
						aHS = np.append(aHS, sTIMD.numHighShotsMadeAuto)
						aLS = np.append(aLS, sTIMD.numLowShotsMadeAuto)
						tHS = np.append(tHS, sTIMD.numHighShotsMadeTele)
						tLS = np.append(tLS, sTIMD.numLowShotsMadeTele)
				for timd in timds:
					aHS = np.append(aHS, timd.numHighShotsMadeAuto)
					aLS = np.append(aLS, timd.numLowShotsMadeAuto)
					tHS = np.append(tHS, timd.numHighShotsMadeTele)
					tLS = np.append(tLS, timd.numLowShotsMadeTele)
				if len(timds) > 1:
					sumVar += sp.stats.tvar(aHS) + sp.stats.tvar(aLS) + np.var(tHS) + sp.stats.tvar(tLS)

		sumVar /= (len(alliance) * 4) 

		return math.sqrt(sumVar)

	def defenseFacedForTIMD(self, timd, defenseKey):
		match = dmutils.getMatchForNumber(timd.matchNumber)
		team = dmutils.getTeamForNumber(timd.teamNumber)
		defensePositions = timd.redDefensePositions if dmutils.teamIsOnRedAllianceInMatch(team, match) else timd.blueDefensePositions
		return defenseKey.upper() in defensePositions

	def numTimesTeamFacedDefense(self, team, defenseKey):
		return len(filter(lambda timd: self.defenseFacedForTIMD(timd, defenseKey)(self.defenseFacedForTIMD, dmutils.getCompletedTIMDsForTeam(team))))

	def numTimesCompetitionFacedDefense(self, defenseKey):
		return sum(map(self.numTimesTeamFacedDefense, self.teamsWithCompletedMatches))

	def competitionProportionForDefense(self, defenseKey):
		competitionDefenseSightings = self.numTimesCompetitionFacedDefense()
		competitionTotalNumberOfDefenseSightings = 5 * len(dmutils.getCompletedTIMDsInCompetition())
		return competitionDefenseSightings / competitionTotalNumberOfDefenseSightings

	def teamProportionForDefense(self, team, defenseKey):
		teamDefenseSightings = self.numTimesTeamFacedDefense(team, defenseKey)
		teamTotalNumberOfDefenseSightings = 5 * len(dmutils.getCompletedTIMDsForTeam(team))
		return teamDefenseSightings / teamTotalNumberOfDefenseSightings

	def alphaForTeamForDefense(self, team, defenseKey):
		return self.competitionProportionForDefense(defenseKey) + self.teamProportionForDefense(defenseKey)

	def betaForTeamForDefense(self, team, defenseKey):
		sumDefenseAlphas = map(lambda dKey: self.alphaForDefense(team, dKey), self.defenseKeys)

	def predictedCrosses(self, team, defenseCategory, defenseKey):
		dataRetrievalFunction = lambda t1: t1.calculatedData.avgSuccessfulTimesCrossedDefensesTele[defenseCategory][defenseKey]
		averageOfDefenseCrossingsAcrossCompetition = np.mean([self.getAverageForDataFunctionForTeam(t, defenseRetrievalFunction) for t in self.teamsWithCompletedMatches()])
		teamAverageDefenseCrossings = self.getAverageForDataFunctionForTeam(team, defenseRetrievalFunction)
		competitionDefenseSightings = self.numTimesCompetitionFacedDefense(defenseKey)
		teamDefenseSightings = self.numTimesTeamFacedDefense(team)
		competitionTotalNumberOfDefenseSightings = 5 * len(dmutils.getCompletedTIMDsInCompetition())
		teamTotalNumberOfDefenseSightings = 5 * len(dmutils.getCompletedTIMDsForTeam(team))
		proportionOfCompetitionDefenseSightings = competitionDefenseSightings / competitionTotalNumberOfDefenseSightings
		proportionOfTeamDefenseSightings = teamDefenseSightings / teamTotalNumberOfDefenseSightings
		theta = sum(map(lambda dKey: self.betaForTeamForDefense(team, dKey), self.defenseKeys)) # TODO: Rename theta something better
		return (averageOfDefenseCrossingsAcrossCompetition * theta + teamAverageDefenseCrossings * teamDefenseSightings) / (teamAverageDefenseCrossings + 1)
	
	def listOfSuperDataPointsForTIMD(self, timd):
		return [timd.rankTorque, timd.rankSpeed, timd.rankEvasion, timd.rankDefense, timd.rankBallControl]

	def sdOfRValuesAcrossCompetition(self):
		if len(self.comp.TIMDs) <= 0:
			return None
		allSuperDataPoints = []
		[allSuperDataPoints.extend(self.listOfSuperDataPointsForTIMD(timd)) for timd in self.comp.TIMDs if dmutils.timdIsCompleted(timd)]
		return np.std(allSuperDataPoints)

	def RScore(self, team, key):
		avgRValue = self.averageTIMDObjectOverMatches(team, key)
		avgTIMDObjectsForTeams = [self.averageTIMDObjectOverMatches(team1, key) for team1 in dmutils.teamsWithMatchesCompleted()]
		averageRValuesOverComp = np.mean(avgTIMDObjectsForTeams)
		RScore = 2 * stats.norm.pdf(avgRValue, averageRValuesOverComp, self.comp.sdRScores)
		return RScore

	def singleMatchRScore(self, timd, key):
		dtimd = utils.makeDictFromTIMD(timd)
		RValue = dtimd[key]
		averageRValuesOverComp = 0.0
		for team1 in self.comp.teams:
			averageRValuesOverComp += self.averageTIMDObjectOverMatches(team1, key)
		averageRValuesOverComp /= len(self.comp.teams)
		avgRValue = utils.makeDictFromTIMD(timd)[key]
		RScore = 2 * (avgRValue, averageRValuesOverComp, self.comp.sdRScores)
		return RScore

	def sdPredictedScoreForMatch(self, match):
		sdPredictedScoreForMatch = {'blue' : 0, 'red' : 0}
		totalSDNumShots = 0
		blueTeams = []
		for teamNumber in match.blueAllianceTeamNumbers:
			blueTeams.append(dmutils.getTeamForNumber(teamNumber))
			predictedScoreForMatch['blue'] += self.totalSDShotPointsForTeam(team)
		
		redTeams = []
		for teamNumber in match.redAllianceTeamNumbers:
			redTeams.append(dmutils.getTeamForNumber(teamNumber)) 

		predictedScoreForMatch['blue'] -= self.blockedShotPointsForAllianceSD(blueTeams, redTeams)
		predictedScoreForMatch['blue'] += self.reachPointsForAlliance(blueTeams)
		crossPointsForAlliance = 0
		for team in blueTeams:
			for defenseCategory in team.calculatedData.avgSuccessfulTimesCrossedDefensesTele:
				crossPointsForAlliance += min(sum(team.calculatedData.avgSuccessfulTimesCrossedDefensesTele[defenseCategory].values()), 2)
				crossPointsForAlliance += min(sum(team.calculatedData.avgSuccessfulTimesCrossedDefensesAuto[defenseCategory].values()), 2)
		predictedScoreForMatch['blue'] += crossPointsForAlliance

	def drivingAbility(self, team, match):
		timd = dmutils.getTIMDForTeamNumberAndMatchNumber(team, match)
		return (1 * timd.rankTorque) + (1 * timd.rankBallControl) + (1 * timd.rankEvasion) + (1 * timd.rankDefense) + (1 * timd.rankSpeed)

	def getDefensePairingsForCategory(self, category):
		return [(category, defenseKey) for defenseKey in defenseDictionary[category]]

	def getDefensePairings(self):
		defensePairings = []
		map(defensePairings.extend, map(self.getDefensePairingsForCategory, self.categories))
		return defensePairings

	def predictedCrossingsForDefenseCategory(self, team, category):
		return np.mean(map(lambda dKey: predictedCrosses(team, category, dKey), self.defenseDictionary[category]))

	def predictedTeleDefenseCrossingsForTeam(self, team):
		return sum(map(lambda category: self.pointsForDefenseCategory(team, category), self.categories))

	def predictedTeleDefensePointsForAllianceForCategory(self, alliance, category):
		predictedCrossingsRetrievalFunction = lambda t: self.predictedCrossingsForDefenseCategory(t, category)
		unlimitedCrossingsForAllianceForCategory = sum(map(predictedCrossingsRetrievalFunction, alliance))
		return min(unlimitedCrossingsForAllianceForCategory, 2)

	def predictedScoreForAlliance(self, alliance):
		allianceTeleopShotPoints = sum(map(lambda t: t.teleopShotAbility, alliance)) # TODO: What do we do if there is a team on the alliance that is None?
		allianceSiegePoints = sum(map(lambda t: t.siegeAbility, alliance))
		allianceAutoPoints = sum(map(lambda t: t.autoAbility, alliance))
		alliancePredictedCrossingsRetrievalFunction = lambda c: self.predictedTeleDefensePointsForAllianceForCategory(alliance, c)
		allianceDefensePointsTele = sum(map(alliancePredictedCrossingsRetrievalFunction, self.categories))


	def numRankingAutoPoints(self, team):
		a = []
		for match in dmutils.getCompletedMatchesForTeam(team):
			a.extend(map(numAutoPointsForTIMD(timd), dmutils.matchTIMDsForTeamAlliance(team, match)))
		return sum(a)
		
	def numRankingSiegePoints(self, team):
		a = []
		for match in dmutils.getCompletedMatchesForTeam(team):
			a.extend(map(numSiegePointsForTIMD(timd), dmutils.matchTIMDsForTeamAlliance(team, match)))
		return sum(a)

	def predictedScoreCustomAlliance(self, alliance):
		predictedScoreCustomAlliance = 0		
		for team in alliance:
			totalAvgShotPoints = self.totalAvgNumShotPointsForTeam(team)
			if totalAvgShotPoints != None:
				predictedScoreCustomAlliance += self.totalAvgNumShotPointsForTeam(team)
		predictedScoreCustomAlliance += self.reachPointsForAlliance(alliance)
		productOfScaleAndChallengePercentages = 1

		standardDevCategories = []
		crossPoints = 0
		sdSum = self.sumOfStandardDeviationsOfShotsForAlliance(alliance)
		if sdSum == str(self.ourTeamNum) + " has insufficient data":
			return None
		for category in alliance[0].calculatedData.avgSuccessfulTimesCrossedDefensesTele:
			crossPoints += min(self.totalAvgDefenseCategoryCrossingsForAlliance(alliance, category) / len(category), 2)
		predictedScoreCustomAlliance += 5 * crossPoints
		for team in alliance:
			if self.siegeConsistency(team) != None:
				productOfScaleAndChallengePercentages *= self.siegeConsistency(team)
		predictedScoreCustomAlliance += 25 * self.probabilityDensity(8.0, self.totalAvgNumShotsForAlliance(alliance), sdSum) * productOfScaleAndChallengePercentages
		breachPercentage = 1

		for defenseCategory in alliance[0].calculatedData.avgSuccessfulTimesCrossedDefensesAuto:
			standardDevCategories.append(self.stanDevSumForDefenseCategory(alliance, defenseCategory))
		standardDevCategories = sorted(standardDevCategories)

		for category in range(1, len(standardDevCategories) + 1):
			category = self.categories[category - 1]
			if self.probabilityDensity(2.0, self.totalAvgDefenseCategoryCrossingsForAlliance(alliance, category), self.stanDevSumForDefenseCategory(alliance, category)) != None:
				breachPercentage *= self.probabilityDensity(2.0, self.totalAvgDefenseCategoryCrossingsForAlliance(alliance, category), self.stanDevSumForDefenseCategory(alliance, category))


		predictedScoreCustomAlliance += 20 * breachPercentage

		return predictedScoreCustomAlliance

	def predictedTIMDScoreCustomAlliance(self, alliance, teamWithMatchesToExclude, timd):
			predictedScoreCustomAlliance = 0		
			otherTeams = []
			for team in alliance:
				if(team.number == teamWithMatchesToExclude.number):
					predictedScoreCustomAlliance += timd.numHighShotsMadeTele + 10 * timd.numHighShotsMadeAuto + 5 * timd.numLowShotsMadeTele + 2 * timd.numLowShotsMadeAuto #woot
				else:
					totalAvgShotPoints = self.totalAvgNumShotPointsForTeam(team)
					if totalAvgShotPoints != None:
						otherTeams.append(team)
						predictedScoreCustomAlliance += self.totalAvgNumShotPointsForTeam(team)
			for team in otherTeams:
				predictedScoreCustomAlliance += team.calculatedData.reachPercentage * 2
			predictedScoreCustomAlliance += (2 * self.bToI(timd.didReachAuto)) 
			
			productOfScaleAndChallengePercentages = 1

			standardDevCategories = []
			crossPoints = 0
			sdSum = self.sumOfStandardDeviationsOfShotsForAllianceWithExclusion(alliance, teamWithMatchesToExclude, timd) 
			if sdSum == str(self.ourTeamNum) + " has insufficient data":
				return None
			for category in alliance[0].calculatedData.avgSuccessfulTimesCrossedDefensesTele:
				crossPoints += min(self.totalAvgDefenseCategoryCrossingsForAllianceWithExclusion(alliance, teamWithMatchesToExclude, timd, category) / len(category), 2) 
			predictedScoreCustomAlliance += 5 * crossPoints
			for team in alliance:
				if team.number == teamWithMatchesToExclude.number:
					productOfScaleAndChallengePercentages *= self.bToI(timd.didScaleTele or timd.didChallengeTele)
				else:
					productOfScaleAndChallengePercentages *= self.siegeConsistency(team)
			predictedScoreCustomAlliance += 25 * self.probabilityDensity(8.0, self.totalAvgNumShotsForAllianceWithExclusion(alliance, teamWithMatchesToExclude, timd), sdSum) * productOfScaleAndChallengePercentages 
			breachPercentage = 1

			for defenseCategory in alliance[0].calculatedData.avgSuccessfulTimesCrossedDefensesAuto:
				standardDevCategories.append(self.stanDevSumForDefenseCategoryWithExclusion(alliance, teamWithMatchesToExclude, timd, defenseCategory)) #Make Secondary Version
			standardDevCategories = sorted(standardDevCategories)

			for category in range(1, len(standardDevCategories) + 1):
				category = self.categories[category - 1]
				breachPercentage *= self.probabilityDensity(2.0, totalAvgDefenseCategoryCrossingsForAllianceWithExclusion(alliance, teamWithMatchesToExclude, timd, category), self.stanDevSumForDefenseCategoryWithExclusion(alliance, teamWithMatchesToExclude, timd, defenseCategory)) #Make Secondary Version


			predictedScoreCustomAlliance += 20 * breachPercentage

			return predictedScoreCustomAlliance

	
	def citrusDPR(self, team):	#I had fun writing this. Thanks Colin :'(
		teamsInValidMatches = []
		for match in dmutils.matchesThatHaveBeenPlayed():
			for team in dmutils.teamsInMatch(match):
				if not team in teamsInValidMatches: teamsInValidMatches.append(team)
		numTeamsInValidMatches = len(teamsInValidMatches)
		matrixOfMatches = np.zeros((numTeamsInValidMatches, numTeamsInValidMatches))
		for team1 in teamsInValidMatches:	#Create an array where the values correspond to how many matches two teams played together in the same alliance
			for team2 in teamsInValidMatches:
				occurrence = len([match for match in dmutils.matchesThatHaveBeenPlayed() if dmutils.teamsAreOnSameAllianceInMatch(team1, team2, match)])
				matrixOfMatches[teamsInValidMatches.index(team1), teamsInValidMatches.index(team2)] = occurrence
		
		inverseMatrixOfMatchOccurrences = np.linalg.inv(matrixOfMatches)	
		teamDeltas = []
		for team1 in teamsInValidMatches:
			oppositionPredictedScore = 0
			oppositionActualScore = 0
			for match in dmutils.getCompletedMatchesForTeam(team):
				if team1.number in match.blueAllianceTeamNumbers:
					oppositionPredictedScore += match.calculatedData.predictedRedScore  
					oppositionActualScore += match.redScore
				elif team1.number in match.redAllianceTeamNumbers:
					oppositionPredictedScore += match.calculatedData.predictedBlueScore
					oppositionActualScore += match.blueScore
			teamDelta = oppositionPredictedScore - oppositionActualScore
			teamDeltas.append([teamDelta])	#Calculate delta of each team (delta(team) = sum of predicted scores - sum of actual scores)
		teamDeltasMatrix = np.matrix(teamDeltas) 
		citrusDPRMatrix = np.dot(inverseMatrixOfMatchOccurrences, teamDeltas)
		print "FINISHED CITRUS DPR"
		return citrusDPRMatrix

	def citrusDPRForTIMD(self, timd):
		ATeam = dmutils.getTeamForNumber(timd.teamNumber)
		teamsWithMatchesPlayed = []
		for team in self.comp.teams:
			if len(dmutils.getCompletedTIMDsForTeam(team)) > 0:
				teamsWithMatchesPlayed.append(team)
		matrixOfMatches = np.zeros((len(teamsWithMatchesPlayed), len(teamsWithMatchesPlayed)))
		for team1 in teamsWithMatchesPlayed:	#Create an array where the values correspond to how many matches two teams played together in the same alliance
			for team2 in teamsWithMatchesPlayed:
				occurrence = 0
				for match in self.comp.matches:
					if (team1.number in match.blueAllianceTeamNumbers and team2.number in match.blueAllianceTeamNumbers) or (team1.number in match.redAllianceTeamNumbers and team2.number in match.redAllianceTeamNumbers):
						occurrence += 1
				matrixOfMatches[teamsWithMatchesPlayed.index(team1), teamsWithMatchesPlayed.index(team2)] = occurrence
		
		inverseMatrixOfMatchOccurrences = np.linalg.inv(matrixOfMatches)	
		teamDeltas = np.array([])
		oppositionPredictedScore = 0
		oppositionActualScore = 0
		for team1 in teamsWithMatchesPlayed:
			oppositionPredictedScore = 0
			oppositionActualScore = 0
			for match in self.getPlayedMatchesForTeam(ATeam):
				if team1.number in match.blueAllianceTeamNumbers:
					oppositionPredictedScore += match.calculatedData.predictedRedScore  
					oppositionActualScore += match.redScore
				elif team1.number in match.redAllianceTeamNumbers:
					oppositionPredictedScore += match.calculatedData.predictedBlueScore
					oppositionActualScore += match.blueScore
			teamDelta = oppositionPredictedScore - oppositionActualScore
			teamDeltas = np.append(teamDeltas, teamDelta)	#Calculate delta of each team (delta(team) = sum of predicted scores - sum of actual scores)
		teamDeltas.shape = (len(teamsWithMatchesPlayed), 1)	 
		citrusDPRMatrix = np.dot(inverseMatrixOfMatchOccurrences, teamDeltas)

		return citrusDPRMatrix

	def firstPickAbility(self, team):
		ourTeam = dmutils.getTeamForNumber(self.ourTeamNum)
		alliance = [ourTeam, team]
		predictedScoreCustomAlliance = self.predictedScoreCustomAlliance(alliance) 
		if math.isnan(predictedScoreCustomAlliance):
			return None
		return self.predictedScoreCustomAlliance(alliance) 

	def teamInMatchFirstPickAbility(self, team, match):
		ourTeam = dmutils.getTeamForNumber(self.ourTeamNum)
		alliance = [ourTeam, team]
		predictedScoreCustomAlliance = self.predictedScoreCustomAlliance(alliance) 
		if math.isnan(predictedScoreCustomAlliance):
			return None
		return self.predictedScoreCustomAlliance(alliance) 

	def secondPickAbility(self, team):
		gamma = 0.5
		teamsArray = [loopTeam for loopTeam in self.comp.teams if dmutils.getCompletedTIMDsForTeam(loopTeam) > 0] 
		secondPickAbility = {}
		ourTeam = dmutils.getTeamForNumber(self.ourTeamNum)
		citrusDPRMatrix = self.citrusDPR(team)
		for team1 in teamsArray:
			if team1.number != self.ourTeamNum and team1.number != team.number:	#Loop through all of the teams and find the score contribution of the team whose
				citrusDPR = citrusDPRMatrix[teamsArray.index(team1) - 1]
				alliance3Robots = [ourTeam, team, team1]				
				alliance2Robots = [ourTeam, team1]
				scoreContribution = self.predictedScoreCustomAlliance(alliance3Robots) - self.predictedScoreCustomAlliance(alliance2Robots)
				secondPickAbility[team1.number] = gamma * scoreContribution * (1 - gamma) * int(citrusDPR)		#gamma is a constant
		for key, spa in secondPickAbility.items():
			if math.isnan(spa): secondPickAbility[key] = None
		return secondPickAbility

	def secondPickAbilityWithExclusion(self, team, timd):
		gamma = 0.5
		teamsArray = []
		for team1 in self.comp.teams:
			if len(dmutils.getCompletedTIMDsForTeam(team)) > 0:
				teamsArray.append(team1)
		secondPickAbility = {}
		ourTeam = dmutils.getTeamForNumber(self.ourTeamNum)
		citrusDPRMatrix = self.citrusDPR(team)
		for team1 in teamsArray:
			if team1.number != self.ourTeamNum and team1.number != team.number:	#Loop through all of the teams and find the score contribution of the team whose
				citrusDPR = citrusDPRMatrix[teamsArray.index(team1) - 1]
				alliance3Robots = [ourTeam, team, team1]				
				alliance2Robots = [ourTeam, team1]
				scoreContribution = self.predictedTIMDScoreCustomAlliance(alliance3Robots, team, timd) - self.predictedTIMDScoreCustomAlliance(alliance2Robots, team, timd)
				secondPickAbility[team1.number] = gamma * scoreContribution * (1 - gamma) * int(citrusDPR)		#gamma is a constant
		for key, spa in secondPickAbility.items():
			if math.isnan(spa): secondPickAbility[key] = -2
		return secondPickAbility

	def overallSecondPickAbility(self, team):
		firstPickAbilityArray = []
		first16 = []
		overallSecondPickAbility = 0.0
		for teamNumber in team.calculatedData.secondPickAbility:
			team1 = dmutils.getTeamForNumber(teamNumber)
			if teamNumber != self.ourTeamNum:
				firstPickAbilityArray.append(team1)
		firstPickAbilityArray = sorted(firstPickAbilityArray, key = lambda team: team.calculatedData.firstPickAbility, reverse=True) #Sort teams by firstPickAbility
		if len(firstPickAbilityArray) == len(team.calculatedData.secondPickAbility) and len(firstPickAbilityArray) >= 16:
			for t in range(0,15):
				first16.append(firstPickAbilityArray[t])
			for t in first16:
				if team.calculatedData.secondPickAbility[t.number] != None:
					overallSecondPickAbility += team.calculatedData.secondPickAbility[t.number]
		return overallSecondPickAbility / 16

	def overallSecondPickAbilityWithExclusion(self, team, timd):
		firstPickAbilityArray = []
		first16 = []
		overallSecondPickAbility = 0.0
		for teamNumber in timd.calculatedData.secondPickAbility:
			team1 = dmutils.getTeamForNumber(teamNumber)
			if teamNumber != self.ourTeamNum:
				firstPickAbilityArray.append(team1)
		firstPickAbilityArray = sorted(firstPickAbilityArray, key = lambda team: timd.calculatedData.firstPickAbility, reverse=True) #Sort teams by firstPickAbility
		if len(firstPickAbilityArray) == len(timd.calculatedData.secondPickAbility) and len(firstPickAbilityArray) >= 16:
			for t in range(0,15):
				first16.append(firstPickAbilityArray[t])
			for t in first16:
				overallSecondPickAbility += timd.calculatedData.secondPickAbility[t.number]
		return overallSecondPickAbility / 16


	#Matches Metrics
	def predictedScoreForMatch(self, match):
		return {'red' : {'score' : 0.0, 'RP' : 0.0}, 'blue' :{'score' : 0.0, 'RP': 0.0}}
	# 	predictedScoreForMatch = {'blue': {'score' : 0.0, 'RP' : 0.0}, 'red': {'score' : 0.0, 'RP' : 0.0}}

	# 	# Blue Alliance First
	# 	totalAvgNumShots = 0
	# 	blueTeams = []
	# 	for teamNumber in match.blueAllianceTeamNumbers:
	# 		team = dmutils.getTeamForNumber(teamNumber)
	# 		blueTeams.append(team)
	# 		if self.totalAvgNumShotPointsForTeam(team) != None:
	# 			predictedScoreForMatch['blue']['score'] += self.totalAvgNumShotPointsForTeam(team)

	# 	redTeams = []
	# 	for teamNumber in match.redAllianceTeamNumbers:
	# 		redTeams.append(dmutils.getTeamForNumber(teamNumber))
	# 	predictedScoreForMatch['blue']['score'] -=  5 * (self.blockedShotPointsForAlliance(blueTeams, redTeams)) - ((self.blockedShotPointsForAlliance(blueTeams, redTeams) + self.blockedShotPointsForAlliance(redTeams, blueTeams)) / 2)
	# 	if self.reachPointsForAlliance(blueTeams) != None:
	# 		predictedScoreForMatch['blue']['score'] += self.reachPointsForAlliance(blueTeams)
		
	# 	for defCategory in blueTeams[0].calculatedData.avgSuccessfulTimesCrossedDefensesTele.values():
	# 		crossesForCategory = 0.0
	# 		for defense in defCategory:
	# 			for team in blueTeams:
	# 				crossesForCategory += self.predictedCrosses(team, defense)
	# 		if len(defCategory) != 0:
	# 			predictedScoreForMatch['blue']['score'] += 5 * min(crossesForCategory / len(defCategory), 2)
	# 		else: 
	# 			predictedScoreForMatch['blue']['score'] += 5 * min(crossesForCategory, 2)

	# 	productOfScaleAndChallengePercentages = 1

	# 	standardDevCategories = []
	# 	for team in blueTeams:
	# 		if self.siegeConsistency(team) != None:
	# 			productOfScaleAndChallengePercentages *= self.siegeConsistency(team)
	# 	captureRPs = self.probabilityDensity(8.0, self.totalAvgNumShotsForAlliance(blueTeams), self.sumOfStandardDeviationsOfShotsForAlliance(blueTeams)) * productOfScaleAndChallengePercentages
	# 	if not math.isnan(captureRPs):
	# 		predictedScoreForMatch['blue']['RP'] += captureRPs
		
	# 	breachRPs = 1.0
	# 	for defenseCategory in self.categories:
	# 		standardDevCategories.append(self.stanDevSumForDefenseCategory(blueTeams, defenseCategory))
	# 	standardDevCategories = sorted(standardDevCategories)	#Sort the array of standard deviations for defense categories

	# 	for category in range(1, len(standardDevCategories) + 1):	#Sort and calculate breach chance using max 4 categories
	# 		category = self.categories[category - 1]
	# 		if self.totalAvgDefenseCategoryCrossingsForAlliance(blueTeams, category) != None and self.stanDevSumForDefenseCategory(blueTeams, category) != None:
	# 			breachRPs *= self.probabilityDensity(2.0, self.totalAvgDefenseCategoryCrossingsForAlliance(blueTeams, category), self.stanDevSumForDefenseCategory(blueTeams, category))
	# 	if not math.isnan(breachRPs):
	# 		predictedScoreForMatch['blue']['RP'] += breachRPs			

	# 	#Red Alliance Next
	# 	totalAvgNumShots = 0
	# 	redTeams = []
	# 	for teamNumber in match.redAllianceTeamNumbers:
	# 		team = dmutils.getTeamForNumber(teamNumber)
	# 		redTeams.append(team)
	# 		if self.totalAvgNumShotPointsForTeam(team) != None:
	# 			predictedScoreForMatch['red']['score'] += self.totalAvgNumShotPointsForTeam(team)

	# 	redTeams = []
	# 	for teamNumber in match.redAllianceTeamNumbers:
	# 		redTeams.append(dmutils.getTeamForNumber(teamNumber))
	# 	predictedScoreForMatch['red']['score'] -=  5 * (self.blockedShotPointsForAlliance(redTeams, blueTeams)) - ((self.blockedShotPointsForAlliance(redTeams, blueTeams) + self.blockedShotPointsForAlliance(blueTeams, redTeams)) / 2)
	# 	if self.reachPointsForAlliance(redTeams) != None:
	# 		predictedScoreForMatch['red']['score'] += self.reachPointsForAlliance(redTeams)
		
	# 	for defCategory in blueTeams[0].calculatedData.avgSuccessfulTimesCrossedDefensesTele.values():
	# 		crossesForCategory = 0.0
	# 		for defense in defCategory:
	# 			for team in blueTeams:
	# 				crossesForCategory += self.predictedCrosses(team, defense)
	# 		if len(defCategory) != 0:
	# 			predictedScoreForMatch['red']['score'] += 5 * min(crossesForCategory / len(defCategory), 2)
	# 		else:
	# 			predictedScoreForMatch['red']['score'] += 5 * min(crossesForCategory, 2)
					
	# 	productOfScaleAndChallengePercentages = 1

	# 	standardDevCategories = []
	# 	for team in redTeams:
	# 		if self.siegeConsistency(team) != None:
	# 			productOfScaleAndChallengePercentages *= self.siegeConsistency(team)
	# 	captureRPs = self.probabilityDensity(8.0, self.totalAvgNumShotsForAlliance(redTeams), self.sumOfStandardDeviationsOfShotsForAlliance(redTeams)) * productOfScaleAndChallengePercentages
	# 	if not math.isnan(captureRPs):
	# 		predictedScoreForMatch['red']['RP'] += captureRPs
	# 	breachRPs = 1.0
	# 	# print "MATCHNUM: " + str(match.number)
	# 	for defenseCategory in self.categories:
	# 		standardDevCategories.append(self.stanDevSumForDefenseCategory(redTeams, defenseCategory))
	# 	standardDevCategories = sorted(standardDevCategories)	#Sort the array of standard deviations for defense categories

	# 	for category in range(1, len(standardDevCategories) + 1):	#Sort and calculate breach chance using max 4 categories
	# 		category = self.categories[category - 1]
	# 		if self.totalAvgDefenseCategoryCrossingsForAlliance(redTeams, category) != None and self.stanDevSumForDefenseCategory(redTeams, category) != None:
	# 			breachRPs *= self.probabilityDensity(2.0, self.totalAvgDefenseCategoryCrossingsForAlliance(redTeams, category), self.stanDevSumForDefenseCategory(redTeams, category))

	# 	if not math.isnan(breachRPs):
	# 		predictedScoreForMatch['red']['RP'] += breachRPs	

	# 	return predictedScoreForMatch
		
	def breachPercentage(self, team):
		breachPercentage = 0
		for match in self.team.matches:
			if team.number in match.blueAllianceTeamNumbers and match.blueScore != None:
				if match.blueAllianceDidBreach == True:
					breachPercentage += 1
			elif team.number in match.redAllianceTeamNumbers and match.blueScore != None:
				if match.redAllianceDidBreach == True:
					breachPercentage += 1
		return breachPercentage/len(self.team.matches)


	def numDefensesCrossedInMatch(self, match):
		numDefensesCrossedInMatch = {'red': None, 'blue': None}
		blueAllianceCrosses = 0
		for teamNum in match.blueAllianceTeamNumbers:
			timd = dmutils.getTIMDForTeamNumberAndMatchNumber(teamNum, match.number)
			for defense in timd.timesSuccessfulCrossedDefensesTele.values():
				blueAllianceCrosses += len(defense) - 1
			for defense in timd.timesSuccessfulCrossedDefensesAuto.values():
				blueAllianceCrosses += len(defense) - 1
		numDefensesCrossedInMatch['blue'] = blueAllianceCrosses
		redAllianceCrosses = 0
		for teamNum in match.redAllianceTeamNumbers:
			timd = dmutils.getTIMDForTeamNumberAndMatchNumber(teamNum, match.number)
			for defense in timd.timesSuccessfulCrossedDefensesTele.values():
				redAllianceCrosses += len(defense) - 1
			for defense in timd.timesSuccessfulCrossedDefensesAuto.values():
				redAllianceCrosses += len(defense) - 1
		numDefensesCrossedInMatch['red'] = redAllianceCrosses

		return numDefensesCrossedInMatch


	def predictedNumberOfRPs(self, team):
		totalRPForTeam = 0
		overallChallengeAndScalePercentage = 0
		overallBreachPercentage = 0
		matchesToBePlayedCounter = 0

		for match in self.comp.matches:		
			if team.number in match.redAllianceTeamNumbers and match.redScore == None:	#Only award predictedRPs if the match has not been played
				matchesToBePlayedCounter += 1
				for teamNumber in match.blueAllianceTeamNumbers:
					team = dmutils.getTeamForNumber(teamNumber)
					overallChallengeAndScalePercentage += self.siegeConsistency(team)
					overallBreachPercentage += team.calculatedData.breachPercentage

				if self.predictedScoreForMatch(match)['red']['score'] > self.predictedScoreForMatch(match)['blue']['score']:
					totalRPForTeam += 2
				elif self.predictedScoreForMatch(match)['red']['score'] == self.predictedScoreForMatch(match)['blue']['score']:
					totalRPForTeam += 1

			elif team.number in match.blueAllianceTeamNumbers and match.blueScore == None:
				matchesToBePlayedCounter += 1
				for teamNumber in match.blueAllianceTeamNumbers:
					team = dmutils.getTeamForNumber(teamNumber)
					overallChallengeAndScalePercentage += team.calculatedData.challengePercentage + team.calculatedData.scalePercentage
					overallBreachPercentage += team.calculatedData.breachPercentage

				if self.predictedScoreForMatch(match)['blue']['score'] > self.predictedScoreForMatch(match)['red']['score']:
					totalRPForTeam += 2
				elif self.predictedScoreForMatch(match)['red']['score'] == self.predictedScoreForMatch(match)['blue']['score']:
					totalRPForTeam += 1

			else:
				print 'This team does not exist or all matches have been played'

		totalRPForTeam += (overallChallengeAndScalePercentage / 3)
		totalRPForTeam += (overallBreachPercentage / 3)

		return totalRPForTeam + self.numRPsForTeam(team)
	
	def scoreContribution(self, timd):
		individualScore = 0
		individualScore += timd.numHighShotsMadeTele + timd.numHighShotsMadeAuto + timd.numLowShotsMadeAuto + timd.numLowShotsMadeTele
		defenseCrossesAuto = self.flattenDictionary(timd.timesSuccessfulCrossedDefensesAuto)
		defenseCrossesTele = self.flattenDictionary(timd.timesSuccessfulCrossedDefensesTele)
		for crosses in defenseCrossesAuto.values():
			if len(crosses) - 1 >= 1:
				individualScore += 10
				break
		for crosses in defenseCrossesTele.values():
			individualScore += 5 * min(len(crosses) - 1, 2)
		if timd.didChallengeTele: individualScore += 5
		if timd.didScaleTele: individualScore += 15
		return individualScore

	def RPsGainedFromMatch(self, match):
		blueRPs = 0
		redRPs = 0
		if match.blueScore > match.redScore: blueRPs += 2
		elif match.redScore > match.blueScore: redRPs += 2
		else:
			blueRPs += 1
			redRPs += 1

		if match.blueAllianceDidBreach: blueRPs += 1
		if match.redAllianceDidBreach: redRPs += 1

		if match.blueAllianceDidCapture: blueRPs += 1
		if match.redAllianceDidCapture: redRPs += 1

		return {'blue': blueRPs, 'red': redRPs}

	#Competition wide Metrics
	def avgCompScore(self):
		a = [(match.redScore + match.blueScore) for match in self.comp.matches if (match.blueScore != None and match.redScore != None)]
		return sum(a) / len(self.comp.matches)

	def numPlayedMatchesInCompetition(self):
		return len([match for match in self.comp.matches if dmutils.matchIsPlayed(match)])

	def actualSeeding(self):
		return sorted(self.comp.teams, key=lambda t: (self.numRPsForTeam(t), self.numRankingAutoPoints(t), self.numRankingSiegePoints(t)), reverse=True)

	def getRankingForTeam(self, team):
		return self.actualSeeding().index(team)

	def predictedSeeding(self):
		return sorted(self.comp.teams, key=attrgetter('calculatedData.predictedNumRPs', 'calculatedData.autoAbility', 'calculatedData.siegeAbility'))

	def doCalculations(self, FBC):
		# self.comp.sdRScores = self.sdOfRValuesAcrossCompetition()
		for team in self.comp.teams:
			timds = dmutils.getCompletedTIMDsForTeam(team)

			# print("Calculating TIMDs for team " + str(team.number)) + "... "
			# for timd in timds:
			# 	c = timd.calculatedData # Think about this later. What if the calculated data is None?
			# 	c.highShotAccuracyTele = self.getTIMDHighShotAccuracyTele(timd) # Checked
			# 	c.highShotAccuracyAuto = self.getTIMDHighShotAccuracyAuto(timd) # Checked
			# 	c.lowShotAccuracyTele = self.getTIMDLowShotAccuracyTele(timd) # Checked
			# 	c.lowShotAccuracyAuto = self.getTIMDLowShotAccuracyAuto(timd) # Checked
			# 	c.siegeAbility = self.singleSiegeAbility(timd)
			# 	c.numRPs = self.RPsGainedFromMatch(dmutils.getMatchForNumber(timd.matchNumber))
			# 	c.numAutoPoints = self.numAutoPointsForTIMD(timd)
			# 	c.numScaleAndChallengePoints = c.siegeAbility #they are the same
			# 	c.scoreContribution = self.scoreContribution(timd)
			# 	c.RScoreSpeed = self.singleMatchRScore(timd, 'rankSpeed')
			# 	c.RScoreEvasion = self.singleMatchRScore(timd, 'rankEvasion')
			# 	c.RScoreDefense = self.singleMatchRScore(timd, 'rankDefense')
			# 	c.RScoreTorque = self.singleMatchRScore(timd, 'rankTorque')
			# 	c.RScoreBallControl = self.singleMatchRScore(timd, 'rankBallControl')
			# 	c.RScoreDrivingAbility = 1 * c.RScoreSpeed + 1 * c.RScoreEvasion + 1 * c.RScoreDefense + 1 * c.RScoreTorque + 1 * c.RScoreBallControl
			# 	c.firstPickAbility = self.teamInMatchFirstPickAbility(team, dmutils.getMatchForNumber(timd.matchNumber))
			# 	c.secondPickAbility = self.secondPickAbilityWithExclusion(team, timd)
			# 	c.overallSecondPickAbility = self.overallSecondPickAbilityWithExclusion(team, timd)
			# 	c.numBallsIntakedOffMidlineAuto = len(utils.makeDictFromTIMD(timd)['ballsIntakedAuto'])

			t = team.calculatedData
			if len(timds) <= 0:
				print "No Complete TIMDs for team " + str(team.number) + ", " + team.name
			else:
				print("Beginning calculations for team: " + str(team.number) + ", " + team.name)
				#Super Scout Averages

				t.avgTorque = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankTorque) # Checked
				t.avgSpeed = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankSpeed)  # Checked
				t.avgEvasion = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankEvasion)  # Checked
				t.avgDefense = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankDefense)  # Checked
				t.avgBallControl = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankBallControl)  # Checked
				t.RScoreTorque = self.RScore(team, 'rankTorque') # Checked
				t.RScoreSpeed = self.RScore(team, 'rankSpeed') # Checked
				t.RScoreEvasion = self.RScore(team, 'rankEvasion') # Checked
				t.RScoreDefense = self.RScore(team, 'rankDefense') # Checked
				t.RScoreBallControl = self.RScore(team, 'rankBallControl') # Checked
				# t.disabledPercentage = self.getPercentageForDataPointForTeam(team, 'didGetDisabled')
				# t.incapacitatedPercentage = self.getPercentageForDataPointForTeam(team, 'didGetIncapacitated')
				# t.disfunctionalPercentage = t.disabledPercentage + t.incapacitatedPercentage 

				#Auto
				t.autoAbility = self.autoAbility(team)
				t.avgHighShotsAuto = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numHighShotsMadeAuto) #Checked
				t.avgLowShotsAuto = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numLowShotsMadeAuto) #Checked	
				# t.reachPercentage = self.getPercentageForDataPointForTeam(team, 'timd.didReachAuto')
				t.highShotAccuracyAuto = self.getAverageForDataFunctionForTeam(team, self.getTIMDHighShotAccuracyAuto) # Checked
				t.lowShotAccuracyAuto = self.getAverageForDataFunctionForTeam(team, self.getTIMDLowShotAccuracyAuto) # Checked
				t.numAutoPoints = self.getAverageForDataFunctionForTeam(team, self.numAutoPointsForTIMD) # Checked
				# t.avgMidlineBallsIntakedAuto = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.ballsIntakedAuto)
				t.sdHighShotsAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numHighShotsMadeAuto) # Checked
				t.sdLowShotsAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numLowShotsMadeAuto) # Checked
				# t.sdMidlineBallsIntakedAuto = self.getStandardDeviationForDataFunctionForTeam(team, 'ballsIntakedAuto')
				t.sdBallsKnockedOffMidlineAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numBallsKnockedOffMidlineAuto) # Checked
				t.avgSuccessfulTimesCrossedDefensesAuto = self.averageDictionaries(self.makeArrayOfDictionaries(team, 'timesSuccessfulCrossedDefensesAuto'))
			
				# #Tele
				# t.challengePercentage = self.getPercentageForDataPointForTeam(team, 'timd.didChallengeTele')
				# t.scalePercentage = self.getPercentageForDataPointForTeam(team, 'timd.didScaleTele')
				t.avgGroundIntakes = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numGroundIntakesTele) # Checked
				t.avgBallsKnockedOffMidlineAuto = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numBallsKnockedOffMidlineAuto) # Checked
				t.avgShotsBlocked = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numShotsBlockedTele) # Checked
				t.avgHighShotsTele = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numHighShotsMadeTele) # Checked
				t.avgLowShotsTele = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numLowShotsMadeTele) # Checked
				t.highShotAccuracyTele = self.getAverageForDataFunctionForTeam(team, self.getTIMDHighShotAccuracyTele) # Checked
				t.lowShotAccuracyTele = self.getAverageForDataFunctionForTeam(team, self.getTIMDLowShotAccuracyTele) # Checked
				# t.blockingAbility = self.blockingAbility(team) # TODO: Move this later
				t.teleopShotAbility = self.teleopShotAbility(team) # Checked
				t.siegeConsistency = t.challengePercentage + t.scalePercentage # Checked
				t.siegeAbility = self.siegeAbility(team) # Checked
				t.avgSuccessfulTimesCrossedDefensesTele = self.averageDictionaries(self.makeArrayOfDictionaries(team, 'timesSuccessfulCrossedDefensesTele'))
				t.sdHighShotsTele = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numHighShotsMadeTele) # Checked
				t.sdLowShotsTele = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numLowShotsMadeTele) # Checked
				t.sdGroundIntakes = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numGroundIntakesTele) # Checked
				t.sdShotsBlocked = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numShotsBlockedTele) # Checked
				t.numRPs = self.numRPsForTeam(team)
				t.numScaleAndChallengePoints = self.numScaleAndChallengePointsForTeam(team) # Checked
				t.firstPickAbility = self.firstPickAbility(team)	
				t.secondPickAbility = self.secondPickAbility(team)
				t.overallSecondPickAbility = self.overallSecondPickAbility(team)
				t.predictedSeed = self.getRankingForTeam(team)
				
			
				FBC.addCalculatedTeamDataToFirebase(team.number, t)
				print("Putting calculations for team " + str(team.number) + " to Firebase.")
				
		#Match Metrics
		for match in self.comp.matches:
			# if match.blueScore > None and match.redScore > None:
			if dmutils.matchIsPlayed:
				print "Beginning calculations for match " + str(match.number) + "..."
				match.calculatedData.predictedBlueScore = self.predictedScoreForMatch(match)['blue']['score']
				match.calculatedData.predictedRedScore = self.predictedScoreForMatch(match)['red']['score']
				match.calculatedData.predictedBlueRPs = self.predictedScoreForMatch(match)['blue']['RP']
				match.calculatedData.predictedRedRPs = self.predictedScoreForMatch(match)['red']['RP']
				match.calculatedData.numDefensesCrossedByBlue = self.numDefensesCrossedInMatch(match)['blue']
				match.calculatedData.numDefensesCrossedByRed = self.numDefensesCrossedInMatch(match)['red']
				match.calculatedData.actualBlueRPs = self.RPsGainedFromMatch(match)['blue']
				match.calculatedData.actualRedRPs = self.RPsGainedFromMatch(match)['red']
				FBC.addCalculatedMatchDataToFirebase(match.number, match.calculatedData)
				print("Putting calculations for match " + str(match.number) + " to Firebase.")

		#Competition metrics
		if self.numPlayedMatchesInCompetition() > 0:
			print "Doing competition calculations... "
			self.comp.averageScore = self.avgCompScore()
			self.comp.actualSeeding = self.actualSeeding()
			print "finished"
			self.comp.predictedSeeding = self.predictedSeeding()
			

