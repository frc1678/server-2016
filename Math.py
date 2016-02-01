# Math.py
import utils
import random
import firebaseCommunicator
import math
import numpy as np

import sys, traceback


class Calculator(object):
	"""docstring for Calculator"""
	def __init__(self, competition):
		super(Calculator, self).__init__()
		self.comp = competition
		
		
	def getTeamForNumber(self, num):
		for team in self.comp.teams:
			if team.number == num:
				return team

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
		print("t: " + str(team.number))
		for timd in team.teamInMatchDatas:
			if timd.numLowShotsMissedAuto > -1:
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
			total += (team.calculatedData.averageTIMDObjectOverAllMatches(team, key) - utils.makeDictFromTIMD(timd)[key]) ** 2
		return math.sqrt(total)

	def percentagesOverAllTIMDs(self, team, key, coefficient = 1):
		 timds = self.getPlayedTIMDsForTeam(team)
		 if len(timds) == 0:
			return -1
		 conditionTrueCounter = 0
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
		totalHighShotsMade = 0
		totalHighShotsMissed = 0
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
			if totalHighShotsMade + totalHighShotsMissed == 0:
				return 0
			else:
				return totalHighShotsMade / (totalHighShotsMade + totalHighShotsMissed)

	def lowShotAccuracy(self, team, auto):
		timds = self.getPlayedTIMDsForTeam(team)
		if len(timds) == 0:
			return -1
		totalLowShotsMade = 0
		totalLowShotsMissed = 0
		if auto:
			for timd in timds:
				if timd.numHighShotsMadeAuto > -1 or timd.numHighShotsMissedAuto > -1:
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

	def makeArrayOfArrays(self, team, key):
		timds = self.getPlayedTIMDsForTeam(team)
		arrayOfArrays = []
		for timd in timds:
			array = utils.makeDictFromTIMD(timd)[key]
			if array[0] > -1:
				arrayOfArrays.append(array)
		return arrayOfArrays				

	def averageArrays(self, arrays):
		if arrays == -1: # we will return a -1 from makeArrayOfArrays if there are no played timds.
			return [-1]
		outputArray = []
		numPlayed = 0
		for array in arrays:	
			if array[0] > -1:
				numPlayed += 1
		for index in range(0, len(arrays[0]) - 1):	#Add all same indexes of all array (add all array[0]s, all array[1]s, ...)
			totalForIndex = 0
			for array in arrays:
				if array[0] > -1:
					totalForIndex += array[index]
				outputArray.append(totalForIndex/numPlayed)
		return outputArray

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
 			if dictionary['rt'] > -1:
 				arrayOfDictionaries.append(dictionary) 
 		return arrayOfDictionaries 


 	def averageDictionaries(self, array):
 		outputDict = {}
 		for dictionary in array:
 			for key, value in dictionary.items():
 				subOutputDict = {}
 				for key, value in value.items():
 					avg = 0
 					for v in eval(str(value)):
 						avg += float(v)
 					avg /= len(value)
 					subOutputDict[key] = avg
 				outputDict[key] = subOutputDict
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

	def teleopShotAbility(self, team): return (5 * team.calculatedData.avgHighShotsTele + 2 * team.calculatedData.avgLowShotsTele)

	def siegeAbility(self, team): return (15 * team.calculatedData.scalePercentage + 5 * team.calculatedData.challengePercentage)

	def siegeConsistency(self, team): return (team.calculatedData.scalePercentage + team.calculatedData.challengePercentage)

	def siegePower(self, team): return (team.calculatedData.siegeConsistency * team.calculatedData.siegeAbility)

	def numAutoPointsForTIMD(self, timd):
		defenseCrossesInAuto = 0
		for value in timd.timesCrossedDefensesAuto.values():
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

	def totalAvgDefenseCategoryCrossingsForAlliance(self, alliance, key, defenseCategory):
		totalAvgDefenseCategoryCrossings = 0
		for team in alliance:
			totalAvgDefenseCategoryCrossings += self.avgDefenseCategoryCrossingsForTeam(team, key, defenseCategory)
		return totalAvgDefenseCategoryCrossings / 3

	def avgDefenseCategoryCrossingsForTeam(self, team, key, defenseCategory):	#Use in standard deviation calculation for each defenseCategory
		category = utils.makeDictFromTeam(team)["calculatedData"][key][defenseCategory].values()
		total = 0
		for value in category:
			total += len(value)
		return total / len(category)
		

	def stanDevSumForDefenseCategory(self, alliance, defenseCategory):
		varianceValues = []			#add variance for each data point to array
		stanDevSum = 0

		for team in alliance:
			timds = self.getPlayedTIMDsForTeam(team)
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
		return 5 * team.calculatedData.challengePercentage * self.getPlayedTIMDsForTeam(team) + 15 * team.calculatedData.scalePercentage * self.getPlayedTIMDsForTeam(team)

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
		return 5 * team.calculatedData.avgHighShotsTele + 10 * team.calculatedData.avgHighShotsAuto + 5 * team.calculatedData.avgLowShotsAuto + 2 * team.calculatedData.avgLowShotsTele
	
	def totalAvgNumShotsForAlliance(self, alliance):
		totalAvgNumShots = 0
		for team in alliance:
			totalAvgNumShots += team.calculatedData.avgHighShotsAuto + team.calculatedData.avgHighShotsTele + team.calculatedData.avgLowShotsTele + team.calculatedData.avgLowShotsAuto
		return totalAvgNumShots	

	def highShotAccuracyForAlliance(self, alliance):
		overallHighShotAccuracy = 0
		for team in alliance:
			overallHighShotAccuracy += team.calculatedData.highShotAccuracy
		return overallHighShotAccuracy / 3

	def blockedShotPointsForAlliance(self, alliance, opposingAlliance):
		blockedShotPoints = 0
		for team in opposingAlliance:
			blockedShotPoints += (self.highShotAccuracyForAlliance(alliance) * team.calculatedData.avgShotsBlocked)
		return 5 * blockedShotPoints

	def reachPointsForAlliance(self, alliance):
		reachPoints = 0
		for team in alliance:
			reachPoints += 2 * team.calculatedData.reachPercentage
		return reachPoints

	def calculatePercentage(self, x, u, o):
		return (1 / (math.sqrt(2 * math.pi ) * o) * (math.e)**(-1.0 * ((x - u)**2) / (2 * o**2))) #calculate percentage of a breach or capture 

	def sumOfStandardDeviationsOfShotsForAlliance(self, alliance):
		sumOfStandardDeviationsOfShotsForAlliance = 0
		shotVariances = []
		for team in alliance:
			autoHighShotVariance = 0
			autoLowShotVariance = 0
			teleHighShotVariance = 0
			teleLowShotVariance = 0
			timds = self.getPlayedTIMDsForTeam(team)
			if len(timds) == 0 and team.number == 1678:
				return("1678 has insufficient data")
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

		for team in blueTeams:
			productOfScaleAndChallengePercentages *= (team.calculatedData.scalePercentage + team.calculatedData.challengePercentage)
		predictedScoreForMatch['blue']['RPs'] += (self.calculatePercentage(8.0, self.totalAvgNumShotsForAlliance(blueTeams), self.sumOfStandardDeviationsOfShotsForAlliance(blueTeams)) * productOfScaleAndChallengePercentages)
		
		breachPercentage = 1

		for defenseCategory in blueTeams[0].calculatedData.avgDefenseCrossingEffectiveness:
			standardDevCategories.append(self.stanDevSumForDefenseCategory(blueTeams, defenseCategory))
		standardDevCategories = sorted(standardDevCategories)	#Sort the array of standard deviations for defense categories

		for category in range(1, len(standardDevCategories) + 1):	#Use the max 4 to calculate percentage
			breachPercentage *= calculatePercentage(2.0, totalAvgDefenseCategoryCrossingsForAlliance(blueTeams, category), stanDevSumForDefenseCategory(blueTeams, category))


		predictedScoreForMatch['blue']['RPs'] += breachPercentage

		# Red Alliance Next
		totalAvgNumShots = 0
		redTeams = []
		for teamNumber in match.blueAllianceTeamNumbers:
			team = self.getTeamForNumber(teamNumber)
			redTeams.append(team)
			predictedScoreForMatch['red']['score'] += self.totalAvgNumShotPointsForTeam(team)
		
		blueTeams = []
		for teamNumber in match.redAllianceTeamNumbers:
			blueTeams.append(self.getTeamForNumber(teamNumber))
		
		predictedScoreForMatch['red']['score'] -= self.blockedShotPointsForAlliance(redTeams, blueTeams)
		predictedScoreForMatch['red']['score'] += self.reachPointsForAlliance(redTeams)
		productOfScaleAndChallengePercentages = 1

		standardDevCategories = []

		for team in redTeams:	#Find chance of a capture, award that many RPs
			productOfScaleAndChallengePercentages *= (team.calculatedData.scalePercentage + team.calculatedData.challengePercentage)

		predictedScoreForMatch['red']['RPs'] += (self.calculatePercentage(8.0, self.totalAvgNumShotsForAlliance(redTeams), self.sumOfStandardDeviationsOfShotsForAlliance(redTeams) * productOfScaleAndChallengePercentages))
		
		breachPercentage = 1
								#Using a dictionary already sorted by category to loop through the defense categories
		for defenseCategory in redTeams[0].calculatedData.avgDefenseCrossingEffectiveness:	#Find chance of a breach, award that many RPs
			standardDevCategories.append(self.stanDevSumForDefenseCategory(redTeams, defenseCategory))	#Add standard deviation of crosses per category to array
		standardDevCategories = sorted(standardDevCategories)

		for category in range(1, len(standardDevCategories) + 1):	#Sort and calculate breach chance using max 4 categories
			breachPercentage *= calculatePercentage(2.0, totalAvgDefenseCategoryCrossingsForAlliance(redTeams, category), stanDevSumForDefenseCategory(redTeams, category))


		predictedScoreForMatch['red']['RPs'] += breachPercentage


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


	def predictedSeeding(self):
		teamsArray = []
		for team in self.comp.teams:
			teamsArray.append(team)
		for team in range(len(teamsArray), 0, -1):
			for i in range(team):
				if teamsArray[i].calculatedData.predictedNumberOfRPs > teamsArray[i + 1].calculatedData.predictedNumberOfRPs:
					temp = teamsArray[i]
					teamsArray[i] = teamsArray[i + 1]
					teamsArray[i + 1] = temp
		return teamsArray
	
	def predictedScoreCustomAlliance(self, alliance):
		predictedScoreCustomAlliance = 0		

		predictedScoreCustomAlliance += self.reachPointsForAlliance(alliance)
		productOfScaleAndChallengePercentages = 1

		standardDevCategories = []
		print ("v" + str(self.calculatePercentage(2.0,1.0,3.0)))

		
		sdSum = self.sumOfStandardDeviationsOfShotsForAlliance(alliance)
		if sdSum == "1678 has insufficient data":
			return -1
		for team in alliance:
			productOfScaleAndChallengePercentages *= (team.calculatedData.scalePercentage + team.calculatedData.challengePercentage)
		predictedScoreCustomAlliance += 25 * self.calculatePercentage(8.0, self.totalAvgNumShotsForAlliance(alliance), sdSum) * productOfScaleAndChallengePercentages
		breachPercentage = 1

		for defenseCategory in alliance[0].calculatedData.avgSuccessfulTimesCrossedDefensesAuto:
			standardDevCategories.append(self.stanDevSumForDefenseCategory(alliance, defenseCategory))
		standardDevCategories = sorted(standardDevCategories)

		for category in range(1, len(standardDevCategories) + 1):
			breachPercentage *= self.calculatePercentage(2.0, self.totalAvgDefenseCategoryCrossingsForAlliance(alliance, category), self.stanDevSumForDefenseCategory(alliance, category))


		predictedScoreCustomAlliance += 20 * breachPercentage

		return predictedScoreCustomAlliance


	def firstPickAbility(self, team):
		citrusC = self.getTeamForNumber(1678)
		alliance = [citrusC, team]
		return self.predictedScoreCustomAlliance(alliance) 

	
	def secondPickAbility(self, team):
		gamma = 0.5
		matrixOfMatches = np.zeros((len(self.comp.teams), len(self.comp.teams)))
		print matrixOfMatches
		teamsArray = []
		secondPickAbility = {}
		citrusC = self.getTeamForNumber(1678)
		for team1 in self.comp.teams:	#Create an array where the values correspond to how many matches two teams played together in the same alliance
			teamsArray.append(team1)
			for team2 in self.comp.teams:
				occurrence = 0
				for match in self.comp.matches:
					if (team1.number in match.blueAllianceTeamNumbers and team2.number in match.blueAllianceTeamNumbers) or (team1.number in match.redAllianceTeamNumbers and team2.number in match.redAllianceTeamNumbers):
						occurrence += 1
				matrixOfMatches[self.comp.teams.index(team1), self.comp.teams.index(team2)] = occurrence

		# Create an array where the values correspond to how many matches two teams played together in the same alliance, and then shape it into a matrix
	
		inverseMatrixOfMatchOccurrences = np.linalg.inv(matrixOfMatches)	#Find the inverse of the matrix
		teamDeltas = np.array([])
		oppositionPredictedScore = 0
		oppositionActualScore = 0
		for team1 in self.comp.teams:
			oppositionPredictedScore = 0
			oppositionActualScore = 0
			for match in self.team.matches:
				if team1.number in match.blueAllianceTeamNumbers:
					oppositionPredictedScore += match.calculatedData.predictedRedScore  
					oppositionActualScore += match.redScore
				elif team1.number in match.redAllianceTeamNumbers:
					oppositionPredictedScore += match.calculatedData.predictedBlueScore
					oppositionActualScore += match.blueScore
			teamDelta = oppositionPredictedScore - oppositionActualScore
			teamDeltas = np.append(teamDeltas, teamDelta)	#Calculate delta of each team (delta(team) = sum of predicted scores - sum of actual scores)
		teamDeltas.shape = (len(self.comp.teams), 1)	#Shape into a 1x(number of teams) matrix
		citrusDPRMatrix = np.multiply(inverseMatrixOfMatchOccurrences, teamDeltas)	#Multiply deltas matrix by InverseMatchOccurrences matrix to get citrusDPR

		for team1 in teamsArray:
			if team1.number != 1678 and team1.number != team.number:	#Loop through all of the teams and find the score contribution of the team whose
				citrusDPR = citrusDPRMatrix[teamsArray.index(team1)]	#second pick ability you are calculating for
				alliance3Robots = [citrusC, team, team1]				
				alliance2Robots = [citrusC, team1]
				scoreContribution = predictedScoreCustomAlliance(alliance3Robots) - predictedScoreCustomAlliance(alliance2Robots)
				secondPickAbility[team1.number] = gamma * scoreContribution * (1 - gamma) * citrusDPR		#gamma is a constant

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
			if match.redScore > -1 and match.blueScore > -1:
				numPlayedMatches += 1
		return numPlayedMatches


	def doCalculations(self, FBC):
		#team Metrics
		if self.numPlayedMatchesInCompetition() > 0:
			for team in self.comp.teams:
				timds = self.getPlayedTIMDsForTeam(team)
				if len(timds) <= 0:
					print "No Complete TIMDs for team: " + str(team.number) + ", " + team.name
				else:
					print("Beginning calculations for " + team.name)

					#Super Scout Averages
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
					team.calculatedData.avgMidlineBallsIntakedAuto = self.averageArrays(self.makeArrayOfArrays(team, 'ballsIntakedAuto'))
					team.calculatedData.numAutoPoints = self.numAutoPointsForTeam(team)
					avgDefenseCrossesAuto = self.averageDictionaries(self.makeArrayOfDictionaries(team, 'timesCrossedDefensesAuto'))

					#Tele
					team.calculatedData.challengePercentage = self.percentagesOverAllTIMDs(team, 'didChallengeTele')
					team.calculatedData.scalePercentage = self.percentagesOverAllTIMDs(team, 'didScaleTele')
					team.calculatedData.avgGroundIntakes = self.averageTIMDObjectOverMatches(team, 'numGroundIntakesTele')
					team.calculatedData.avgBallsKnockedOffMidlineAuto = self.averageTIMDObjectOverMatches(team, 'numBallsKnockedOffMidlineAuto')
					team.calculatedData.avgShotsBlocked = self.averageTIMDObjectOverMatches(team, 'numShotsBlockedTele')
					team.calculatedData.avgHighShotsTele = self.averageTIMDObjectOverMatches(team, 'numHighShotsMadeTele')
					team.calculatedData.avgLowShotsTele = self.averageTIMDObjectOverMatches(team, 'numLowShotsMadeTele')
					team.calculatedData.highShotAccuracyTele = self.highShotAccuracy(team, False)
					team.calculatedData.lowShotAccuracyTele = self.lowShotAccuracy(team, False)
					team.calculatedData.blockingAbility = self.blockingAbility(team)
					team.calculatedData.teleopShotAbility = self.teleopShotAbility(team)
					team.calculatedData.siegeConsistency = self.siegeConsistency(team)
					team.calculatedData.siegeAbility = self.siegeAbility(team)
					team.calculatedData.siegePower = self.siegePower(team)
					avgDefensesCrossesTele = self.averageDictionaries(self.makeArrayOfDictionaries(team, 'timesSuccessfulCrossedDefensesTele'))
					

					team.calculatedData.numRPs = self.numRPsForTeam(team)
					team.calculatedData.numScaleAndChallengePoints = self.numScaleAndChallengePointsForTeam(team)

					team.calculatedData.firstPickAbility = self.firstPickAbility(team)
					team.calculatedData.secondPickAbility = self.secondPickAbility(team)

					FBC.addCalculatedTeamDataToFirebase(team.number, team.calculatedData)
					print("Putting calculations for team " + team.number + " to Firebase.")
			
			#Match Metrics
			for match in self.comp.matches:
				numDefenseCrosses = self.numDefensesCrossedInMatch(match)
				match.calculatedData.numDefenseCrossesByBlue = numDefenseCrosses['blue']
				match.calculatedData.numDefenseCrossesByRed = numDefenseCrosses['red']
				match.calculatedData.blueRPs = self.RPsGainedFromMatch(match)['blue']
				match.calculatedData.redRPs = self.RPsGainedFromMatch(match)['red']
				print("Putting calculations for match " + str(match.number) + " to Firebase.")


			#Competition metrics
			self.comp.averageScore = self.avgCompScore()

