import utils
import numpy as np
import CacheModel as cache
import pdb
import prepFirebaseForCompetition
import TBACommunicator
# Scout Performance Analysis
class ScoutPerformance(object):
	"""docstring for ScoutPerformance"""
	def __init__(self, comp, calculator):
		super(ScoutPerformance, self).__init__()
		self.comp = comp
		self.calculator = calculator
		self.correctionalMatches = {}
		self.TBAC = TBACommunicator.TBACommunicator()
		self.scoutAccRank()

	def getCompletedTIMDsForScout(self, scout):
		return filter(lambda tm: tm.scoutName == scout, self.getCompletedTIMDsInCompetition())

	def getCompletedMatchesForScout(self, scout):
		return filter(self.calculator.matchIsCompleted, map(lambda x: self.calculator.getMatchForNumber(x.matchNumber), self.calculator.getCompletedTIMDsForScout(scout)))

	def scoutScoutedMatch(self, name, match):
		return len(filter(lambda x: x.scoutName == name, self.calculator.getTIMDsForMatchNumber(match.number))) == 1

	def scoutsOnSameAllianceInMatch(self, scout1, scout2, match):
		if not all([self.scoutScoutedMatch(scout1, match), self.scoutScoutedMatch(scout2, match)]): return False
		timds = [self.calculator.getTIMDForScoutNameAndMatch(scout1, match), self.calculator.getTIMDForScoutNameAndMatch(scout2, match)]
		alliances = [match.blueAllianceTeamNumbers, match.redAllianceTeamNumbers]
		return sum([timd.teamNumber in a for a in alliances for timd in timds]) == 2

	def getTIMDForScoutNameAndMatch(self, name, match):
		return filter(lambda x: x.scoutName == name and x.matchNumber == match.number, self.calculator.getCompletedTIMDsForScout(name))[0]


	def makeTBAMatches(self):
		func = lambda m: utils.setDictionaryValue(self.correctionalMatches, m.number, 
			self.TBAC.makeSingleMatchRequest(m.number))
		map(func, self.calculator.getCompletedMatchesInCompetition())
		
	def scoutedScoreForMatchNum(self, match, allianceIsRed):
		matchNum = match.number
		allTIMDs = self.calculator.getTIMDsForMatchNumber(matchNum)
		allianceNumbers = self.calculator.getAllianceForMatch(match, allianceIsRed)
		allianceNumbers = map(lambda t: t.number, allianceNumbers)
		allianceTIMDs = [timd for timd in allTIMDs if timd.teamNumber in allianceNumbers]

		autoPts = self.calculator.getAutoPointsForMatchForAllianceIsRed(match, allianceIsRed)

		teleShotPts = 2 * sum([(timd.numLowShotsMadeTele or 0) for timd in allianceTIMDs]) + 5 * sum([(timd.numHighShotsMadeTele or 0) for timd in allianceTIMDs])
		
		for timd in allianceTIMDs:
			s = timd.timesSuccessfulCrossedDefensesTele
			for key in self.calculator.defenseList:
				if not key in s:
					s[key] = 0
				elif s[key] == None:
					s[key] = 0
				else:
					s[key] = len(s[key])
		allDefenseCrossings = utils.dictSum(allianceTIMDs[0].timesSuccessfulCrossedDefensesTele, utils.dictSum(allianceTIMDs[1].timesSuccessfulCrossedDefensesTele, allianceTIMDs[2].timesSuccessfulCrossedDefensesTele))
		
		temp = {}
		for defense, crossings in allDefenseCrossings.items():
			if crossings > 2:
				temp[defense] = 2
			else:
				temp[defense] = crossings
		allDefenseCrossings = temp

		teleDefenseCrossPts = 5 * sum(allDefenseCrossings.values())
		
		scalePts = 15 * sum([utils.convertFirebaseBoolean(timd.didScaleTele) for timd in allianceTIMDs])
		challengePts = 5 * sum([utils.convertFirebaseBoolean(timd.didChallengeTele) for timd in allianceTIMDs])

		return autoPts + teleShotPts + teleDefenseCrossPts + scalePts + challengePts

	def scoutAccRank(self):
	        print "Analyzing Scouts..."
	        scoutScores = []
	        scoutErrByMatch = self.analyzeScouts()
	        scoutList = scoutErrByMatch.keys()
	        timesTogetherFunc = lambda s, s1: len(filter(lambda m: self.scoutsOnSameAllianceInMatch(s, s1, m), 
	            self.getCompletedMatchesForScout(s)))
	        getTeamRowFunc = lambda s: map(lambda s1: timesTogetherFunc(s, s1), scoutList)
	        matrixOfScoutMatchesTogether = np.matrix(map(getTeamRowFunc, scoutList))
	        if np.linalg.det(matrixOfScoutMatchesTogether) == 0: 
	            print "Cannot invert matrix"
	            return
	        else: inverseMatrixOfScoutMatchesTogether = np.linalg.inv(matrixOfScoutMatchesTogether)
	        errorList = map(lambda s: scoutErrByMatch[s], scoutList)
	        errorMatrix = np.matrix(errorList).reshape(len(errorList), 1)
	        scoutErrorOPRs = np.dot(inverseMatrixOfScoutMatchesTogether, errorMatrix)
	        for c in scoutList: 
	            scoutScores.append({'name' : c, 'score' : scoutErrorOPRs.item(scoutList.index(c), 0)})
	        print scoutScores
	        return scoutScores

	def analyzeScouts(self):
		scoutScoresByMatch = {}
		scoutScores = {} # Lower is better
		self.makeTBAMatches()
		TBAMatches = self.correctionalMatches
		for m in self.calculator.getCompletedMatchesInCompetition():
			redScoutedScore = self.scoutedScoreForMatchNum(m, True)
			blueScoutedScore = self.scoutedScoreForMatchNum(m, False)
			penaltyFreeRedScore = abs(m.redScore-TBAMatches[m.number]["score_breakdown"]["red"]["foulPoints"])
			penaltyFreeBlueScore = abs(m.blueScore-TBAMatches[m.number]["score_breakdown"]["blue"]["foulPoints"])
			redScoreDifference = abs(redScoutedScore-penaltyFreeRedScore)
			blueScoreDifference = abs(blueScoutedScore-penaltyFreeBlueScore)

			allTIMDs = self.calculator.getTIMDsForMatchNumber(m.number)
			redAllianceNumbers = self.calculator.getAllianceForMatch(m, True)
			redAllianceTIMDs = [timd for timd in allTIMDs if timd.teamNumber in redAllianceNumbers]
			blueAllianceNumbers = self.calculator.getAllianceForMatch(m, False)
			blueAllianceTIMDs = [timd for timd in allTIMDs if timd.teamNumber in blueAllianceNumbers]

			for timd in allTIMDs:
				si = timd.scoutName
				if not si in scoutScoresByMatch.keys(): scoutScoresByMatch[si] = []
				scoutScoresByMatch[si].append(redScoreDifference if timd in redAllianceTIMDs else blueScoreDifference)
		f = lambda s: utils.setDictionaryValue(scoutScores, s, np.mean(scoutScoresByMatch[s]))

		map(f, scoutScoresByMatch)
		print scoutScores
		return scoutScores

