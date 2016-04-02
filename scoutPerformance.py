import Math
import DataModel
import utils
import numpy as np
import prepFirebaseForCompetition

# Scout Performance Analysis
class ScoutPerformance(object):
	"""docstring for ScoutPerformance"""
	def __init__(self, comp):
		super(ScoutPerformance, self).__init__()
		self.comp = comp
		self.calculator = Math.Calculator(comp)
		self.correctionalMatches = {}

	def makeTBAMatches(self):
		func = lambda m: utils.setDictionaryValue(self.correctionalMatches, m.number, 
			prepFirebaseForCompetition.makeSingleMatchRequest(m.number))
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

	def analyzeScouts(self):
		scoutScoresByMatch = {}
		scoutScores = {} # Lower is better
		self.makeTBAMatches()
		TBAMatches = self.correctionalMatches
		for m in self.calculator.getCompletedMatchesInCompetition():
			redScoutedScore = self.scoutedScoreForMatchNum(m, True)
			blueScoutedScore = self.scoutedScoreForMatchNum(m, False)
			penaltyFreeRedScore = abs(m.redScore - TBAMatches[m.number]["score_breakdown"]["red"]["foulPoints"])
			penaltyFreeBlueScore = abs(m.blueScore - TBAMatches[m.number]["score_breakdown"]["blue"]["foulPoints"])
			redScoreDifference = abs(redScoutedScore - penaltyFreeRedScore)
			blueScoreDifference = abs(blueScoutedScore - penaltyFreeBlueScore)

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
'''SAC

Kyle: 569,
Emily: 568,
Wesley: 458,
Evan Long: 326, 
Sophia S: 442, 
Maya: 835, 
Sheela: 187,
Sam: 429,
Sage: 659,

'''
