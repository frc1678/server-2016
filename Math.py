# Math.py
import utils
import firebaseCommunicator

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

	# Calculated Team Data
	def averageTIMDObjectOverMatches(self, team, key, coefficient = 1):
		timds = self.getPlayedTIMDsForTeam(team)
		if len(timds) == 0:
			return -1
		total = 0.0
		for timd in timds:
			 total = total + utils.makeDictFromTIMD(timd)[key]
		return total/len(timds)

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

	def averageArrays(self, arrays):
		if arrays == -1: # we will return a -1 from makeArrayOfArrays if there are no played timds.
			return [-1]
		outputArray = []
		numPlayed = 0
		for array in arrays:                          #for dictionary in array: add all values of dict key in index 0, 1, ... 
			if array[0] > -1:						  #assign each added value to bigger array, from that array take each index and divide by numPlayed
				numPlayed += 1						  #add these to another array (or just replace the existing array indices with the calculated averages) 
		for index in range(0, len(arrays[0]) - 1):
			totalForIndex = 0
			for array in arrays:
				if array[0] > -1:
					totalForIndex += array[index]
				outputArray.append(totalForIndex/numPlayed)
		return outputArray

	def makeArrayOfArrays(self, team, key): 
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

	def doCalculations(self, FBC):
		for team in self.comp.teams:
			timds = self.getPlayedTIMDsForTeam(team)
			if len(timds) <= 0:                                                                                                        
				print "No Complete TIMDs for team: " + str(team.number) + ", " + team.name
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
				team.calculatedData.avgTimesCrossedDefensesAuto = self.averageDictionaries(self.makeArrayOfDictionaries(team, 'timesDefensesCrossedAuto'))

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
				team.calculatedData.avgTimesCrossedDefensesTele = self.averageDictionaries(self.makeArrayOfDictionaries(team, 'timesDefensesCrossedTele'))


				FBC.addCalculatedTeamDataToFirebase(team.number, team.calculatedData)
				
