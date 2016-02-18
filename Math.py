
# Math.py
import utils
import random
import firebaseCommunicator
import math
import numpy as np
import DataModel
import scipy as sp
import scipy.stats as stats
import sys, traceback


class Calculator(object):
	"""docstring for Calculator"""
	def __init__(self, competition):
		super(Calculator, self).__init__()
		self.comp = competition
		self.categories = ['a', 'b', 'c', 'd', 'e']
		self.ourTeamNum = 1678

	# Team utility functions
	def getTeamForNumber(self, teamNumber):
		return [team for team in self.comp.teams if team.number == teamNumber][0]

	def getMatchesForTeam(self, team):
		return [match for match in self.comp.matches if self.teamInMatch(team, match)]

	def getPlayedTIMDsForTeam(self, team):
		return [timd for timd in self.getTIMDsForTeamNumber(team.number) if self.timdIsPlayed(timd)]

	# Match utility functions
	def getMatchForNumber(self, matchNumber):
		return [match for match in self.comp.matches if match.number == matchNumber][0]

	def teamsInMatch(self, match):
		teamNumbersInMatch = match.redAllianceTeamNumbers
		teamNumbersInMatch.extend(match.blueAllianceTeamNumbers)
		return [self.getTeamForNumber(teamNumber) for teamNumber in teamNumbersInMatch]

	def teamInMatch(self, team, match):
		return team in self.teamsInMatch(match)

	def matchIsPlayed(self, match):
		return match.redScore != None or match.blueScore != None

	# TIMD utility functions
	def getTIMDsForTeamNumber(self, teamNumber):
		return [timd for timd in self.comp.TIMDs if timd.teamNumber == teamNumber]

	def getCompletedTIMDsForTeamNumber(self, teamNumber):
		return filter(self.timdIsCompleted, self.getTIMDsForTeamNumber(teamNumber))

	def getCompletedTIMDsForTeam(self, team):
		return getCompletedTIMDsForTeamNumber(team.number)

	def getPlayedTIMDsForTeamNumber(self, teamNumber):
		return filter(self.timdIsPlayed, self.getTIMDsForTeamNumber(teamNumber))

	def timdIsPlayed(self, timd):
		isPlayed = False 
		for key, value in utils.makeDictFromTIMD(timd).items():
			if value != None:
				isPlayed = True
		return isPlayed

	def timdIsCompleted(self, timd):
		isCompleted = True 
		for key, value in utils.makeDictFromTIMD(timd).items():
			if value == None:
				isCompleted = False
		return isCompleted

	# Calculated Team Data
	def averageTIMDObjectOverMatches(self, team, key, coefficient = 1):
		return np.mean([utils.makeDictFromTIMD(timd)[key] for timd in self.getCompletedTIMDsForTeam(team) if timd.rankTorque != None])

	def standardDeviationObjectOverAllMatches(self, team, key, coefficient = 1):
		return np.mean([utils.makeDictFromTIMD(timd)[key] for timd in self.getCompletedTIMDsForTeam(team) if timd.rankTorque != None])

	def percentagesOverAllTIMDs(self, team, key, coefficient = 1):
		 percentage = [timd for timd in self.getCompletedTIMDsForTeam(team) if utils.makeDictFromTIMD(timd)[key] == True]
		 return len(percentage) / len(self.getCompletedTIMDsForTeam(team))

	def disfunctionalPercentage(self, team):
		percentage = [timd for timd in self.getCompletedTIMDsForTeam(team) if timd.didGetDisabled == True or didGetIncapacitated == True]
		return len(percentage) / len(self.getCompletedTIMDsForTeam(team))

	def shotAccuracy(self, team, auto, high):
		timds = self.getCompletedTIMDsForTeam(team)
		if len(timds) == 0:
			return None
		totalShotAccuracy = 0
		for timd in timds:
			a = self.singleMatchShotAccuracy(timd, auto, high)
			totalShotAccuracy += a
		return totalShotAccuracy / len(timds)

	def teamsAreOnSameAllianceInMatch(self, team1, team2, match):
		areInSameMatch = False
		alliances = [match.redAllianceTeamNumbers, match.blueAllianceTeamNumbers]
		for alliance in alliances:
			if team1.number in alliance and team2.number in alliance:
				areInSameMatch = True
		return areInSameMatch

	def teamsWithMatchesPlayed(self):
		return [team for team in self.comp.teams if len(self.getCompletedTIMDsForTeam(team)) > 0]

	def getAllTIMDsForMatch(self, match):
		return [timd for timd in self.comp.TIMDs if timd.matchNumber == match.number]

	def matchHasAllTeams(self, match):
		return len(self.getAllTIMDsForMatch(match)) == 6

	def matchesThatHaveBeenPlayed(self):
		return [match for match in self.comp.matches if self.matchHasAllTeams(match)]

	def getTIMDForTeamNumberAndMatchNumber(self, teamNumber, matchNumber):
		return [timd for timd in self.getTIMDsForTeamNumber(teamNumber) if timd.matchNumber == matchNumber][0]


		
	def singleMatchShotAccuracy(self, timd, auto, high):
		if high:
			if auto:
				if timd.numHighShotsMadeAuto > None and timd.numHighShotsMissedAuto > None and ((timd.numHighShotsMadeAuto + timd.numHighShotsMissedAuto) > 0):
					return timd.numHighShotsMadeAuto / (timd.numHighShotsMadeAuto + timd.numHighShotsMissedAuto)
				return 0
			else:
				if timd.numHighShotsMadeTele > None and timd.numHighShotsMissedTele > None and ((timd.numHighShotsMadeTele + timd.numHighShotsMissedTele) > 0):
					return timd.numHighShotsMadeTele / (timd.numHighShotsMadeTele + timd.numHighShotsMissedTele)
				return 0
		else:
			if auto:
				if timd.numLowShotsMadeAuto > None and timd.numLowShotsMissedAuto > None and ((timd.numLowShotsMadeAuto + timd.numLowShotsMissedAuto) > 0):
					return timd.numLowShotsMadeAuto / (timd.numLowShotsMadeAuto + timd.numLowShotsMissedAuto)
				return 0
			else:
				if timd.numLowShotsMadeTele > None and timd.numLowShotsMissedTele > None and ((timd.numLowShotsMadeTele + timd.numLowShotsMissedTele) > 0):
					return timd.numLowShotsMadeTele / (timd.numLowShotsMadeTele + timd.numLowShotsMissedTele)
				return 0


	def avgBallsIntaked(self, team, key):
		timds = self.getCompletedTIMDsForTeam(team)
		avgBallsIntaked = 0.0
		for timd in timds:
			if timd.ballsIntakedAuto != None:
				avgBallsIntaked += len(utils.makeDictFromTIMD(timd)[key])
		return avgBallsIntaked / len(timds)

	def flattenDictionary(self, dictionary):
		flattenedDict = {}
		for categoryDict in dictionary.values():
			for defense, dictionary in categoryDict.items():
				flattenedDict[defense] = dictionary
		return flattenedDict


	def makeArrayOfDictionaries(self, team, key): 
 		timds = self.getCompletedTIMDsForTeam(team)
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
  		timds = getCompletedTIMDsForTeam(team)
  		for timd in timds:
  			defenses = self.flattenDictionary(timd.timesSuccessfulCrossedDefensesTele)
  			avgDefenseCrosses += sum(defenses.values())
  		return avgDefenseCrosses / len(timds)

  	def averageDefenseCrossesAuto(self, team):
  		avgDefenseCrosses = 0
  		timds = getCompletedTIMDsForTeam(team)
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
 		timds = self.getCompletedTIMDsForTeam(team)
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
		avgHighShotsMissedAuto = self.averageTIMDObjectOverMatches(team, 'numHighShotsMissedAuto')
		avgLowShotsMissedAuto = self.averageTIMDObjectOverMatches(team, 'numLowShotsMissedAuto')

		if (team.calculatedData.avgHighShotsAuto != 0 or team.calculatedData.avgLowShotsAuto != 0) and (avgHighShotsMissedAuto != 0 or avgLowShotsMissedAuto != 0):
			if team.calculatedData.avgHighShotsAuto != None:
				return 10 * team.calculatedData.avgHighShotsAuto + 5 * team.calculatedData.avgLowShotsAuto + 2 * team.calculatedData.reachPercentage + 10 
		else:
			if team.calculatedData.avgHighShotsAuto != None:
				return 10 * team.calculatedData.avgHighShotsAuto + 5 * team.calculatedData.avgLowShotsAuto + 2 * team.calculatedData.reachPercentage

	def teleopShotAbility(self, team): return (5 * team.calculatedData.avgHighShotsTele + 2 * team.calculatedData.avgLowShotsTele)

	def siegeAbility(self, team): return (15 * team.calculatedData.scalePercentage + 5 * team.calculatedData.challengePercentage)

	def singleSiegeAbility(self, timd): return (15 * self.booleanToIntegerValue(timd.didScaleTele) + 5 * self.booleanToIntegerValue(timd.didChallengeTele))

	def siegeConsistency(self, team): 
		if team.calculatedData.reachPercentage != None: return (team.calculatedData.scalePercentage + team.calculatedData.challengePercentage)

	def siegePower(self, team): return (team.calculatedData.siegeConsistency * team.calculatedData.siegeAbility)


	def numAutoPointsForTIMD(self, timd):
		defenseCrossesInAuto = 0
		for defense, value in timd.timesSuccessfulCrossedDefensesAuto.items():
			defenseCrossesInAuto += len(value) - 1
		if defenseCrossesInAuto > 1: defenseCrossesInAuto = 1
		return 10 * int(timd.numHighShotsMadeAuto) + 5 * int(timd.numLowShotsMadeAuto) + 2 * (1 if timd.didReachAuto else 0) + 10 * int(defenseCrossesInAuto)

	def numAutoPointsForTeam(self, team):
		totalAutoPoints = 0
		for timd in self.getCompletedTIMDsForTeamNumber(team.number):
			totalAutoPoints += self.numAutoPointsForTIMD(timd)
		return totalAutoPoints

	def numRPsForTeam(self, team):
		totalRPsForTeam = 0
		for m in self.getCompletedMatchesForTeam(team):
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
					defenses = timd.avgSuccessfulTimesCrossedDefensesTele[defenseCategory]
					for defense, value in defenses:
						t += value 
					totalAvgDefenseCategoryCrossings += value / len(defenses)
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
		

	def stanDevSumForDefenseCategory(self, alliance, defenseCategory):
		varianceValues = []			#add variance for each data point to array
		stanDevSum = 0
		for team in alliance:
			timds = self.getCompletedTIMDsForTeam(team)
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

	def stanDevSumForDefenseCategoryWithExclusion(self, alliance, teamWithMatchesToExclude, sTIMD, defenseCategory):
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
				timds = self.getCompletedTIMDsForTeam(team)
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
		return 5 * team.calculatedData.challengePercentage * len(self.getCompletedTIMDsForTeam(team)) + 15 * team.calculatedData.scalePercentage * len(self.getCompletedTIMDsForTeam(team))

	def totalAvgNumShotPointsForTeam(self, team):
		#print "TESTING" + str(team.calculatedData)
		# if isinstance(team.calculatedData, {}.__class__): team.calculatedData = DataModel.CalculatedTeamData(**team.calculatedData)
		if team.calculatedData.avgHighShotsTele != None:
			return 5 * (team.calculatedData.avgHighShotsTele) + 10 * team.calculatedData.avgHighShotsAuto + 5 * team.calculatedData.avgLowShotsAuto + 2 * team.calculatedData.avgLowShotsTele
	
	def totalSDShotPointsForTeam(self, team):
		return 5 * team.calculatedData.sdHighShotsTele + 10 * team.calculatedData.sdHighShotsAuto + 5 * team.calculatedData.sdLowShotsAuto + 2 * team.calculatedData.sdLowShotsTele

	def totalAvgNumShotsForAlliance(self, alliance):
		totalAvgNumShots = 0
		for team in alliance:
			if team.calculatedData.avgHighShotsAuto:
				totalAvgNumShots += team.calculatedData.avgHighShotsAuto + team.calculatedData.avgHighShotsTele + team.calculatedData.avgLowShotsTele + team.calculatedData.avgLowShotsAuto
		return totalAvgNumShots	/ len(alliance)

	def totalAvgNumShotsForAllianceWithExclusion(self, alliance, teamWithMatchesToExclude, timd):
		totalAvgNumShots = 0
		for team in alliance:
			if team.number == teamWithMatchesToExclude.number:
				totalAvgNumShots += timd.numHighShotsMadeAuto + timd.numHighShotsMadeTele + timd.numLowShotsMadeAuto + timd.numLowShotsMadeTele
			else:
				totalAvgNumShots += team.calculatedData.avgHighShotsAuto + team.calculatedData.avgHighShotsTele + team.calculatedData.avgLowShotsTele + team.calculatedData.avgLowShotsAuto
		return totalAvgNumShots / len(alliance)

	def highShotAccuracyForAlliance(self, alliance):
		overallHighShotAccuracy = 0
		for team in alliance:
			overallHighShotAccuracy += team.calculatedData.highShotAccuracyAuto
			overallHighShotAccuracy += team.calculatedData.highShotAccuracyTele
		return overallHighShotAccuracy / len(alliance)

	def blockedShotPointsForAlliance(self, alliance, opposingAlliance):
		blockedShotPoints = 0
		for team in opposingAlliance:
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
		if o == str(self.ourTeamNum) + " has insufficient data" or o == 0.0:
			return None
		else:	
			return stats.norm.cdf(x,u,o)

	def sumOfStandardDeviationsOfShotsForAlliance(self, alliance):
		for team in alliance:
			sumOfStanDev += sp.stats.tvar([timd.numHighShotsMadeAuto for timd in self.getCompletedTIMDsForTeam(team) if timd.numHighShotsMadeAuto != None])
			sumOfStanDev += sp.stats.tvar([timd.numHighShotsMadeTele for timd in self.getCompletedTIMDsForTeam(team) if timd.numHighShotsMadeAuto != None])
			sumOfStanDev += sp.stats.tvar([timd.numLowShotsMadeAuto for timd in self.getCompletedTIMDsForTeam(team) if timd.numHighShotsMadeAuto != None])
			sumOfStanDev += sp.stats.tvar([timd.numLowShotsMadeTele for timd in self.getCompletedTIMDsForTeam(team) if timd.numHighShotsMadeAuto != None])
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
			timds = self.getCompletedTIMDsForTeam(team)
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


	def timesDefensesFacedInAllMatches(self):
		outputDict = {'pc' : 0, 'cdf' : 0, 'mt' : 0, 'rp' : 0, 'sp' : 0, 'db' : 0, 'rt' : 0, 'rw' : 0, 'lb' : 0}
		for match in self.comp.matches:
			for d in outputDict:
				if match.blueDefensePositions != None:
					if d in match.blueDefensePositions:
						outputDict[d] += 3
					if d in match.redDefensePositions:
						outputDict[d] += 3
		return outputDict

	def timesDefensesFacedInAllMatchesForTeam(self, team):
		outputDict = {'pc' : 0, 'cdf' : 0, 'mt' : 0, 'rp' : 0, 'sp' : 0, 'db' : 0, 'rt' : 0, 'rw' : 0, 'lb' : 0}
		for match in self.comp.matches:
			if team.number in match.redAllianceTeamNumbers:
				for d in outputDict:
					if match.blueDefensePositions != None:
						if d in match.blueDefensePositions:
							outputDict[d] += 1
			elif team.number in match.blueAllianceTeamNumbers:
				for d in outputDict:
					if match.blueDefensePositions != None:
						if d in match.redDefensePositions:
							outputDict[d] += 1
		return outputDict

	def predictedCrosses(self, team, defense):
		predictedCrossesForDefense = 0.0
		timesDefenseFacedAllBots = 0
		timesDefenseFacedOneBot = 0
		avgCrossesDefenseAcrossComp = 0.0
		Xa = 0
		Xobs = self.timesDefensesFacedInAllMatches()[defense]
		Fobs = self.timesDefensesFacedInAllMatchesForTeam(team)[defense]
		timdsForTeam = self.getCompletedTIMDsForTeam(team)
		for team1 in self.comp.teams:
			for dC, d in team.calculatedData.avgSuccessfulTimesCrossedDefensesAuto.items():
				if d == defense:
					avgCrossesDefenseAcrossComp += team.calculatedData.avgSuccessfulTimesCrossedDefensesTele[dC][d]
		avgCrossesDefenseAcrossComp /= (len(self.comp.teams) * 2)
		if sum(self.timesDefensesFacedInAllMatches().values()) > 0:
			Xprop = Xobs / sum(self.timesDefensesFacedInAllMatches().values())
		if sum(self.timesDefensesFacedInAllMatches().values()) > 0:
			Fprop = Fobs / sum(self.timesDefensesFacedInAllMatchesForTeam(team).values())
		for dC, d in team.calculatedData.avgSuccessfulTimesCrossedDefensesAuto.items():
			if d == defense:
				Xa += team.calculatedData.avgSuccessfulTimesCrossedDefensesTele[dC][d] 
		alphaForDefense = {'pc' : 0, 'cdf' : 0, 'mt' : 0, 'rp' : 0, 'sp' : 0, 'db' : 0, 'rt' : 0, 'rw' : 0, 'lb' : 0}
		for d in alphaForDefense:
			if sum(self.timesDefensesFacedInAllMatches().values()) + sum(self.timesDefensesFacedInAllMatchesForTeam(team).values()) > 0:
				alphaForDefense[d] = (self.timesDefensesFacedInAllMatches()[d]/sum(self.timesDefensesFacedInAllMatches().values())) + (self.timesDefensesFacedInAllMatchesForTeam(team)[d]/sum(self.timesDefensesFacedInAllMatchesForTeam(team).values()))
		betaForDefense = {'pc' : 0, 'cdf' : 0, 'mt' : 0, 'rp' : 0, 'sp' : 0, 'db' : 0, 'rt' : 0, 'rw' : 0, 'lb' : 0}
		for d in betaForDefense:
			if sum(alphaForDefense.values()) > 0:
				betaForDefense[d] = alphaForDefense[d] / sum(alphaForDefense.values())
		thetaForDefense = sum(betaForDefense.values())
		if Xobs > 0:
			predictedCrossesForDefense += ((avgCrossesDefenseAcrossComp * thetaForDefense) + (Xa * Xobs)) / (Xobs + 1)
		return predictedCrossesForDefense
	
	def listOfSuperDataPointsForTIMD(self, timd):
		return [timd.rankTorque, timd.rankSpeed, timd.rankEvasion, timd.rankDefense, timd.avgBallControl]

	def sdOfRValuesAcrossCompetition(self):
		if len(self.comp.TIMDs) <= 0:
			return None
		allSuperDataPoints = []
		[allSuperDataPoints.extend(self.listOfSuperDataPointsForTIMD(timd)) for timd in self.comp.TIMDs if self.timdIsCompleted(timd)]
		return np.std(allSuperDataPoints)

	def RScore(self, team, key):
		avgRValue = self.averageTIMDObjectOverMatches(team, key)
		averageRValuesOverComp = 0.0
		for team1 in self.comp.teams:
			averageRValuesOverComp += self.averageTIMDObjectOverMatches(team1, key)
		averageRValuesOverComp /= len(self.comp.teams)
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
		RScore = 2 * s(avgRValue, averageRValuesOverComp, self.comp.sdRScores)
		return RScore

	def sdPredictedScoreForMatch(self, match):
		sdPredictedScoreForMatch = {'blue' : 0, 'red' : 0}
		totalSDNumShots = 0
		blueTeams = []
		for teamNumber in match.blueAllianceTeamNumbers:
			blueTeams.append(self.getTeamForNumber(teamNumber))
			predictedScoreForMatch['blue'] += self.totalSDShotPointsForTeam(team)
		
		redTeams = []
		for teamNumber in match.redAllianceTeamNumbers:
			redTeams.append(self.getTeamForNumber(teamNumber)) 

		predictedScoreForMatch['blue'] -= self.blockedShotPointsForAllianceSD(blueTeams, redTeams)
		predictedScoreForMatch['blue'] += self.reachPointsForAlliance(blueTeams)
		crossPointsForAlliance = 0
		for team in blueTeams:
			for defenseCategory in team.calculatedData.avgSuccessfulTimesCrossedDefensesTele:
				crossPointsForAlliance += min(sum(team.calculatedData.avgSuccessfulTimesCrossedDefensesTele[defenseCategory].values()), 2)
				crossPointsForAlliance += min(sum(team.calculatedData.avgSuccessfulTimesCrossedDefensesAuto[defenseCategory].values()), 2)
		predictedScoreForMatch['blue'] += crossPointsForAlliance

	def drivingAbility(self, team, match):
		timd = self.getTIMDForTeamNumberAndMatchNumber(team, match)
		return (1 * timd.rankTorque) + (1 * timd.rankBallControl) + (1 * timd.rankEvasion) + (1 * timd.rankDefense) + (1 * timd.rankSpeed)

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
		for match in self.matchesThatHaveBeenPlayed():
			for team in self.teamsInMatch(match):
				if not team in teamsInValidMatches: teamsInValidMatches.append(team)
		numTeamsInValidMatches = len(teamsInValidMatches)
		matrixOfMatches = np.zeros((numTeamsInValidMatches, numTeamsInValidMatches))
		for team1 in teamsInValidMatches:	#Create an array where the values correspond to how many matches two teams played together in the same alliance
			for team2 in teamsInValidMatches:
				occurrence = len([match for match in self.matchesThatHaveBeenPlayed() if self.teamsAreOnSameAllianceInMatch(team1, team2, match)])
				matrixOfMatches[teamsInValidMatches.index(team1), teamsInValidMatches.index(team2)] = occurrence
		
		inverseMatrixOfMatchOccurrences = np.linalg.inv(matrixOfMatches)	
		teamDeltas = []
		for team1 in teamsWithMatchesPlayed:
			oppositionPredictedScore = 0
			oppositionActualScore = 0
			for match in self.getPlayedMatchesForTeam(team):
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
		ATeam = self.getTeamForNumber(timd.teamNumber)
		teamsWithMatchesPlayed = []
		for team in self.comp.teams:
			if len(self.getCompletedTIMDsForTeam(team)) > 0:
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
		ourTeam = self.getTeamForNumber(self.ourTeamNum)
		alliance = [ourTeam, team]
		predictedScoreCustomAlliance = self.predictedScoreCustomAlliance(alliance) 
		if math.isnan(predictedScoreCustomAlliance):
			return None
		return self.predictedScoreCustomAlliance(alliance) 

	def teamInMatchFirstPickAbility(self, team, match):
		ourTeam = self.getTeamForNumber(self.ourTeamNum)
		alliance = [ourTeam, team]
		predictedScoreCustomAlliance = self.predictedScoreCustomAlliance(alliance) 
		if math.isnan(predictedScoreCustomAlliance):
			return None
		return self.predictedScoreCustomAlliance(alliance) 

	def secondPickAbility(self, team):
		gamma = 0.5
		teamsArray = [loopTeam for loopTeam in self.comp.teams if self.getCompletedTIMDsForTeam(loopTeam) > 0] 
		secondPickAbility = {}
		ourTeam = self.getTeamForNumber(self.ourTeamNum)
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
			if len(self.getCompletedTIMDsForTeam(team)) > 0:
				teamsArray.append(team1)
		secondPickAbility = {}
		ourTeam = self.getTeamForNumber(self.ourTeamNum)
		citrusDPRMatrix = self.citrusDPR(team)
		for team1 in teamsArray:
			if team1.number != self.ourTeamNum and team1.number != team.number:	#Loop through all of the teams and find the score contribution of the team whose
				citrusDPR = citrusDPRMatrix[teamsArray.index(team1) - 1]
				allianceeRobots = [ourTeam, team, team1]				
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
			team1 = self.getTeamForNumber(teamNumber)
			if teamNumber != self.ourTeamNum:
				firstPickAbilityArray.append(team1)
		firstPickAbilityArray = sorted(firstPickAbilityArray, key = lambda team: team.calculatedData.firstPickAbility, reverse=True) #Sort teams by firstPickAbility
		if len(firstPickAbilityArray) == len(team.calculatedData.secondPickAbility) and len(firstPickAbilityArray) >= 16:
			for t in range(0,15):
				first16.append(firstPickAbilityArray[t])
			for t in first16:
				overallSecondPickAbility += team.calculatedData.secondPickAbility[t.number]
		return overallSecondPickAbility / 16

	def overallSecondPickAbilityWithExclusion(self, team, timd):
		firstPickAbilityArray = []
		first16 = []
		overallSecondPickAbility = 0.0
		for teamNumber in timd.calculatedData.secondPickAbility:
			team1 = self.getTeamForNumber(teamNumber)
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
		predictedScoreForMatch = {'blue': {'score' : 0.0, 'RP' : 0.0}, 'red': {'score' : 0.0, 'RP' : 0.0}}

		# Blue Alliance First
		totalAvgNumShots = 0
		blueTeams = []
		for teamNumber in match.blueAllianceTeamNumbers:
			team = self.getTeamForNumber(teamNumber)
			blueTeams.append(team)
			if self.totalAvgNumShotPointsForTeam(team) != None:
				predictedScoreForMatch['blue']['score'] += self.totalAvgNumShotPointsForTeam(team)

		redTeams = []
		for teamNumber in match.redAllianceTeamNumbers:
			redTeams.append(self.getTeamForNumber(teamNumber))
		predictedScoreForMatch['blue']['score'] -=  5 * (self.blockedShotPointsForAlliance(blueTeams, redTeams)) - ((self.blockedShotPointsForAlliance(blueTeams, redTeams) + self.blockedShotPointsForAlliance(redTeams, blueTeams)) / 2)
		if self.reachPointsForAlliance(blueTeams) != None:
			predictedScoreForMatch['blue']['score'] += self.reachPointsForAlliance(blueTeams)
		
		for defCategory in blueTeams[0].calculatedData.avgSuccessfulTimesCrossedDefensesTele.values():
			crossesForCategory = 0.0
			for defense in defCategory:
				for team in blueTeams:
					crossesForCategory += self.predictedCrosses(team, defense)
			if len(defCategory) != 0:
				predictedScoreForMatch['blue']['score'] += 5 * min(crossesForCategory / len(defCategory), 2)
			else: 
				predictedScoreForMatch['blue']['score'] += 5 * min(crossesForCategory, 2)

		productOfScaleAndChallengePercentages = 1

		standardDevCategories = []
		for team in blueTeams:
			if self.siegeConsistency(team) != None:
				productOfScaleAndChallengePercentages *= self.siegeConsistency(team)
		captureRPs = self.probabilityDensity(8.0, self.totalAvgNumShotsForAlliance(blueTeams), self.sumOfStandardDeviationsOfShotsForAlliance(blueTeams)) * productOfScaleAndChallengePercentages
		if not math.isnan(captureRPs):
			predictedScoreForMatch['blue']['RP'] += captureRPs
		
		breachRPs = 1.0
		for defenseCategory in self.categories:
			standardDevCategories.append(self.stanDevSumForDefenseCategory(blueTeams, defenseCategory))
		standardDevCategories = sorted(standardDevCategories)	#Sort the array of standard deviations for defense categories

		for category in range(1, len(standardDevCategories) + 1):	#Sort and calculate breach chance using max 4 categories
			category = self.categories[category - 1]
			breachRPs *= self.probabilityDensity(2.0, self.totalAvgDefenseCategoryCrossingsForAlliance(blueTeams, category), self.stanDevSumForDefenseCategory(blueTeams, category))

		if not math.isnan(breachRPs):
			predictedScoreForMatch['blue']['RP'] += breachRPs			

		#Red Alliance Next
		totalAvgNumShots = 0
		redTeams = []
		for teamNumber in match.redAllianceTeamNumbers:
			team = self.getTeamForNumber(teamNumber)
			redTeams.append(team)
			if self.totalAvgNumShotPointsForTeam(team) != None:
				predictedScoreForMatch['red']['score'] += self.totalAvgNumShotPointsForTeam(team)

		redTeams = []
		for teamNumber in match.redAllianceTeamNumbers:
			redTeams.append(self.getTeamForNumber(teamNumber))
		predictedScoreForMatch['red']['score'] -=  5 * (self.blockedShotPointsForAlliance(redTeams, blueTeams)) - ((self.blockedShotPointsForAlliance(redTeams, blueTeams) + self.blockedShotPointsForAlliance(blueTeams, redTeams)) / 2)
		if self.reachPointsForAlliance(redTeams) != None:
			predictedScoreForMatch['red']['score'] += self.reachPointsForAlliance(redTeams)
		
		for defCategory in blueTeams[0].calculatedData.avgSuccessfulTimesCrossedDefensesTele.values():
			crossesForCategory = 0.0
			for defense in defCategory:
				for team in blueTeams:
					crossesForCategory += self.predictedCrosses(team, defense)
			if len(defCategory) != 0:
				predictedScoreForMatch['red']['score'] += 5 * min(crossesForCategory / len(defCategory), 2)
			else:
				predictedScoreForMatch['red']['score'] += 5 * min(crossesForCategory, 2)
					
		productOfScaleAndChallengePercentages = 1

		standardDevCategories = []
		for team in redTeams:
			if self.siegeConsistency(team) != None:
				productOfScaleAndChallengePercentages *= self.siegeConsistency(team)
		captureRPs = self.probabilityDensity(8.0, self.totalAvgNumShotsForAlliance(redTeams), self.sumOfStandardDeviationsOfShotsForAlliance(redTeams)) * productOfScaleAndChallengePercentages
		if not math.isnan(captureRPs):
			predictedScoreForMatch['red']['RP'] += captureRPs
		breachRPs = 1.0
		# print "MATCHNUM: " + str(match.number)
		for defenseCategory in self.categories:
			standardDevCategories.append(self.stanDevSumForDefenseCategory(redTeams, defenseCategory))
		standardDevCategories = sorted(standardDevCategories)	#Sort the array of standard deviations for defense categories

		for category in range(1, len(standardDevCategories) + 1):	#Sort and calculate breach chance using max 4 categories
			category = self.categories[category - 1]
			breachRPs *= self.probabilityDensity(2.0, self.totalAvgDefenseCategoryCrossingsForAlliance(redTeams, category), self.stanDevSumForDefenseCategory(redTeams, category))

		if not math.isnan(breachRPs):
			predictedScoreForMatch['red']['RP'] += breachRPs	

		return predictedScoreForMatch
		
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
			timd = self.getTIMDForTeamNumberAndMatchNumber(teamNum, match.number)
			for defense in timd.timesSuccessfulCrossedDefensesTele.values():
				blueAllianceCrosses += len(defense) - 1
			for defense in timd.timesSuccessfulCrossedDefensesAuto.values():
				blueAllianceCrosses += len(defense) - 1
		numDefensesCrossedInMatch['blue'] = blueAllianceCrosses
		redAllianceCrosses = 0
		for teamNum in match.redAllianceTeamNumbers:
			timd = self.getTIMDForTeamNumberAndMatchNumber(teamNum, match.number)
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
					team = self.getTeamForNumber(teamNumber)
					overallChallengeAndScalePercentage += self.siegeConsistency(team)
					overallBreachPercentage += team.calculatedData.breachPercentage

				if self.predictedScoreForMatch(match)['red']['score'] > self.predictedScoreForMatch(match)['blue']['score']:
					totalRPForTeam += 2
				elif self.predictedScoreForMatch(match)['red']['score'] == self.predictedScoreForMatch(match)['blue']['score']:
					totalRPForTeam += 1

			elif team.number in match.blueAllianceTeamNumbers and match.blueScore == None:
				matchesToBePlayedCounter += 1
				for teamNumber in match.blueAllianceTeamNumbers:
					team = self.getTeamForNumber(teamNumber)
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
		numPlayedMatches = 0
		for match in self.comp.matches:
			if match.redScore > -0.5 and match.blueScore > -0.5:
				numPlayedMatches += 1
		return numPlayedMatches

	def actualSeeding(self):
		return sorted(self.comp.teams, key=attrgetter('calculatedData.numRPs', 'calculatedData.numAutoPoints', 'calculatedData.numScaleAndChallengePoints'), reverse=True)

	def getRankingForTeam(self, team):
		return self.actualSeeding().index(team)

	def predictedSeeding(self):
		return sorted(self.comp.teams, key=attrgetter('calculatedData.predictedRPs', 'calculatedData.autoAbility', 'calculatedData.siegeAbility'))

	def doCalculations(self, FBC):
		#team Metrics
		#if self.numPlayedMatchesInCompetition() > 0:
		self.comp.sdRScores = self.sdOfRValuesAcrossCompetition()
		for team in self.comp.teams:
			timds = self.getCompletedTIMDsForTeam(team)
			t = team.calculatedData
			if len(timds) <= 0:
				print "No Complete TIMDs for team " + str(team.number) + ", " + team.name
			else:
				print("Beginning calculations for team: " + str(team.number) + "..." + team.name)
				#Super Scout Averages
				t.avgTorque = self.averageTIMDObjectOverMatches(team, 'rankTorque')
				t.avgSpeed = self.averageTIMDObjectOverMatches(team, 'rankSpeed')
				t.avgEvasion = self.averageTIMDObjectOverMatches(team, 'rankEvasion')
				t.avgDefense = self.averageTIMDObjectOverMatches(team, 'rankDefense')
				t.avgBallControl = self.averageTIMDObjectOverMatches(team, 'rankBallControl')
				t.RScoreTorque = self.RScore(team, 'rankTorque')
				t.RScoreSpeed = self.RScore(team, 'rankSpeed')
				t.RScoreEvasion = self.RScore(team, 'rankEvasion')
				t.RScoreDefense = self.RScore(team, 'rankDefense')
				t.RScoreBallControl = self.RScore(team, 'rankBallControl')
				t.disabledPercentage = self.percentagesOverAllTIMDs(team, 'didGetDisabled')
				t.incapacitatedPercentage = self.percentagesOverAllTIMDs(team, 'didGetIncapacitated')
				t.disfunctionalPercentage = self.disfunctionalPercentage(team)

				#Auto
				t.avgHighShotsAuto = self.averageTIMDObjectOverMatches(team, 'numHighShotsMadeAuto')
				t.avgLowShotsAuto = self.averageTIMDObjectOverMatches(team, 'numLowShotsMadeAuto')
				t.reachPercentage = self.percentagesOverAllTIMDs(team, 'didReachAuto')
				t.highShotAccuracyAuto = self.shotAccuracy(team, True, True)
				t.lowShotAccuracyAuto = self.shotAccuracy(team, True, False)
				t.numAutoPoints = self.numAutoPointsForTeam(team)
				t.avgMidlineBallsIntakedAuto = self.avgBallsIntaked(team, 'ballsIntakedAuto')
				t.sdHighShotsAuto = self.standardDeviationObjectOverAllMatches(team, 'numHighShotsMadeAuto')
				t.sdLowShotsAuto = self.standardDeviationObjectOverAllMatches(team, 'numLowShotsMadeAuto')
				# t.sdMidlineBallsIntakedAuto = self.standardDeviationObjectOverAllMatches(team, 'ballsIntakedAuto')
				t.sdBallsKnockedOffMidlineAuto = self.standardDeviationObjectOverAllMatches(team, 'numBallsKnockedOffMidlineAuto')
				t.avgSuccessfulTimesCrossedDefensesAuto = self.averageDictionaries(self.makeArrayOfDictionaries(team, 'timesSuccessfulCrossedDefensesAuto'))
			
				#Tele
				t.challengePercentage = self.percentagesOverAllTIMDs(team, 'didChallengeTele')
				t.scalePercentage = self.percentagesOverAllTIMDs(team, 'didScaleTele')
				t.avgGroundIntakes = self.averageTIMDObjectOverMatches(team, 'numGroundIntakesTele')
				t.avgBallsKnockedOffMidlineAuto = self.averageTIMDObjectOverMatches(team, 'numBallsKnockedOffMidlineAuto')
				t.avgShotsBlocked = self.averageTIMDObjectOverMatches(team, 'numShotsBlockedTele')
				t.avgHighShotsTele = self.averageTIMDObjectOverMatches(team, 'numHighShotsMadeTele')
				t.avgLowShotsTele = self.averageTIMDObjectOverMatches(team, 'numLowShotsMadeTele')
				t.highShotAccuracyTele = self.shotAccuracy(team, False, True)
				t.lowShotAccuracyTele = self.shotAccuracy(team, False, False)
				t.blockingAbility = self.blockingAbility(team)
				t.teleopShotAbility = self.teleopShotAbility(team)
				t.siegeConsistency = self.siegeConsistency(team)
				t.siegeAbility = self.siegeAbility(team)
				t.siegePower = self.siegePower(team)
				t.avgSuccessfulTimesCrossedDefensesTele = self.averageDictionaries(self.makeArrayOfDictionaries(team, 'timesSuccessfulCrossedDefensesTele'))
				t.sdHighShotsTele = self.standardDeviationObjectOverAllMatches(team, 'numHighShotsMadeTele')
				t.sdLowShotsTele = self.standardDeviationObjectOverAllMatches(team, 'numLowShotsMadeTele')
				t.sdGroundIntakes = self.standardDeviationObjectOverAllMatches(team, 'numGroundIntakesTele')
				t.sdShotsBlocked = self.standardDeviationObjectOverAllMatches(team, 'numShotsBlockedTele')
				t.numRPs = self.numRPsForTeam(team)
				t.numScaleAndChallengePoints = self.numScaleAndChallengePointsForTeam(team)
				t.firstPickAbility = self.firstPickAbility(team)	
				t.secondPickAbility = self.secondPickAbility(team)
				t.overallSecondPickAbility = self.overallSecondPickAbility(team)
				t.predictedSeed = self.getRankingForTeam(team)
			
				FBC.addCalculatedTeamDataToFirebase(team.number, t)
				print("Putting calculations for team " + str(team.number) + " to Firebase.")
				print("Calculating TIMDs for team " + str(team.number))
				for timd in timds:
					c = timd.calculatedData
					c.highShotAccuracyTele = self.singleMatchShotAccuracy(timd, False, True)
					c.highShotAccuracyAuto = self.singleMatchShotAccuracy(timd, True, True)
					c.lowShotAccuracyTele = self.singleMatchShotAccuracy(timd, False, False)
					c.lowShotAccuracyAuto = self.singleMatchShotAccuracy(timd, True, False)
					c.siegeAbility = self.singleSiegeAbility(timd)
					c.numRPs = self.RPsGainedFromMatch(self.getMatchForNumber(timd.matchNumber))
					c.numAutoPoints = self.numAutoPointsForTIMD(timd)
					c.numScaleAndChallengePoints = c.siegeAbility #they are the same
					c.scoreContribution = self.scoreContribution(timd)
					c.RScoreSpeed = self.singleMatchRScore(timd, 'rankSpeed')
					c.RScoreEvasion = self.singleMatchRScore(timd, 'rankEvasion')
					c.RScoreDefense = self.singleMatchRScore(timd, 'rankDefense')
					c.RScoreTorque = self.singleMatchRScore(timd, 'rankTorque')
					c.RScoreBallControl = self.singleMatchRScore(timd, 'rankBallControl')
					c.RScoreDrivingAbility = 1 * c.RScoreSpeed + 1 * c.RScoreEvasion + 1 * c.RScoreDefense + 1 * c.RScoreTorque + 1 * c.RScoreBallControl
					c.firstPickAbility = self.teamInMatchFirstPickAbility(team, self.getMatchForNumber(timd.matchNumber))
					c.secondPickAbility = self.secondPickAbilityWithExclusion(team, timd)
					c.overallSecondPickAbility = self.overallSecondPickAbilityWithExclusion(team, timd)
					c.numBallsIntakedOffMidlineAuto = len(utils.makeDictFromTIMD(timd)['ballsIntakedAuto'])
		#Match Metrics
		for match in self.comp.matches:
			# if match.blueScore > None and match.redScore > None:
			if match.blueScore != None and match.redScore != None:
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
			self.comp.averageScore = self.avgCompScore()
			self.comp.actualSeeding = self.actualSeeding()
			self.comp.predictedSeeding = self.predictedSeeding()
			

