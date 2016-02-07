
# Math.py
import utils
import random
import firebaseCommunicator
import math
import numpy as np
import DataModel

import sys, traceback


class Calculator(object):
	"""docstring for Calculator"""
	def __init__(self, competition):
		super(Calculator, self).__init__()
		self.comp = competition
		self.categories = ['a', 'b', 'c', 'd', 'e']
		
		
	def getTeamForNumber(self, num):
		num = int(num)
		for t in self.comp.teams: print t.number
		for team in self.comp.teams:
			if team.number == num:
				if isinstance(team.calculatedData, {}.__class__): team.calculatedData = DataModel.CalculatedTeamData(**team.calculatedData) #We shouldnt have to do this here, it should already be done. Don't have time to figure out why right now.
				print("TCD: " + str(team.calculatedData))
				return team
		print "NO TEAM FOR NUMBER: " + str(num)

	def getMatchForNumber(self, num):
		for match in self.comp.matches:
			if match.number == num:
				return match

	def getTIMDsForTeamNumber(self, num):
		timds = []
		for timd in self.comp.TIMDs:
			if timd.teamNumber == num:
				timds.append(timd)
		return timds

	def getPlayedTIMDsForTeam(self, team):
		timds = []
		#print("t: " + str(team.number))
		for timd in team.teamInMatchDatas:
			if timd.rankTorque > -1:
				timds.append(timd)
		print("timds: " + str(timds))
		return timds

	def getTIMDForTeamNumberAndMatchNumber(self, teamNumber, matchNumber): # Match number is an int
		for timd in self.getTIMDsForTeamNumber(teamNumber):
			if timd.matchNumber == matchNumber:
				return timd
		return -1

	def getPlayedMatchesForTeam(self, team):
		matchesPlayed = []
		for timd in self.getPlayedTIMDsForTeam(team):
			matchesPlayed.append(self.getMatchForNumber(timd.matchNumber))
		return matchesPlayed

	# Calculated Team Data
	def averageTIMDObjectOverMatches(self, team, key, coefficient = 1):
		timds = self.getPlayedTIMDsForTeam(team)
		if len(timds) == 0:
			return -1
		total = 0.0
		for timd in timds:
			 total += utils.makeDictFromTIMD(timd)[key]
		return total/len(timds)

	def standardDeviationObjectOverAllMatches(self, team, key, coefficient = 1):
		timds = self.getPlayedTIMDsForTeam(team)
		if len(timds) == 0:
			return -1
		total = 0.0
		for timd in timds:
			total += (self.averageTIMDObjectOverMatches(team, key) - utils.makeDictFromTIMD(timd)[key]) ** 2
		return math.sqrt(total)

	def percentagesOverAllTIMDs(self, team, key, coefficient = 1):
		 timds = self.getPlayedTIMDsForTeam(team)
		 if len(timds) == 0:
			return -1
		 conditionTrueCounter = 0.0
		 for timd in timds:
			if utils.makeDictFromTIMD(timd)[key] == True:
				conditionTrueCounter += 1
		 return conditionTrueCounter/len(timds)

	def disfunctionalPercentage(self, team):
		timds = self.getPlayedTIMDsForTeam(team)
		if len(timds) == 0:
			return -1
		wasOutOfPlayCounter = 0
		for timd in timds:
			if timd.didGetDisabled or timd.didGetIncapacitated:
				wasOutOfPlayCounter += 1
		return wasOutOfPlayCounter/len(timds)

	def highShotAccuracy(self, team, auto):
		timds = self.getPlayedTIMDsForTeam(team)
		if len(timds) == 0:
			return -1
		totalHighShotsMade = 0.0
		totalHighShotsMissed = 0.0
		if auto:
			for timd in timds:
				if timd.numHighShotsMadeAuto > -1 or timd.numHighShotsMissedAuto > -1:
					totalHighShotsMade += timd.numHighShotsMadeAuto
					totalHighShotsMissed += timd.numHighShotsMissedAuto
			if totalHighShotsMade + totalHighShotsMissed == 0:
				return 0
			else:
				return totalHighShotsMade / (totalHighShotsMade + totalHighShotsMissed)
		else:
			for timd in timds:
				if timd.numHighShotsMadeTele > -1 or timd.numHighShotsMissedTele > -1:
					totalHighShotsMade += timd.numHighShotsMadeTele
					totalHighShotsMissed += timd.numHighShotsMissedTele
			if totalHighShotsMade + totalHighShotsMissed == 0.0:
				return 0.0
			else:
				return totalHighShotsMade / (totalHighShotsMade + totalHighShotsMissed)

	def lowShotAccuracy(self, team, auto):
		timds = self.getPlayedTIMDsForTeam(team)
		if len(timds) == 0:
			return -1
		totalLowShotsMade = 0.0
		totalLowShotsMissed = 0.0
		if auto:
			for timd in timds:
				if timd.numHighShotsMadeAuto > -1 and timd.numHighShotsMissedAuto > -1:
					totalLowShotsMade += timd.numLowShotsMadeAuto
					totalLowShotsMissed += timd.numLowShotsMissedAuto
			if totalLowShotsMade + totalLowShotsMissed == 0:
				return 0
			else:
				return totalLowShotsMade / (totalLowShotsMade + totalLowShotsMissed)
		else:
			for timd in timds:
				if timd.numHighShotsMadeAuto > -1 or timd.numHighShotsMissedAuto > -1:
					totalLowShotsMade += timd.numLowShotsMadeTele
					totalLowShotsMissed += timd.numLowShotsMissedTele
				if totalLowShotsMade + totalLowShotsMissed == 0:
					return 0
				else:
					return totalLowShotsMade / (totalLowShotsMade + totalLowShotsMissed)
		return -1

	def avgBallsIntaked(self, team, key):
		timds = self.getPlayedTIMDsForTeam(team)
		avgBallsIntaked = 0.0
		for timd in timds:
			if timd.numHighShotsMadeAuto > -1:
				avgBallsIntaked += len(utils.makeDictFromTIMD(timd)[key])
		return avgBallsIntaked / len(timds)

	def flattenDictionary(self, dictionary):
		flattenedDict = {}
		for categoryDict in dictionary.values():
			for defense, dictionary in categoryDict.items():
				flattenedDict[defense] = dictionary
		return flattenedDict


	def makeArrayOfDictionaries(self, team, key): 
 		timds = self.getPlayedTIMDsForTeam(team)
 		arrayOfDictionaries = [] 
 		for timd in timds:
 			dictionary = utils.makeDictFromTIMD(timd)[key]
 			dictionary = self.flattenDictionary(dictionary)
 			if dictionary['rw'] > -1:
 				arrayOfDictionaries.append(dictionary) 
  		return arrayOfDictionaries 


 	def averageDictionaries(self, array):
 		outputDict = {}
 		
 		#print array
 		for dic in array:
			for key, value in dic.items():
				avg = 0.0
				#print "val " + str(value)
				for dictionary in array:
					print key
					if key in dictionary.keys():
						avg += len(dictionary[key])
					#print "avg for " + str(key) + " is " + str(avg)
				avg /= len(array)
				outputDict[key] = avg
			
 		#print outputDict
 		return outputDict


 	# def averageDictionaries(self, array):
 	# 	if array == -1:
 	# 		return -1
 	# 	outputArray = []
 	# 	numPlayed = 0
 	# 	print array
 	# 	for dictionary in array:
 	# 		for d in dictionary.values():
	 # 			for outcome in d.values():
	 # 				if outcome[0] == -1:
	 # 					numPlayed += 1
	 # 		for key in dictionary:
	 # 			totalForKey = 0
	 # 			for dictionary in array:
	 				
	 # 					print dictionary
	 # 					totalForKey += dictionary[key]
	 # 				outputArray.append(totalForKey/numPlayed)
 	# 	return outputArray

	def defenseAverageCrosses(self, array):
		if array == -1:
 			return -1
 		outputArray = []
 		numPlayed = 0
  		for dictionary in array:
  			if dictionary[0] > -1:
  				numPlayed += 1
 		for key in dictionary:	#Add all values of a common key 
 			totalForKey = 0
 			for dictionary in array:	
 				if dictionary[key] > -1:
 					totalForKey += dictionary[key]
 				outputArray.append(totalForKey/numPlayed)
 		return totalForKey

	def blockingAbility(self, team):
		allHighShotsAccuracies = 0
		for team in self.comp.teams:
			if team.calculatedData.highShotAccuracyTele > -1: allHighShotsAccuracies += team.calculatedData.highShotAccuracyTele 
		avgHighShotAccuracy = allHighShotsAccuracies / len(self.comp.teams)
		return 5 * avgHighShotAccuracy * team.calculatedData.avgShotsBlocked

	def autoAbility(self, team): 
		if team.calculatedData.avgHighShotsAuto != 0 and team.calculatedData.avgLowShotsAuto != 0:
			return 10 * team.calculatedData.avgHighShotsAuto + 5 * team.calculatedData.avgLowShotsAuto + 2 * team.calculatedData.reachPercentage + 10 
		else:
			return 10 * team.calculatedData.avgHighShotsAuto + 5 * team.calculatedData.avgLowShotsAuto + 2 * team.calculatedData.reachPercentage

	def teleopShotAbility(self, team): return (5 * team.calculatedData.avgHighShotsTele + 2 * team.calculatedData.avgLowShotsTele)

	def siegeAbility(self, team): return (15 * team.calculatedData.scalePercentage + 5 * team.calculatedData.challengePercentage)

	def siegeConsistency(self, team): return (team.calculatedData.scalePercentage + team.calculatedData.challengePercentage)

	def siegePower(self, team): return (team.calculatedData.siegeConsistency * team.calculatedData.siegeAbility)

	def numAutoPointsForTIMD(self, timd):
		defenseCrossesInAuto = 0
		for value in timd.timesSuccessfulCrossedDefensesAuto.values():
					if value > -1:
						defenseCrossesInAuto += 1
		if defenseCrossesInAuto > 1: print "ERROR: Num Auto Points From Defenses Is Too High."
		return 10 * int(timd.numHighShotsMadeAuto) + 5 * int(timd.numLowShotsMadeAuto) + 2 * (1 if timd.didReachAuto else 0) + 10 * int(defenseCrossesInAuto)

	def numAutoPointsForTeam(self, team):
		totalAutoPoints = 0
		for timd in self.getPlayedTIMDsForTeam(team):
			totalAutoPoints += self.numAutoPointsForTIMD(timd)
		return totalAutoPoints

	def numRPsForTeam(self, team):
		totalRPsForTeam = 0
		for m in self.getPlayedMatchesForTeam(team):
			RPs = self.RPsGainedFromMatch(m)
			if team.number in m.blueAllianceTeamNumbers:
				totalRPsForTeam += RPs['blue']
			elif team.number in m.redAllianceTeamNumbers:
				totalRPsForTeam += RPs['red']
			else:
				print "ERROR: team not in match."

	def totalAvgDefenseCategoryCrossingsForAlliance(self, alliance, defenseCategory):
		totalAvgDefenseCategoryCrossings = 0
		for team in alliance:
			totalAvgDefenseCategoryCrossings += (self.avgDefenseCategoryCrossingsForTeam(team, 'avgSuccessfulTimesCrossedDefensesTele', defenseCategory) + self.avgDefenseCategoryCrossingsForTeam(team, 'avgSuccessfulTimesCrossedDefensesAuto', defenseCategory))
		return totalAvgDefenseCategoryCrossings / (len(alliance) * 2)

	def avgDefenseCategoryCrossingsForTeam(self, team, key, defenseCategory):	#Use in standard deviation calculation for each defenseCategory
		#print utils.makeDictFromTeam(team)['calculatedData']['avgSuccessfulTimesCrossedDefensesAuto'][defenseCategory]
		category = utils.makeDictFromTeam(team)["calculatedData"][key][defenseCategory]
		#print category
		total = 0
		for value in category.values():
			#print "TESTING" + str(value)
			total += value
		return total / len(category)
		

	def stanDevSumForDefenseCategory(self, alliance, defenseCategory):
		varianceValues = []			#add variance for each data point to array
		stanDevSum = 0
		for team in alliance:
			timds = self.getPlayedTIMDsForTeam(team)
			if len(timds) == 0:
				return -1
			else:
				difOfAvgSquaresTele = 0
				difOfAvgSquaresAuto = 0
				for timd in timds:	#find the variances for a team's crosses in the specified category in auto, and then the same in tele
					
					numCrossesForDefenseCategoryInMatchTele = 0
					numCrossesForDefenseCategoryInMatchAuto = 0
					for value in timd.timesSuccessfulCrossedDefensesTele[defenseCategory].values():
						numCrossesForDefenseCategoryInMatchTele += len(value)
					for value in timd.timesSuccessfulCrossedDefensesAuto[defenseCategory].values():
						numCrossesForDefenseCategoryInMatchAuto += len(value)

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
		return 5 * team.calculatedData.challengePercentage * len(self.getPlayedTIMDsForTeam(team)) + 15 * team.calculatedData.scalePercentage * len(self.getPlayedTIMDsForTeam(team))

	'''def avgNumberOfTimesDefenseCrossedByAlliance(self, alliance, defense):
		totalAvg = 0
		for team in alliance:
			avgTimesDefenseCrossedForTeam = 0
			for defenseKey, value in team.calculatedData.avgTimesCrossedDefensesAuto:
				if defenseKey == defense and value > -1: avgTimesDefenseCrossedForTeam += value
			for defenseKey, value in team.calculatedData.avgTimesCrossedDefensesTele:
				if defenseKey == defense and value > -1: avgTimesDefenseCrossedForTeam += value
			totalAvg += avgTimesDefenseCrossedForTeam
		return totalAvg / 3

	def predictedScoreLambda1(self, alliance, a, defense):
		return (2 - (a / 5) / self.avgNumberOfTimesDefenseCrossedByAlliance(alliance))

	def predictedScoreBeta(self, alliance, a, defenseCategory):
		total = 0
		for category, defenses in self.defenseCategories[defenseCategory]:
			for defense in defenses:
				total += self.predictedScoreLambda1(alliance, a, defense)
		return total / len(self.defenseCategories[defenseCategory])

	def sumOf4SmallestBetas(self, alliance, a):
		betas = []
		for category, defenses in self.defenseCategories:
			betas.append(self.predictedScoreBeta(alliance, a, category))
		betas = sorted(betas)
		return betas[0] + betas[1] + betas[2] + betas[3]

	def createCrossingsArray(self, alliance, a):
		betaA = self.predictedScoreBeta(alliance, a, 'a')
		betaB = self.predictedScoreBeta(alliance, a, 'b')
		betaC = self.predictedScoreBeta(alliance, a, 'c')
		betaD = self.predictedScoreBeta(alliance, a, 'd')
		betaE = self.predictedScoreBeta(alliance, a, 'e')
		return sorted([betaA, betaA, betaB, betaB, betaC, betaC, betaD, betaD]) #low to high'''
	
	def totalAvgNumShotPointsForTeam(self, team):
		#print "TESTING" + str(team.calculatedData)
		if isinstance(team.calculatedData, {}.__class__): team.calculatedData = DataModel.CalculatedTeamData(**team.calculatedData)
		return 5 * (team.calculatedData.avgHighShotsTele) + 10 * team.calculatedData.avgHighShotsAuto + 5 * team.calculatedData.avgLowShotsAuto + 2 * team.calculatedData.avgLowShotsTele
	
	def totalSDShotPointsForTeam(self, team):
		return 5 * team.calculatedData.sdHighShotsTele + 10 * team.calculatedData.sdHighShotsAuto + 5 * team.calculatedData.sdLowShotsAuto + 2 * team.calculatedData.sdLowShotsTele

	def totalAvgNumShotsForAlliance(self, alliance):
		totalAvgNumShots = 0
		for team in alliance:
			totalAvgNumShots += team.calculatedData.avgHighShotsAuto + team.calculatedData.avgHighShotsTele + team.calculatedData.avgLowShotsTele + team.calculatedData.avgLowShotsAuto
		return totalAvgNumShots	

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
		return 5 * blockedShotPoints

	def blockedShotPointsForAllianceSD(self, alliance, opposingAlliance):
		blockedShotPoints = 0
		for team in opposingAlliance:
			blockedShotPoints += (self.highShotAccuracyForAlliance(alliance) * team.calculatedData.sdShotsBlocked)
		return 5 * blockedShotPoints

	def reachPointsForAlliance(self, alliance):
		reachPoints = 0
		for team in alliance:
			reachPoints += 2 * team.calculatedData.reachPercentage
		return reachPoints

	def probabilityDensity(self, x, u, o):
		if o == "1678 has insufficient data" or o == 0.0:
			return -1
		else:	
			return (1 / (math.sqrt(2 * math.pi ) * o) * (math.e)**(-1.0 * ((x - u)**2) / (2 * o**2))) #calculate percentage of a breach or capture 

	def sumOfStandardDeviationsOfShotsForAlliance(self, alliance):
		sumOfStandardDeviationsOfShotsForAlliance = 0
		shotVariances = []
		for team in alliance:
			autoHighShotVariance = 0
			autoLowShotVariance = 0
			teleHighShotVariance = 0
			teleLowShotVariance = 0.0
			timds = self.getPlayedTIMDsForTeam(team)
			if len(timds) == 0:
				return -1
			else:
				for timd in timds:
					if timd.numHighShotsMadeAuto > -1:
						autoHighShotVariance += (team.calculatedData.avgHighShotsAuto - timd.numHighShotsMadeAuto)**2	#For all shot data points, add all differences
						autoLowShotVariance += (team.calculatedData.avgLowShotsAuto - timd.numLowShotsMadeAuto)**2		#of the average for that data point minus
						teleHighShotVariance += (team.calculatedData.avgHighShotsTele - timd.numHighShotsMadeTele)**2	#each individual data point, divide by n
						teleLowShotVariance += (team.calculatedData.avgLowShotsTele - timd.numLowShotsMadeTele)**2		
				autoHighShotVariance /= len(timds)
				autoLowShotVariance /= len(timds)
				teleHighShotVariance /= len(timds)
				teleLowShotVariance /= len(timds)
				shotVariances.append(autoHighShotVariance)
				shotVariances.append(autoLowShotVariance)
				shotVariances.append(teleHighShotVariance)
				shotVariances.append(teleLowShotVariance)				
			for i in shotVariances:
				sumOfStandardDeviationsOfShotsForAlliance += i
			return math.sqrt(sumOfStandardDeviationsOfShotsForAlliance)

	def timesDefensesFacedInAllMatches(self):
		outputDict = {'pc' : 0, 'cdf' : 0, 'mt' : 0, 'rp' : 0, 'sp' : 0, 'db' : 0, 'rt' : 0, 'rw' : 0, 'lb' : 0}
		for match in self.comp.matches:
			for d in outputDict:
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
					if d in match.blueDefensePositions:
						outputDict[d] += 1
			elif team.number in match.blueAllianceTeamNumbers:
				for d in outputDict:
					if d in match.redDefensePositions:
						outputDict[d] += 1


	def predictedCrosses(self, team, defense):
		allTIMDs = []
		timesDefenseFacedAllBots = 0
		timesDefenseFacedOneBot = 0
		avgCrossesDefenseAcrossComp = 0.0
		timdsForTeam = self.getPlayedTIMDsForTeam(team)
		for team1 in self.comp.teams:
			allTIMDs.append(self.getPlayedTIMDsForTeam(team1))
			for dC, d in team.calculatedData.avgSuccessfulTimesCrossedDefensesAuto.items():
				if d == defense:
					avgCrossesDefensesAcrossComp += team.calculatedData.avgSuccessfulTimesCrossedDefensesAuto[dC][d] + team.calculatedData.avgSuccessfulTimesCrossedDefensesTele[dC][d]
		avgCrossesDefenseAcrossComp /= (len(self.comp.teams) * 2)
		Xprop = self.timesDefensesFacedInAllMatches()[defense]/sum(self.timesDefensesFacedInAllMatches().values())
		Fprop = self.timesDefensesFacedInAllMatchesForTeam(team)[defense]/sum(self.timesDefensesFacedInAllMatchesForTeam(team).values())

	def sdOfRValuesAcrossCompetition(self):
		avgOfAllRValues = 0.0
		allTIMDS = []
		sdOfRValues = 0.0
		for team in self.comp.teams:
			allTIMDS.append(self.getPlayedTIMDsForTeam(team))
			avgOfAllRValues += team.calculatedData.avgTorque + team.calculatedData.avgSpeed + team.calculatedData.avgEvasion + team.calculatedData.avgDefense + team.calculatedData.avgBallControl
		avgOfAllRValues /= (len(self.comp.teams) * 5)
		numberOfTIMDObjects = 0
		for timds in allTIMDS:
			for timd in timds:
				numberOfTIMDObjects += 1
				sdOfRValues += (avgOfAllRValues - timd.rankTorque)**2
				sdOfRValues += (avgOfAllRValues - timd.rankSpeed)**2
				sdOfRValues += (avgOfAllRValues - timd.rankEvasion)**2
				sdOfRValues += (avgOfAllRValues - timd.rankDefense)**2
				sdOfRValues += (avgOfAllRValues - timd.rankBallControl)**2
		sdOfRValues /= (numberOfTIMDObjects * 5)
		return math.sqrt(sdOfRValues)

	def RScore(self, team, key):
		avgRValue = averageTIMDObjectOverMatches(team, key)
		averageRValuesOverComp = 0.0
		for team1 in self.comp.teams:
			averageRValuesOverComp += averageTIMDObjectOverMatches(team, key)
		averageRValuesOverComp /= len(self.comp.teams)
		sdOfRValues = self.sdOfRValuesAcrossCompetition()
		RScore = 2 * self.probabilityDensity(avgRValue, averageRValuesOverComp, sdOfRValues)
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
			for defenseCategory in team.calculatedData.timesSuccessfulCrossedDefensesTele:
				crossPointsForAlliance += min(sum(team.calculatedData.timesSuccessfulCrossedDefensesTele[defenseCategory].values()), 2)
				crossPointsForAlliance += min(sum(team.calculatedData.timesSuccessfulCrossedDefensesAuto[defenseCategory].values()), 2)
		predictedScoreForMatch['blue'] += crossPointsForAlliance


	#Matches Metrics
	def predictedScoreForMatch(self, match):
		predictedScoreForMatch = {'blue': {'score' : 0, 'RP' : 0}, 'red': {'score' : 0, 'RP' : 0}}

		# Blue Alliance First
		totalAvgNumShots = 0
		blueTeams = []
		for teamNumber in match.blueAllianceTeamNumbers:
			team = self.getTeamForNumber(teamNumber)
			blueTeams.append(team)
			predictedScoreForMatch['blue']['score'] += self.totalAvgNumShotPointsForTeam(team)
		
		redTeams = []
		for teamNumber in match.redAllianceTeamNumbers:
			redTeams.append(self.getTeamForNumber(teamNumber))
		
		predictedScoreForMatch['blue']['score'] -= self.blockedShotPointsForAlliance(blueTeams, redTeams)
		predictedScoreForMatch['blue']['score'] += self.reachPointsForAlliance(blueTeams)
		productOfScaleAndChallengePercentages = 1

		standardDevCategories = []

		#print "TESTING" + str(self.calculatePercentage(8.0, self.totalAvgNumShotsForAlliance(blueTeams), self.sumOfStandardDeviationsOfShotsForAlliance(blueTeams)))

		for team in blueTeams:
			productOfScaleAndChallengePercentages *= (team.calculatedData.scalePercentage + team.calculatedData.challengePercentage)
		predictedScoreForMatch['blue']['RP'] += self.probabilityDensity(8.0, self.totalAvgNumShotsForAlliance(blueTeams), self.sumOfStandardDeviationsOfShotsForAlliance(blueTeams)) * productOfScaleAndChallengePercentages
		
		breachPercentage = 1

		for defenseCategory in blueTeams[0].calculatedData.avgSuccessfulTimesCrossedDefensesAuto:
			standardDevCategories.append(self.stanDevSumForDefenseCategory(blueTeams, defenseCategory))
		standardDevCategories = sorted(standardDevCategories)	#Sort the array of standard deviations for defense categories

		for category in range(1, len(standardDevCategories) + 1):	#Sort and calculate breach chance using max 4 categories
			category = self.categories[category - 1]
			breachPercentage *= self.probabilityDensity(2.0, self.totalAvgDefenseCategoryCrossingsForAlliance(redTeams, category), self.stanDevSumForDefenseCategory(redTeams, category))


		predictedScoreForMatch['blue']['RP'] += breachPercentage

		# Red Alliance Next
		totalAvgNumShots = 0
		redTeams = []
		for teamNumber in match.redAllianceTeamNumbers:
			team = self.getTeamForNumber(teamNumber)
			redTeams.append(team)
			predictedScoreForMatch['red']['score'] += self.totalAvgNumShotPointsForTeam(team)
		
		blueTeams = []
		for teamNumber in match.blueAllianceTeamNumbers:
			blueTeams.append(self.getTeamForNumber(teamNumber))
		
		predictedScoreForMatch['red']['score'] -= self.blockedShotPointsForAlliance(redTeams, blueTeams)
		predictedScoreForMatch['red']['score'] += self.reachPointsForAlliance(redTeams)
		productOfScaleAndChallengePercentages = 1

		standardDevCategories = []

		for team in redTeams:	#Find chance of a capture, award that many RPs
			productOfScaleAndChallengePercentages *= (team.calculatedData.scalePercentage + team.calculatedData.challengePercentage)

		predictedScoreForMatch['red']['RP'] += (self.probabilityDensity(8.0, self.totalAvgNumShotsForAlliance(redTeams), self.sumOfStandardDeviationsOfShotsForAlliance(redTeams) * productOfScaleAndChallengePercentages))
		
		breachPercentage = 1
								#Using a dictionary already sorted by category to loop through the defense categories
		for defenseCategory in redTeams[0].calculatedData.avgFailedTimesCrossedDefensesAuto:	#Find chance of a breach, award that many RPs, this is an arbitrary database locaiton, being used only for it's keys
			standardDevCategories.append(self.stanDevSumForDefenseCategory(redTeams, defenseCategory))	#Add standard deviation of crosses per category to array
		standardDevCategories = sorted(standardDevCategories)

		for category in range(1, len(standardDevCategories) + 1):	#Sort and calculate breach chance using max 4 categories
			category = self.categories[category - 1]
			breachPercentage *= self.probabilityDensity(2.0, self.totalAvgDefenseCategoryCrossingsForAlliance(redTeams, category), self.stanDevSumForDefenseCategory(redTeams, category))

		predictedScoreForMatch['red']['RP'] += breachPercentage


		return predictedScoreForMatch

		


	def breachPercentage(self, team):
		breachPercentage = 0
		for match in self.team.matches:
			if team.number in match.blueAllianceTeamNumbers and match.blueScore != -1:
				if match.blueAllianceDidBreach == True:
					breachPercentage += 1
			elif team.number in match.redAllianceTeamNumbers and match.blueScore != -1:
				if match.redAllianceDidBreach == True:
					breachPercentage += 1
		return breachPercentage/len(self.team.matches)


	def numDefensesCrossedInMatch(self, match):
		numDefensesCrossedInMatch = {'red': -1, 'blue': -1}
		blueAllianceCrosses = 0
		for teamNum in match.blueAllianceTeamNumbers:
			timd = self.getTIMDForTeamNumberAndMatchNumber(teamNum, match.number)
			for defense in timd.timesSuccessfulCrossedDefensesTele.values():
				blueAllianceCrosses += len(defense)
			for defense in timd.timesSuccessfulCrossedDefensesAuto.values():
				blueAllianceCrosses += len(defense)
		numDefensesCrossedInMatch['blue'] = blueAllianceCrosses
		redAllianceCrosses = 0
		for teamNum in match.redAllianceTeamNumbers:
			timd = self.getTIMDForTeamNumberAndMatchNumber(teamNum, match.number)
			for defense in timd.timesSuccessfulCrossedDefensesTele.values():
				redAllianceCrosses += len(defense)
			for defense in timd.timesSuccessfulCrossedDefensesAuto.values():
				redAllianceCrosses += len(defense)
		numDefensesCrossedInMatch['red'] = redAllianceCrosses

		return numDefensesCrossedInMatch


	def predictedNumberOfRPs(self, team):
		totalRPForTeam = 0
		overallChallengeAndScalePercentage = 0
		overallBreachPercentage = 0
		matchesToBePlayedCounter = 0

		for match in self.comp.matches:		
			if team.number in match.redAllianceTeamNumbers and match.redScore == -1:	#Only award predictedRPs if the match has not been played
				matchesToBePlayedCounter += 1
				for teamNumber in match.blueAllianceTeamNumbers:
					team = self.getTeamForNumber(teamNumber)
					overallChallengeAndScalePercentage += team.calculatedData.challengePercentage + team.calculatedData.scalePercentage
					overallBreachPercentage += team.calculatedData.breachPercentage

				if self.calculatedData.predictedScoreForMatch(match)['red']['score'] > self.calculatedData.predictedScoreForMatch(match)['blue']['score']:
					totalRPForTeam += 2
				elif self.calculatedData.predictedScoreForMatch(match)['red']['score'] == self.calculatedData.predictedScoreForMatch(match)['blue']['score']:
					totalRPForTeam += 1

			elif team.number in match.blueAllianceTeamNumbers and match.blueScore == -1:
				matchesToBePlayedCounter += 1
				for teamNumber in match.blueAllianceTeamNumbers:
					team = self.getTeamForNumber(teamNumber)
					overallChallengeAndScalePercentage += team.calculatedData.challengePercentage + team.calculatedData.scalePercentage
					overallBreachPercentage += team.calculatedData.breachPercentage

				if self.calculatedData.predictedScoreForMatch(match)['blue']['score'] > self.calculatedData.predictedScoreForMatch(match)['red']['score']:
					totalRPForTeam += 2
				elif self.calculatedData.predictedScoreForMatch(match)['red']['score'] == self.calculatedData.predictedScoreForMatch(match)['blue']['score']:
					totalRPForTeam += 1

			else:
				print 'This team does not exist or all matches have been played'

		totalRPForTeam += (overallChallengeAndScalePercentage / 3)
		totalRPForTeam += (overallBreachPercentage / 3)

		return totalRPForTeam + numRPsForTeam(team)

	def actualSeeding(self):
		rankedTeams = []
		for team in self.comp.teams:	#I don't know anything but bubble sorting ... :,(
			rankedTeams.append(team)
		for team in range(len(rankedTeams)-1, 0, -1):
			for i in range(team):
				if rankedTeams[i].calculatedData.numRPs < rankedTeams[i + 1].calculatedData.numRPs:
					temp = rankedTeams[i]
					rankedTeams[i] = rankedTeams[i + 1]
					rankedTeams[i + 1] = temp
				elif rankedTeams[i].calculatedData.numRPs < rankedTeams[i + 1].calculatedData.numRPs:
					if rankedTeams[i].calculatedData.numAutoPoints < rankedTeams[i + 1].calculatedData.numAutoPoints:
						temp = rankedTeams[i]
						rankedTeams[i] = rankedTeams[i + 1]
						rankedTeams[i + 1] = temp
					elif rankedTeams[i].calculatedData.numAutoPoints < rankedTeams[i + 1].calculatedData.numAutoPoints:
						if rankedTeams[i].calculatedData.numScaleAndChallengePoints< rankedTeams[i + 1].calculatedData.numScaleAndChallengePoints:
							temp = rankedTeams[i]
							rankedTeams[i] = rankedTeams[i + 1]
							rankedTeams[i + 1] = temp

		return rankedTeams

	def getRankingForTeam(self, team):
		rankedTeams = self.actualSeeding()
		return rankedTeams.index(team) + 1



	def predictedSeeding(self):
		teamsArray = []
		for team in self.comp.teams:
			teamsArray.append(team)
		for team in range(len(teamsArray), 0, -1):
			for i in range(team):
				if teamsArray[i].calculatedData.predictedNumberOfRPs < teamsArray[i + 1].calculatedData.predictedNumberOfRPs:
					temp = teamsArray[i]
					teamsArray[i] = teamsArray[i + 1]
					teamsArray[i + 1] = temp
				elif teamsArray[i].calculatedData.predictedNumberOfRPs < teamsArray[i + 1].calculatedData.predictedNumberOfRPs:
					if self.autoAbility(teamsArray[i]) < self.autoAbility(teamsArray[i + 1]):
						temp = teamsArray[i]
						teamsArray[i] = teamsArray[i + 1]
						teamsArray[i + 1] = temp

		return teamsArray
	
	def predictedScoreCustomAlliance(self, alliance):
		predictedScoreCustomAlliance = 0		

		predictedScoreCustomAlliance += self.reachPointsForAlliance(alliance)
		productOfScaleAndChallengePercentages = 1

		standardDevCategories = []
		#print ("v" + str(self.calculatePercentage(2.0,1.0,3.0)))

		
		sdSum = self.sumOfStandardDeviationsOfShotsForAlliance(alliance)
		if sdSum == "1678 has insufficient data":
			return -1
		for team in alliance:
			productOfScaleAndChallengePercentages *= (team.calculatedData.scalePercentage + team.calculatedData.challengePercentage)
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


	def firstPickAbility(self, team):
		citrusC = self.getTeamForNumber(1678)
		alliance = [citrusC, team]
		return self.predictedScoreCustomAlliance(alliance) 

	
	def secondPickAbility(self, team):
		gamma = 0.5
		teamsWithMatchesPlayed = []
		for team in self.comp.teams:
			if len(self.getPlayedMatchesForTeam(team)) > 0:
				teamsWithMatchesPlayed.append(team)
		matrixOfMatches = np.zeros((len(teamsWithMatchesPlayed), len(teamsWithMatchesPlayed)))
		teamsArray = []
		secondPickAbility = {}
		citrusC = self.getTeamForNumber(1678)
		for team1 in teamsWithMatchesPlayed:	#Create an array where the values correspond to how many matches two teams played together in the same alliance
			teamsArray.append(team1)
			for team2 in teamsWithMatchesPlayed:
				occurrence = 0
				for match in self.comp.matches:
					if (team1.number in match.blueAllianceTeamNumbers and team2.number in match.blueAllianceTeamNumbers) or (team1.number in match.redAllianceTeamNumbers and team2.number in match.redAllianceTeamNumbers):
						occurrence += 1
				matrixOfMatches[teamsWithMatchesPlayed.index(team1), teamsWithMatchesPlayed.index(team2)] = occurrence

		# Create an array where the values correspond to how many matches two teams played together in the same alliance, and then shape it into a matrix
	
		inverseMatrixOfMatchOccurrences = np.linalg.inv(matrixOfMatches)	#Find the inverse of the matrix
		teamDeltas = np.array([])
		oppositionPredictedScore = 0
		oppositionActualScore = 0
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
			teamDeltas = np.append(teamDeltas, teamDelta)	#Calculate delta of each team (delta(team) = sum of predicted scores - sum of actual scores)
		teamDeltas.shape = (len(teamsWithMatchesPlayed), 1)	#Shape into a 1x(number of teams) matrix
		citrusDPRMatrix = np.multiply(inverseMatrixOfMatchOccurrences, teamDeltas)	#Multiply deltas matrix by InverseMatchOccurrences matrix to get citrusDPR

		for team1 in teamsArray:
			if team1.number != 1678 and team1.number != team.number:	#Loop through all of the teams and find the score contribution of the team whose
				citrusDPR = citrusDPRMatrix[teamsArray.index(team1)]	#second pick ability you are calculating for
				alliance3Robots = [citrusC, team, team1]				
				alliance2Robots = [citrusC, team1]
				scoreContribution = self.predictedScoreCustomAlliance(alliance3Robots) - self.predictedScoreCustomAlliance(alliance2Robots)
				secondPickAbility[team1.number] = gamma * scoreContribution * (1 - gamma) * int(citrusDPR)		#gamma is a constant

		return secondPickAbility

	


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
		totalScore = 0
		totalNumScores = 0
		for match in self.comp.matches:
			if match.blueScore > -1:
				totalScore += match.blueScore
				totalNumScores += 1
			if match.redScore > -1:
				totalScore += match.redScore
				totalNumScores += 1
		return totalScore / totalNumScores

	def numPlayedMatchesInCompetition(self):
		numPlayedMatches = 0
		for match in self.comp.matches:
			if match.redScore > -0.5 and match.blueScore > -0.5:
				numPlayedMatches += 1
		return numPlayedMatches


	def doCalculations(self, FBC):
		#team Metrics
		#if self.numPlayedMatchesInCompetition() > 0:
		for team in self.comp.teams:
			timds = self.getPlayedTIMDsForTeam(team)
			if len(timds) <= 0:
				print "No Complete TIMDs for team: " + str(team.number) + ", " + team.name
			else:
				print("Beginning calculations for team: " + str(team.number) + ", " + team.name)

				#Super Scout Averages
				
				if isinstance(team.calculatedData, {}.__class__): team.calculatedData = DataModel.CalculatedTeamData(**team.calculatedData) #We shouldnt have to do this here, it should already be done. Don't have time to figure out why right now.

				team.calculatedData.avgTorque = self.averageTIMDObjectOverMatches(team, 'rankTorque')
				team.calculatedData.avgSpeed = self.averageTIMDObjectOverMatches(team, 'rankSpeed')
				team.calculatedData.avgEvasion = self.averageTIMDObjectOverMatches(team, 'rankEvasion')
				team.calculatedData.avgDefense = self.averageTIMDObjectOverMatches(team, 'rankDefense')
				team.calculatedData.avgBallControl = self.averageTIMDObjectOverMatches(team, 'rankBallControl')
				team.calculatedData.disabledPercentage = self.percentagesOverAllTIMDs(team, 'didGetDisabled')
				team.calculatedData.incapacitatedPercentage = self.percentagesOverAllTIMDs(team, 'didGetIncapacitated')
				team.calculatedData.disfunctionalPercentage = self.disfunctionalPercentage(team)

				#Auto
				team.calculatedData.avgHighShotsAuto = self.averageTIMDObjectOverMatches(team, 'numHighShotsMadeAuto')
				team.calculatedData.avgLowShotsAuto = self.averageTIMDObjectOverMatches(team, 'numLowShotsMadeAuto')
				team.calculatedData.reachPercentage = self.percentagesOverAllTIMDs(team, 'didReachAuto')
				team.calculatedData.highShotAccuracyAuto = self.highShotAccuracy(team, True)
				team.calculatedData.lowShotAccuracyAuto = self.lowShotAccuracy(team, True)
				team.calculatedData.numAutoPoints = self.numAutoPointsForTeam(team)
				team.calculatedData.avgMidlineBallsIntakedAuto = self.avgBallsIntaked(team, 'ballsIntakedAuto')
				team.calculatedData.sdHighShotsAuto = self.standardDeviationObjectOverAllMatches(team, 'numHighShotsMadeAuto')
				team.calculatedData.sdLowShotsAuto = self.standardDeviationObjectOverAllMatches(team, 'numLowShotsMadeAuto')
				#team.calculatedData.sdMidlineBallsIntakedAuto = self.standardDeviationObjectOverAllMatches(team, 'ballsIntakedAuto')
				team.calculatedData.sdBallsKnockedOffMidlineAuto = self.standardDeviationObjectOverAllMatches(team, 'numBallsKnockedOffMidlineAuto')
				

				if isinstance(team.calculatedData, {}.__class__): team.calculatedData = DataModel.CalculatedTeamData(**team.calculatedData) #We shouldnt have to do this here, it should already be done. Don't have time to figure out why right now.


				#Tele
				team.calculatedData.challengePercentage = self.percentagesOverAllTIMDs(team, 'didChallengeTele')
				team.calculatedData.scalePercentage = self.percentagesOverAllTIMDs(team, 'didScaleTele')
				team.calculatedData.avgGroundIntakes = self.averageTIMDObjectOverMatches(team, 'numGroundIntakesTele')
				team.calculatedData.avgBallsKnockedOffMidlineAuto = self.averageTIMDObjectOverMatches(team, 'numBallsKnockedOffMidlineAuto')
				team.calculatedData.avgShotsBlocked = self.averageTIMDObjectOverMatches(team, 'numShotsBlockedTele')
				team.calculatedData.avgHighShotsTele = self.averageTIMDObjectOverMatches(team, 'numHighShotsMadeTele')
				
				#dddd
				team.calculatedData.avgLowShotsTele = self.averageTIMDObjectOverMatches(team, 'numLowShotsMadeTele')
				
				if isinstance(team.calculatedData, {}.__class__): team.calculatedData = DataModel.CalculatedTeamData(**team.calculatedData) #We shouldnt have to do this here, it should already be done. Don't have time to figure out why right now.

				team.calculatedData.highShotAccuracyTele = self.highShotAccuracy(team, False)
				
				#dddd
				team.calculatedData.lowShotAccuracyTele = self.lowShotAccuracy(team, False)

				if isinstance(team.calculatedData, {}.__class__): team.calculatedData = DataModel.CalculatedTeamData(**team.calculatedData) #We shouldnt have to do this here, it should already be done. Don't have time to figure out why right now.
				print("THE TEAM Calc: " + str(team.calculatedData))

				team.calculatedData.blockingAbility = self.blockingAbility(team)
				team.calculatedData.teleopShotAbility = self.teleopShotAbility(team)
				team.calculatedData.siegeConsistency = self.siegeConsistency(team)
				team.calculatedData.siegeAbility = self.siegeAbility(team)
				team.calculatedData.siegePower = self.siegePower(team)
				avgDefensesCrossesTele = self.averageDictionaries(self.makeArrayOfDictionaries(team, 'timesSuccessfulCrossedDefensesTele'))
				team.calculatedData.sdHighShotsTele = self.standardDeviationObjectOverAllMatches(team, 'numHighShotsMadeTele')
				team.calculatedData.sdLowShotsTele = self.standardDeviationObjectOverAllMatches(team, 'numLowShotsMadeTele')
				team.calculatedData.sdGroundIntakes = self.standardDeviationObjectOverAllMatches(team, 'numGroundIntakesTele')
				team.calculatedData.sdShotsBlocked = self.standardDeviationObjectOverAllMatches(team, 'numShotsBlockedTele')

				print "challenge% "  + str(team.calculatedData.challengePercentage)
				print "groundint "  + str(team.calculatedData.avgGroundIntakes)
				print "midintaked" + str(team.calculatedData.avgMidlineBallsIntakedAuto)
				print "avgmidlineknock "  + str(team.calculatedData.avgBallsKnockedOffMidlineAuto)
				print "avghightele "  + str(team.calculatedData.avgHighShotsTele)
				print "avglowtele "  + str(team.calculatedData.avgLowShotsTele)
				print "avglowauto "  + str(team.calculatedData.avgLowShotsAuto)
				print "avghighauto " + str(team.calculatedData.avgHighShotsAuto)
				print "highacctele "  + str(team.calculatedData.highShotAccuracyTele)
				print "lowaccauto "  + str(team.calculatedData.lowShotAccuracyAuto)
				print "telecross " + str(avgDefensesCrossesTele)
				print "shotsblocked " + str(team.calculatedData.avgShotsBlocked)


				team.calculatedData.numRPs = self.numRPsForTeam(team)
				team.calculatedData.numScaleAndChallengePoints = self.numScaleAndChallengePointsForTeam(team)
				# #team.calculatedData.predictedNumRPs = self.predictedNumberOfRPs(team)
				# print team.calculatedData.firstPickAbility
				# print self.firstPickAbility(team)
				# team.calculatedData.firstPickAbility = self.firstPickAbility(team)
				# team.calculatedData.secondPickAbility = self.secondPickAbility(team)
				# #print team.calculatedData.secondPickAbility
		# 		team.calculatedData.predictedSeed = self.getRankingForTeam(team)
		# 		FBC.addCalculatedTeamDataToFirebase(team.number, team.calculatedData)
		# 		print("Putting calculations for team " + str(team.number) + " to Firebase.")
		
		#Match Metrics
		for match in self.comp.matches:
			if isinstance(match.calculatedData, {"d":"d"}.__class__): match.calculatedData = DataModel.CalculatedTeamData(**match.calculatedData) #We shouldnt have to do this here, it should already be done. Don't have time to figure out why right now.
			match.calculatedData.predictedBlueScore = self.predictedScoreForMatch(match)['blue']
			match.calculatedData.predictedRedScore = self.predictedScoreForMatch(match)['red']
			print "\nMatch " + str(match.number) + ':' + ' Blue: ' + str(match.calculatedData.predictedBlueScore) + ' Red: ' + str(match.calculatedData.predictedRedScore) 
			numDefenseCrosses = self.numDefensesCrossedInMatch(match)
			match.calculatedData.numDefenseCrossesByBlue = numDefenseCrosses['blue']
			match.calculatedData.numDefenseCrossesByRed = numDefenseCrosses['red']
			match.calculatedData.blueRPs = self.RPsGainedFromMatch(match)['blue']
			match.calculatedData.redRPs = self.RPsGainedFromMatch(match)['red']
			#print("Putting calculations for match " + str(match.number) + " to Firebase.")


		#Competition metrics
		if self.numPlayedMatchesInCompetition() > 0:
			self.comp.averageScore = self.avgCompScore()
			

