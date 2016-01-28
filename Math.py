# Math.py
import utils
import random
import firebaseCommunicator
import math

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
		for timd in team.teamInMatchDatas:
			if timd.numLowShotsMissedAuto > -1:
				timds.append(timd)
		return timds

	def getTIMDForTeamNumberAndMatchNumber(self, teamNumber, matchNumber): # Match number is an int
		for timd in self.getTIMDsForTeamNumber(teamNumber):
			if timd.matchNumber == matchNumber:
				return timd
		return(-1)

	def getPlayedMatchesForTeam(self, team):
		matches = []
		for timd in self.getPlayedTIMDsForTeam(team):
			matches.append(self.getMatchForNumber(timd.matchNumber))

	# Calculated Team Data
	def averageTIMDObjectOverMatches(self, team, key, coefficient = 1):
		timds = self.getPlayedTIMDsForTeam(team)
		if len(timds) == 0:
			return -1
		total = 0.0
		for timd in timds:
			 total = total + utils.makeDictFromTIMD(timd)[key]
		return total/len(timds)

	def standardDeviationObjectOverAllMatches(self, team, key):
		timds = self.getPlayedTIMDsForTeam(team)
		if len(timds) == 0:
			return -1
		total = 0.0
		for timd in timds:
			total += (team.calculatedData.averageTIMDObjectOverAllMatches(team, key) - utils.makeDictFromTIMD(key)) ** 2
		return math.sqrt(total)

	def percentagesOverAllTIMDs(self, team, key, coefficient = 1):
		 timds = self.getPlayedTIMDsForTeam(team)
		 if len(timds) == 0:
			return -1
		 conditionTrueCounter = 0
		 for timd in timds:
			if utils.makeDictFromTIMD(timd)[key] == True:
				conditionTrueCounter = conditionTrueCounter + 1
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

	def averageArrays(self, arrays):
		if arrays == -1: # we will return a -1 from makeArrayOfArrays if there are no played timds.
			return [-1]
		outputArray = []
		numPlayed = 0
		for array in arrays:
			if array[0] > -1:
				numPlayed += 1
		for index in range(0, len(arrays[0]) - 1):
			totalForIndex = 0
			for array in arrays:
				if array[0] > -1:
					totalForIndex += array[index]
				outputArray.append(totalForIndex/numPlayed)
		return outputArray

	def averageDictionaries(self, array):
		if array == -1:
			return -1
		outputArray = []
		numPlayed = 0
		for dictionary in array:
			if dictionary[0] > -1:
				numPlayed += 1
		for key in dictionary:
			totalForKey = 0
			for dictionary in array:
				if dictionary[key] > -1:
					totalForKey += dictionary[key]
				outputArray.append(totalForKey/numPlayed)
		return totalForKey

	def makeArrayOfArrays(self, team, key):
		timds = self.getPlayedTIMDsForTeam(team)
		arrayOfArrays = []
		if len(timds) == 0:
			return -1
		for timd in timds:
			array = utils.makeDictFromTIMD(timd)[key]
			if array[0] > -1:
				arrayOfArrays.append(array)
		return arrayOfArrays

	def makeArrayOfDictionaries(self, team, key): 
				timds = self.getPlayedTIMDsForTeam(team)
				arrayOfDictionaries = [] 
				if len(timds) == 0:
					return -1
				for timd in timds:
					dictionary = utils.makeDictFromTIMD(timd)[key]
					if dictionary[0] > -1:
						arrayOfDictionaries.append(dictionary) 
				return arrayOfDictionaries 


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
		for value in timd.timesDefensesCrossedAuto.values():
					if value > -1:
						defenseCrossesInAuto += 1
		if defenseCrossesInAuto > 1: print "ERROR: Num Auto Points From Defenses Is Too High."
		return 10 * timd.numHighShotsMadeAuto + 5 * timd.numLowShotsMadeAuto + 2 * timd.didReachAuto + 10 * defenseCrossesInAuto

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
		totalCrossesForCategory = 0
		numberOfDataPointsInCategory = 0
		for team in alliance:
			for defense in defenseCategory:
				numberOfDataPointsInCategory += 1
				totalCrossesForCategory += team.calculatedData.avgTimesCrossedDefensesAuto[defenseCategory][defense] + team.calculatedData.avgTimesCrossedDefensesTele[defenseCategory][defense]
		return totalCrossesForCategory

	def stanDevSumForDefenseCategory(self, alliance, defenseCategory):
		varianceValues = []			#add variance  for each data point to array
		stanDevSum = 0
		for team in alliance:
			difOfAvgSquaresTele = 0
			difOfAvgSquaresAuto = 0 
			timds = getPlayedTIMDsForTeam(team)
			for timd in timds:
				for defense in defenseCategory:
					difOfAvgSquaresTele += (team.calculatedData.avgTimesCrossedDefensesTele[defenseCategory][defense] - timd.timesDefensesCrossedTele[defenseCategory][defense])**2 
					difOfAvgSquaresAuto += (team.calculatedData.avgTimesCrossedDefensesAuto[defenseCategory][defense] - timd.timesDefensesCrossedAuto[defenseCategory][defense])**2 
			difOfAvgSquaresTele /= (len(timds) - 1)			#divide difference from average squared by n - 1
			difOfAvgSquaresAuto /= (len(timds) - 1)
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
		return (1 / (math.sqrt(2 * math.pi ) * o)) * (math.e)**(-1.0 * ((x - u)**2) / (2 * o**2))

	def sumOfStandardDeviationsOfShotsForAlliance(self, alliance):
		sumOfStandardDeviationsOfShotsForAlliance = 0
		shotVariances = []
		for team in alliance:
			autoHighShotVariance = 0
			autoLowShotVariance = 0
			teleHighShotVariance = 0
			teleleLowShotVariance = 0
			timds = getPlayedTIMDsForTeam(team)
			for timd in timds:
				if timd.numHighShotsMadeAuto > -1:
					autoHighShotVariance += (team.calculatedData.avgHighShotsAuto - timd.numHighShotsMadeAuto)**2
					autoLowShotVariance += (team.calculatedData.avgLowShotsAuto - timd.numLowShotsMadeAuto)**2
					teleHighShotLowance += (team.calculatedData.avgHighShotsTele - timd.numHighShotsMadeTele)**2
					teleLowShotVariance += (team.calculatedData.avgLowShotsTele - timd.numLowShotsMadeTele)**2
			autoHighShotVariance /= (len(timds) - 1)
			autoLowShotVariance /= (len(timds) - 1)
			teleHighShotVariance /= (len(timds) - 1)
			teleLowShotVariance /= (len(timds) - 1)
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
		
		if self.totalAvgNumShotsForAlliance(blueTeams) >= 8: 
			challengeAndScale = 1
			a = 0
			for team in blueTeams:
				predictedScoreForMatch['blue']['score'] += self.totalAvgNumShotPointsForTeam(team)
				a += 10 * team.calculatedData.avgTimesCrossedDefensesAuto
				challengeAndScale *= team.calculatedData.challengePercentage + team.calculatedData.scalePercentage
			predictedScoreForMatch['blue']['score'] += 25 * challengeAndScale
			predictedScoreForMatch['blue']['score'] += a
		

		crossings = self.createCrossingsArray(alliance, a)

		redTeams = []
		for teamNumber in match.redAllianceTeamNumbers:
			redTeams.append(self.getTeamForNumber(teamNumber))
		
		predictedScoreForMatch['blue']['score'] -= self.blockedShotPointsForAlliance(blueTeams, redTeams)
		predictedScoreForMatch['blue']['score'] += self.reachPointsForAlliance(blueTeams)
		productOfScaleAndChallengePercentages = 1

		standardDevCategories = []

		for team in blueTeams:
			productOfScaleAndChallengePercentages *= (team.calculatedData.scalePercentage + team.calculatedData.challengePercentage)
		predictedScoreForMatch['blue']['RPs'] += (self.calculatePercentage(8.0, self.totalAvgNumShotsForAlliance(blueTeams), self.varianceOfShotsForAlliance(blueTeams)) * productOfScaleAndChallengePercentages)
		
		breachPercentage = 1

		for defenseCategory in blueTeams[0].calculatedData.avgDefenseCrossingEffectiveness:
			standardDevCategories.append(self.stanDevSumForDefenseCategory(blueTeams, defenseCategory))
		standardDevCategories = sorted(standardDevCategories)

		for category in range(1, len(standardDevCategories) + 1):
			breachPercentage *= calculatePercentage(2.0, totalAvgDefenseCategoryCrossingsForAlliance(blueTeams, category), stanDevSumForDefenseCategory(blueTeams, category))


		predictedScoreForMatch['blue']['RPs'] += breachPercentage
		# Red Alliance Next
		'''totalAvgNumShots = 0
		redTeams = []
		for teamNumber in match.redAllianceTeamNumbers:
			team = self.getTeamForNumber(teamNumber)
			redTeams.append(team)
			predictedScoreForMatch['red'] += self.totalAvgNumShotPointsForTeam(team)
		if self.totalAvgNumShotsForAlliance(redTeams) >= 8: 
			challengeAndScale = 1
			a = 0
			for team in redTeams:
				predictedScoreForMatch['red'] += self.totalAvgNumShotPointsForTeam(team)
				a += 10 * team.calculatedData.avgTimesCrossedDefensesAuto
				challengeAndScale *= team.calculatedData.challengePercentage + team.calculatedData.scalePercentage
			predictedScoreForMatch['red'] += 25 * challengeAndScale
			predictedScoreForMatch['red'] += a
		if self.sumOf4SmallestBetas(redTeams, a) < 135: predictedScoreForMatch['red'] += 20

		crossings = self.createCrossingsArray(alliance, a)

		blueTeams = []
		for teamNumber in match.blueAllianceTeamNumbers:
			blueTeams.append(self.getTeamForNumber(teamNumber))
		for defenseCategory in crossings:
			if timeUsed > 135:
				break
			timeUsed += crossings.pop(0)
			predictedScoreForMatch['red'] += 5
		
		predictedScoreForMatch['red'] -= self.blockedShotPointsForAlliance(redTeams, blueTeams)
		predictedScoreForMatch['red'] += self.reachPointsForAlliance(redTeams)'''


		return predictedScoreForMatch

		

	def didBreachInMatch(self, match):
		didBreach = {'red': False, 'blue': False}
		if match.numDefenseCrossesByBlue >= 8:
			didBreach['blue'] = True
		if match.numDefenseCrossesByRed >= 8:
			didBreach['red'] = True
		return didBreach


	def breachPercentage(self, team):
		breachPercentage = 0
		for match in self.team.matches:
			if team.number in match.blueAllianceTeamNumbers and match.blueScore != -1:
				if didBreachInMatch(match)['blue'] == True:
					breachPercentage += 1
			elif team.number in match.redAllianceTeamNumbers and match.blueScore != -1:
				if didBreachInMatch(match)['red'] == True:
					breachPercentage += 1
		return breachPercentage/len(self.team.matches)


	def numDefensesCrossedInMatch(self, match):
		numDefensesCrossedInMatch = {'red': -1, 'blue': -1}
		blueAllianceCrosses = 0
		for teamNum in match.blueAllianceTeamNumbers:
			for timd in self.getTIMDForTeamNumberAndMatchNumber(teamNum, match.number):
				for value in timd.timesDefensesCrossedAuto.values():
					if value > -1:
						blueAllianceCrosses += 1
				for value in timd.timesDefensesCrossedTele.values():
					if value > -1:
						blueAllianceCrosses += value
		numDefensesCrossedInMatch['blue'] = blueAllianceCrosses
		redAllianceCrosses = 0
		for teamNum in match.redAllianceTeamNumbers:
			for timd in self.getTIMDForTeamNumberAndMatchNumber(teamNum, match.number):
				for value in timd.timesDefensesCrossedAuto.values():
					if value > -1:
						redAllianceCrosses += 1
				for value in timd.timesDefensesCrossedTele.values():
					if value > -1:
						redAllianceCrosses += value
		numDefensesCrossedInMatch['red'] = redAllianceCrosses

		return numDefensesCrossedInMatch


	def predictedNumberOfRPs(self, team):
		totalRPForTeam = 0
		overallChallengeAndScalePercentage = 0
		overallBreachPercentage = 0
		matchesToBePlayedCounter = 0

		for match in self.comp.matches:		
			if team.number in match.redAllianceTeamNumbers and match.redScore == -1:
				matchesToBePlayedCounter += 1
				for teamNumber in match.blueAllianceTeamNumbers:
					team = self.getTeamForNumber(teamNumber)
					overallChallengeAndScalePercentage += team.calculatedData.challengePercentage + team.calculatedData.scalePercentage
					overallBreachPercentage += team.calculatedData.breachPercentage

				if self.calculatedData.predictedScoreForMatch(match)['red'] > self.calculatedData.predictedScoreForMatch(match)['blue']:
					totalRPForTeam += 2
				elif self.calculatedData.predictedScoreForMatch(match)['red'] == self.calculatedData.predictedScoreForMatch(match)['blue']:
					totalRPForTeam += 1

				if totalChallengeAndScalePercentage > randomNum:
					totalRPsForTeam += 1
				if totalBreachPercentage > randomNum:
					totalRPForTeam += 1


			elif team.number in match.blueAllianceTeamNumbers and match.blueScore == -1:
				matchesToBePlayedCounter += 1
				for teamNumber in match.blueAllianceTeamNumbers:
					team = self.getTeamForNumber(teamNumber)
					overallChallengeAndScalePercentage += team.calculatedData.challengePercentage + team.calculatedData.scalePercentage
					overallBreachPercentage += team.calculatedData.breachPercentage

				if self.calculatedData.predictedScoreForMatch(match)['blue'] > self.calculatedData.predictedScoreForMatch(match)['red']:
					totalRPForTeam += 2
				elif self.calculatedData.predictedScoreForMatch(match)['red'] == self.calculatedData.predictedScoreForMatch(match)['blue']:
					totalRPForTeam += 1

			else:
				print 'This team does not exist or all matches have been played'

		totalRPForTeam += (overallChallengeAndScalePercentage / 3)
		totalRPForTeam += (overallBreachPercentage / 3)

		return totalRPForTeam + numRPsForTeam(team)


	def predictedSeeding(self, competition):
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
	
	def predictedScoreTwoTeams(self, team1, team):
		firstPickTeams = []
		for team in self.comp.teams:
			if team.number != 1678:
				firstPickTeams.append(team)





	def firstPickAbility(self, competition):
		teamsArray = []
		for team in self.comp.teams:
			teamsArray.append(team)

	


	def RPsGainedFromMatch(self, match):
		blueRPs = 0
		redRPs = 0
		if match.blueScore > match.redScore: blueRPs += 2
		elif match.redScore > match.blueScore: redRPs += 2
		else:
			blueRPs += 1
			redRPs += 1

		didBreach = self.didBreachInMatch(match)
		if didBreach['blue']: blueRPs += 1
		if didBreach['red']: redRPs += 1

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


	def doCalculations(self, FBC):
		#team Metrics
		if self.numPlayedMatchesInCompetition() > 0:
			for team in self.comp.teams:
				timds = self.getPlayedTIMDsForTeam(team)
				if len(timds) <= 0:
					print "No Complete TIMDs for team:" + str(team.number) + ", " + team.name
				else:
					#Super Scout Averages
					team.calculatedData.avgTorque = self.averageTIMDObjectOverMatches(team, 'rankTorque')
					team.calculatedData.avgSpeed = self.averageTIMDObjectOverMatches(team, 'rankSpeed')
					team.calculatedData.avgEvasion = self.averageTIMDObjectOverMatches(team, 'rankEvasion')
					team.calculatedData.avgDefense = self.averageTIMDObjectOverMatches(team, 'rankDefense')
					team.calculatedData.avgBallControl = self.averageTIMDObjectOverMatches(team, 'rankBallControl')
					team.calculatedData.disabledPercentage = self.percentagesOverAllTIMDs(team, 'didGetDisabled')
					team.calculatedData.incapacitatedPercentage = self.percentagesOverAllTIMDs(team, 'didGetIncapacitated')
					team.calculatedData.disfunctionalPercentage = self.disfunctionalPercentage(team)
					team.calculatedData.avgDefenseCrossingEffectiveness = self.averageDictionaries(team, 'rankDefenseCrossingEffectiveness')

					#Auto
					team.calculatedData.avgHighShotsAuto = self.averageTIMDObjectOverMatches(team, 'numHighShotsMadeAuto')
					team.calculatedData.avgLowShotsAuto = self.averageTIMDObjectOverMatches(team, 'numLowShotsMadeAuto')
					team.calculatedData.reachPercentage = self.percentagesOverAllTIMDs(team, 'didReachAuto')
					team.calculatedData.highShotAccuracyAuto = self.highShotAccuracy(team, True)
					team.calculatedData.lowShotAccuracyAuto = self.lowShotAccuracy(team, True)
					team.calculatedData.avgMidlineBallsIntakedAuto = self.averageArrays(self.makeArrayOfArrays(team, 'ballsIntakedAuto'))
					team.calculatedData.numAutoPoints = self.numAutoPointsForTeam(team)
					team.calculatedData.sdHighShotsAuto = self.standardDeviationObjectOverAllMatches(team, 'numHighShotsMadeAuto')
					team.calculatedData.sdLowShotsAuto = self.standardDeviationObjectOverAllMatches(team, 'numLowShotsMadeAuto')
					team.calculatedData.sdMidlineBallsIntakedAuto = self.standardDeviationObjectOverAllMatches(team, 'ballsIntakedAuto')
					team.calculatedData.sdBallsKnockedOffMidlineAuto = self.standardDeviationObjectOverAllMatches(team, 'numBallsKnockedOffMidlineAutob')
					

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
					team.calculatedData.sdHighShotsTele = self.standardDeviationObjectOverAllMatches(team, 'numHighShotsMadeTele')
					team.calculatedData.sdLowShotsTele = self.standardDeviationObjectOverAllMatches(team, 'numLowShotsMadeTele')
					team.calculatedData.sdShotsBlocked = self.standardDeviationObjectOverAllMatches(team, 'numShotsBlockedTele')
					team.calculatedData.sdGroundIntakes = self.standardDeviationObjectOverAllMatches(team, 'numGroundIntakesTele')
					

					team.calculatedData.numRPs = self.numRPsForTeam(team)
					team.calculatedData.numScaleAndChallengePoints = self.numScaleAndChallengePointsForTeam(team)

					FBC.addCalculatedTeamDataToFirebase(team.number, team.calculatedData)
			
			#Match Metrics
			for match in self.comp.matches:
				numDefenseCrosses = self.numDefensesCrossedInMatch(match)
				match.calculatedData.numDefenseCrossesByBlue = numDefenseCrosses['blue']
				match.calculatedData.numDefenseCrossesByRed = numDefenseCrosses['red']
				match.calculatedData.blueRPs = self.RPsGainedFromMatch(match)['blue']
				match.calculatedData.redRPs = self.RPsGainedFromMatch(match)['red']

			#Competition metrics
			self.comp.averageScore = self.avgCompScore()

