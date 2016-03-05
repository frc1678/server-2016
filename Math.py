import math
from operator import attrgetter
import pdb

import numpy as np
import scipy as sp
import scipy.stats as stats

import CacheModel as cache
import DataModel
import utils


class Calculator(object):
    """docstring for Calculator"""

    def __init__(self, competition):
        super(Calculator, self).__init__()
        self.comp = competition
        self.categories = ['a', 'b', 'c', 'd', 'e']
        self.ourTeamNum = 1678
        self.monteCarloIterations = 50
        self.defenseList = ['pc', 'cdf', 'mt', 'rt', 'rw', 'lb', 'rp', 'sp', 'db']
        self.defenseDictionary = {'a': ['pc', 'cdf'],
                                  'b': ['mt', 'rp'],
                                  'c': ['sp', 'db'],
                                  'd': ['rw', 'rt'],
                                  'e': ['lb']
                                  }
        self.matches = self.comp.matches
        self.TIMDs = self.comp.TIMDs
        self.cachedTeamDatas = {}
        self.averageTeam = DataModel.Team()
        self.averageTeam.number = -1
        self.cachedTeamDatas[self.averageTeam.number] = cache.CachedTeamData(**{'teamNumber': self.averageTeam.number})
        [utils.setDictionaryValue(self.cachedTeamDatas, team.number,
                                  cache.CachedTeamData(**{'teamNumber': team.number})) for team in self.comp.teams]

    def getDefenseRetrievalFunctionForDefense(self, retrievalFunction, defenseKey):
        return lambda t: retrievalFunction(t)[defenseKey]

    def getDefenseRetrievalFunctions(self, retrievalFunction):
        return map(lambda dKey: self.getDefenseRetrievalFunctionForDefense(retrievalFunction, dKey), self.defenseList)

    def getValuedDefenseRetrievalFunctionsForTeam(self, team, retrievalFunction):
        return filter(lambda f: f(team) != None, self.getDefenseRetrievalFunctions(retrievalFunction))

    # Team utility functions
    def getTeamForNumber(self, teamNumber):
        return [team for team in self.comp.teams if team.number == teamNumber][0]

    def teamsWithCalculatedData(self):
        return filter(lambda t: self.calculatedDataHasValues(t.calculatedData), self.comp.teams)

    def getMatchesForTeam(self, team):
        return [match for match in self.matches if self.teamInMatch(team, match)]

    def getCompletedMatchesForTeam(self, team):
        return filter(self.matchIsCompleted, self.getMatchesForTeam(team))

    def getPlayedTIMDsForTeam(self, team):
        return [timd for timd in self.getTIMDsForTeamNumber(team.number) if self.timdIsPlayed(timd)]

    def teamsWithMatchesCompleted(self):
        return [team for team in self.comp.teams if len(self.getCompletedTIMDsForTeam(team)) > 0]

    def getColorFromTeamAndMatch(self, team, match):
        blue = map(self.getTeamForNumber, match.blueAllianceTeamNumbers)
        red = map(self.getTeamForNumber, match.redAllianceTeamNumbers)
        return blue if team in blue else red

    def getOppColorFromTeamAndMatch(self, team, match):
        isRed = self.getTeamAllianceIsRedInMatch(team, match)
        return self.getAllianceForMatch(match, not isRed)

    def getAllTeamMatchAlliances(self, team):
        return [self.getColorFromTeamAndMatch(team, match) for match in self.getCompletedMatchesForTeam(team)]

    def getAllTeamOppositionAlliances(self, team):
        return [self.getOppColorFromTeamAndMatch(team, match) for match in self.getCompletedMatchesForTeam(team)]

    # Match utility functions
    def getMatchForNumber(self, matchNumber):
        return [match for match in self.matches if match.number == matchNumber][0]

    def teamsInMatch(self, match):
        teamNumbersInMatch = []
        teamNumbersInMatch.extend(match.redAllianceTeamNumbers)
        teamNumbersInMatch.extend(match.blueAllianceTeamNumbers)
        return [self.getTeamForNumber(teamNumber) for teamNumber in teamNumbersInMatch]

    def teamInMatch(self, team, match):
        return team in self.teamsInMatch(match)

    def matchIsPlayed(self, match):
        return match.redScore != None or match.blueScore != None

    def matchIsCompleted(self, match):
        return len(self.getCompletedTIMDsForMatchNumber(match.number)) == 6

    def getAllTIMDsForMatch(self, match):
        return [timd for timd in self.comp.TIMDs if timd.matchNumber == match.number]

    def matchHasAllTeams(self, match):
        return len(self.getAllTIMDsForMatch(match)) == 6

    # TIMD utility functions
    def getTIMDsForTeamNumber(self, teamNumber):
        if teamNumber == -1:
            return self.TIMDs
        return [timd for timd in self.comp.TIMDs if timd.teamNumber == teamNumber]

    def getCompletedTIMDsForTeamNumber(self, teamNumber):
        return filter(self.timdIsCompleted, self.getTIMDsForTeamNumber(teamNumber))

    def getCompletedTIMDsForTeam(self, team):
        return self.getCompletedTIMDsForTeamNumber(team.number)

    def getTIMDsForMatchNumber(self, matchNumber):
        return [timd for timd in self.comp.TIMDs if timd.matchNumber == matchNumber]

    def getCompletedTIMDsForMatchNumber(self, matchNumber):
        return filter(self.timdIsCompleted, self.getTIMDsForMatchNumber(matchNumber))

    def getTIMDForTeamNumberAndMatchNumber(self, teamNumber, matchNumber):
        return [timd for timd in self.getTIMDsForTeamNumber(teamNumber) if timd.matchNumber == matchNumber][0]

    def getCompletedTIMDsInCompetition(self):
        return [timd for timd in self.comp.TIMDs if self.timdIsCompleted(timd)]

    def calculatedDataHasValues(self, calculatedData):
        hasValues = False
        for key, value in utils.makeDictFromObject(calculatedData).items():
            if value != None and not 'Defense' in key and not 'defense' in key and not 'second' in key and not "ballsIntakedAuto" in key:
                hasValues = True
        return hasValues

    def timdIsPlayed(self, timd):
        isPlayed = False
        for key, value in utils.makeDictFromTIMD(timd).items():
            if value != None:
                isPlayed = True
        return isPlayed

    def teamsAreOnSameAllianceInMatch(self, team1, team2, match):
        areInSameMatch = False
        alliances = [match.redAllianceTeamNumbers, match.blueAllianceTeamNumbers]
        for alliance in alliances:
            if team1.number in alliance and team2.number in alliance:
                areInSameMatch = True
        return areInSameMatch

    exceptedKeys = ['calculatedData', 'ballsIntakedAuto', 'superNotes']

    def timdIsCompleted(self, timd):
        isCompleted = True
        for key, value in utils.makeDictFromTIMD(timd).items():
            if key not in self.exceptedKeys and value == None:
                isCompleted = False
        return isCompleted

    # Calculated Team Data
    def getAverageForDataFunctionForTeam(self, team, dataFunction):
        validTIMDs = filter(lambda timd: dataFunction(timd) != None, self.getCompletedTIMDsForTeam(team))
        return np.mean(map(dataFunction, validTIMDs))

    def getStandardDeviationForDataFunctionForTeam(self, team, dataFunction):
        return np.std(map(dataFunction, self.getCompletedTIMDsForTeam(team)))

    def getAccuracyForTIMDForMadeFunctionForMissedFunction(self, timd, madeFunction, missedFunction):
        denominator = madeFunction(timd) + missedFunction(timd)
        return (float(madeFunction(timd)) / float(denominator)) if denominator != 0 else 0

    def getTIMDHighShotAccuracyTele(self, timd):
        madeFunction = lambda t: t.numHighShotsMadeTele
        missedFunction = lambda t: t.numHighShotsMissedTele
        return self.getAccuracyForTIMDForMadeFunctionForMissedFunction(timd, madeFunction, missedFunction)

    def getTIMDLowShotAccuracyTele(self, timd):
        madeFunction = lambda t: t.numLowShotsMadeTele
        missedFunction = lambda t: t.numLowShotsMissedTele
        return self.getAccuracyForTIMDForMadeFunctionForMissedFunction(timd, madeFunction, missedFunction)

    def getTIMDHighShotAccuracyAuto(self, timd):
        madeFunction = lambda t: t.numHighShotsMadeAuto
        missedFunction = lambda t: t.numHighShotsMissedAuto
        return self.getAccuracyForTIMDForMadeFunctionForMissedFunction(timd, madeFunction, missedFunction)

    def getTIMDLowShotAccuracyAuto(self, timd):
        madeFunction = lambda t: t.numLowShotsMadeAuto
        missedFunction = lambda t: t.numLowShotsMissedAuto
        return self.getAccuracyForTIMDForMadeFunctionForMissedFunction(timd, madeFunction, missedFunction)

    def twoBallAutoAccuracy(self, team):
        timds = self.getCompletedTIMDsForTeam(team)
        twoBallAutoCompleted = 0
        for timd in timds:
            totalNumShots = timd.numHighShotsMadeAuto + timd.numLowShotsMadeAuto + timd.numHighShotsMissedAuto + timd.numLowShotsMissedAuto
            if totalNumShots > 2:
                twoBallAutoCompleted += 1
        return twoBallAutoCompleted / len(timds)

    def blockingAbility(self, team):
        avgHighShotAccuracy = sum(
            map(lambda t: t.calculatedData.highShotAccuracyTele, self.teamsWithMatchesCompleted()))
        return (5 * avgHighShotAccuracy * team.calculatedData.avgShotsBlocked) / len(
            self.teamsWithMatchesCompleted()) if len(self.getCompletedMatchesForTeam(team)) > 0 else None

    def autoAbility(self, timd):
        crossesDict = timd.timesSuccessfulCrossedDefensesAuto
        crossesDict = crossesDict if crossesDict != None else {}
        defensesCrossed = sum([np.mean(len(crossesDict[category]) if category in crossesDict else 0) for category in self.categories if crossesDict != None])
        return sum([10 * timd.numHighShotsMadeAuto,
                   5 * timd.numLowShotsMadeAuto,
                   2 * int(utils.convertFirebaseBoolean(timd.didReachAuto)),
                   10 if defensesCrossed >= 1 else 0])


    def stdDevTeleopShotAbility(self, team):
        return utils.sumStdDevs(5 * team.calculatedData.sdHighShotsTele, 2 * team.calculatedData.sdLowShotsTele)

    def siegeAbility(self, team):
        return 15 * team.calculatedData.scalePercentage + 5 * team.calculatedData.challengePercentage

    def singleSiegeAbility(self, timd):
        return (15 * utils.convertFirebaseBoolean(timd.didScaleTele) + 5 * utils.convertFirebaseBoolean(timd.didChallengeTele))

    def siegeConsistency(self, team):
        return team.calculatedData.scalePercentage + team.calculatedData.challengePercentage if team.calculatedData.scalePercentage != None and team.calculatedData.challengePercentage != None else None

    def numAutoPointsForTIMD(self, timd):
        defenseCrossesInAuto = 0
        for defense, value in timd.timesSuccessfulCrossedDefensesAuto.items():
            defenseCrossesInAuto += len(value) if value != None else 0
        if defenseCrossesInAuto > 1: defenseCrossesInAuto = 1
        return 10 * int(timd.numHighShotsMadeAuto) + 5 * int(timd.numLowShotsMadeAuto) + 2 * (
            1 if timd.didReachAuto else 0) + 10 * int(defenseCrossesInAuto)

    def numRPsForTeam(self, team):
        return sum(map(lambda m: self.RPsGainedFromMatchForTeam(m, team), self.getCompletedMatchesForTeam(team)))

    def numScaleAndChallengePointsForTeam(self, team):
        if team.calculatedData.siegeAbility != None:
            return team.calculatedData.siegeAbility * len(self.getCompletedTIMDsForTeam(team))

    def numSiegePointsForTIMD(self, timd):
        total = 0
        if timd.didChallengeTele: total += 5
        if timd.didScaleTele: total += 15
        return total

    def totalSDShotPointsForTeam(self, team):
        return 5 * team.calculatedData.sdHighShotsTele + 10 * team.calculatedData.sdHighShotsAuto + 5 * team.calculatedData.sdLowShotsAuto + 2 * team.calculatedData.sdLowShotsTele

    def shotDataPoints(self, team):
        return [team.calculatedData.avgHighShotsAuto, team.calculatedData.avgLowShotsTele,
                team.calculatedData.avgHighShotsTele, team.calculatedData.avgLowShotsAuto]

    def highShotAccuracyForAlliance(self, alliance):
        overallHighShotAccuracy = []
        [overallHighShotAccuracy.extend(
            [team.calculatedData.highShotAccuracyTele, team.calculatedData.highShotAccuracyAuto]) for team in alliance
         if team.calculatedData.highShotAccuracyAuto != None]
        return sum(overallHighShotAccuracy) / len(overallHighShotAccuracy)

    def blockedShotPointsForAlliance(self, alliance, opposingAlliance):
        blockedShotPoints = 0
        for team in opposingAlliance:
            if team.calculatedData.avgShotsBlocked != None:
                blockedShotPoints += (self.highShotAccuracyForAlliance(alliance) * team.calculatedData.avgShotsBlocked)
        return blockedShotPoints

    def probabilityDensity(self, x, mu, sigma):
        if sigma == 0.0:
            return int(x == mu)
        if x != None and mu != None and sigma != None: return stats.norm.cdf(x, mu, sigma)

    def monteCarloForMeanForStDevForValueFunction(self, mean, stDev, valueFunction):
        values = []
        if stDev == 0.0:
            return 0.0
        for i in range(self.monteCarloIterations):
            randomNumber = np.random.normal(mean, stDev)
            values.append(valueFunction(randomNumber))
        return np.std(values)

    def stdDevNumCrossingsTeleForTeamForCategory(self, team, category):
        if team.number == -1:
            pdb.set_trace()
        return utils.rms([team.calculatedData.sdSuccessfulDefenseCrossesTele[dKey] for dKey in self.defenseDictionary[category] if self.teamFacedDefense(team, dKey)])

    def stdDevForPredictedDefenseScoreForAllianceForCategory(self, alliance, category):
        mean = self.predictedTeleDefensePointsForAllianceForCategory(alliance, category)
        getStdDevFunction = lambda t: self.stdDevNumCrossingsTeleForTeamForCategory(t, category)
        stdDev = utils.sumStdDevs(map(getStdDevFunction, alliance))
        return self.monteCarloForMeanForStDevForValueFunction(mean, stdDev, lambda crossings: 5 * min(crossings, 2))


    def defenseFacedForTIMD(self, timd, defenseKey):
        match = self.getMatchForNumber(timd.matchNumber)
        team = self.getTeamForNumber(timd.teamNumber)
        defensePositions = match.redDefensePositions if self.getTeamAllianceIsRedInMatch(team,
                                                                                         match) else match.blueDefensePositions
        return defenseKey in defensePositions

    def timdsWhereTeamFacedDefense(self, team, defenseKey):
        return filter(lambda timd: self.defenseFacedForTIMD(timd, defenseKey), self.getCompletedTIMDsForTeam(team))

    def numTimesTeamFacedDefense(self, team, defenseKey):
        return len(self.timdsWhereTeamFacedDefense(team, defenseKey))

    def teamFacedDefense(self, team, defenseKey):
        return self.numTimesTeamFacedDefense(team, defenseKey) > 0

    def numTimesCompetitionFacedDefense(self, defenseKey):
        return sum(map(lambda t: self.numTimesTeamFacedDefense(t, defenseKey), self.teamsWithMatchesCompleted()))

    def competitionProportionForDefense(self, defenseKey):
        competitionDefenseSightings = float(self.numTimesCompetitionFacedDefense(defenseKey))
        competitionTotalNumberOfDefenseSightings = float(5 * len(self.getCompletedTIMDsInCompetition()))
        return competitionDefenseSightings / competitionTotalNumberOfDefenseSightings if competitionTotalNumberOfDefenseSightings > 0 else 0

    def teamProportionForDefense(self, team, defenseKey):
        teamDefenseSightings = float(self.numTimesTeamFacedDefense(team, defenseKey))
        teamTotalNumberOfDefenseSightings = float(5 * len(self.getCompletedTIMDsForTeam(team)))
        return teamDefenseSightings / teamTotalNumberOfDefenseSightings if teamTotalNumberOfDefenseSightings > 0 else 0

    def alphaForTeamForDefense(self, team, defenseKey):
        return self.competitionProportionForDefense(defenseKey) + self.teamProportionForDefense(team, defenseKey)

    def betaForTeamForDefense(self, team, defenseKey):
        cachedData = self.cachedTeamDatas[team.number]
        defenseAlpha = cachedData.alphas[defenseKey]
        sumDefenseAlphas = sum(map(lambda dKey: cachedData.alphas[dKey], self.defenseList))
        return defenseAlpha / sumDefenseAlphas if sumDefenseAlphas > 0 else None

    def predictedCrosses(self, team, defenseKey):
        defenseRetrievalFunction = self.getDefenseRetrievalFunctionForDefense(
            lambda t: t.calculatedData.avgSuccessfulTimesCrossedDefensesTele, defenseKey)
        averageOfDefenseCrossingsAcrossCompetition = np.mean(
            [defenseRetrievalFunction(t) for t in self.teamsWithMatchesCompleted() if
             defenseRetrievalFunction(t) != None])
        teamAverageDefenseCrossings = defenseRetrievalFunction(team) if defenseRetrievalFunction(team) != None else 0
        competitionDefenseSightings = self.numTimesCompetitionFacedDefense(defenseKey)
        teamDefenseSightings = self.numTimesTeamFacedDefense(team, defenseKey)
        competitionTotalNumberOfDefenseSightings = 5 * len(self.getCompletedTIMDsInCompetition())
        teamTotalNumberOfDefenseSightings = 5 * len(self.getCompletedTIMDsForTeam(team))
        proportionOfCompetitionDefenseSightings = competitionDefenseSightings / competitionTotalNumberOfDefenseSightings if competitionTotalNumberOfDefenseSightings > 0 else 0
        proportionOfTeamDefenseSightings = teamDefenseSightings / teamTotalNumberOfDefenseSightings if teamTotalNumberOfDefenseSightings > 0 else 0
        theta = sum([self.betaForTeamForDefense(team, dKey) for dKey in self.defenseList if
                     self.betaForTeamForDefense(team, dKey) != None])  # TODO: Rename theta something better
        try:
            return (
                       averageOfDefenseCrossingsAcrossCompetition * theta + teamAverageDefenseCrossings * teamDefenseSightings) / (
                       teamDefenseSightings + 1)
        except:
            pass

    def listOfSuperDataPointsForTIMD(self, timd):
        return [timd.rankTorque, timd.rankSpeed, timd.rankEvasion, timd.rankDefense, timd.rankBallControl]

    def sdOfRValuesAcrossCompetition(self):
        allSuperDataPoints = []
        [allSuperDataPoints.extend(self.listOfSuperDataPointsForTIMD(timd)) for timd in self.comp.TIMDs if
         self.timdIsCompleted(timd)]
        return np.std(allSuperDataPoints)

    def RScoreForTeamForRetrievalFunction(self, team, retrievalFunction):
        avgRValue = self.getAverageForDataFunctionForTeam(team, retrievalFunction)
        avgTIMDObjectsForTeams = map(lambda t: self.getAverageForDataFunctionForTeam(t, retrievalFunction),
                                     self.teamsWithMatchesCompleted())
        averageRValuesOverComp = np.mean(avgTIMDObjectsForTeams)
        RScore = 2 * stats.norm.pdf(avgRValue, averageRValuesOverComp, self.comp.sdRScores)
        return RScore

    def drivingAbilityForTIMD(self, timd):
        return (1 * timd.rankTorque) + (1 * timd.rankBallControl) + (1 * timd.rankEvasion) + (1 * timd.rankDefense) + (
            1 * timd.rankSpeed)

    def drivingAbility(self, team, match):
        return self.drivingAbilityForTIMD(self.getTIMDForTeamNumberAndMatchNumber(team, match))

    def predictedCrossingsForDefenseCategory(self, team, category):
        return np.mean([self.predictedCrosses(team, dKey) for dKey in self.defenseDictionary[category] if
                        self.teamFacedDefense(team, dKey)])

    def getPredictedCrossingsForAllianceForCategory(self, alliance, category):
        predictedCrossingsRetrievalFunction = lambda t: self.predictedCrossingsForDefenseCategory(t, category)
        return sum(map(predictedCrossingsRetrievalFunction, alliance))

    def predictedTeleDefensePointsForAllianceForCategory(self, alliance, category):
        return 5 * min(self.getPredictedCrossingsForAllianceForCategory(alliance, category), 2)

    def predictedScoreForAllianceWithNumbers(self, allianceNumbers):
        return self.predictedScoreForAlliance(map(self.getTeamForNumber, allianceNumbers))

    def replaceWithAverageIfNecessary(self, team):
        return team if self.calculatedDataHasValues(team.calculatedData) else self.averageTeam

    def stdDevPredictedScoreForAlliance(self, alliance):
        alliance = map(self.replaceWithAverageIfNecessary, alliance)
        allianceTeleopShotPointStdDev = utils.sumStdDevs([t.calculatedData.sdTeleopShotAbility for t in alliance])
        allianceSiegePointsStdDev = utils.sumStdDevs([t.calculatedData.sdSiegeAbility for t in alliance])
        allianceAutoPointsStdDev = utils.sumStdDevs([t.calculatedData.autoAbility for t in alliance])
        allianceDefensePointsTeleStdDev = utils.sumStdDevs(map(lambda cKey: self.stdDevForPredictedDefenseScoreForAllianceForCategory(alliance, cKey), self.categories))
        return utils.sumStdDevs([allianceTeleopShotPointStdDev,
                                 allianceSiegePointsStdDev,
                                 allianceAutoPointsStdDev,
                                 allianceDefensePointsTeleStdDev])

    def stdDevPredictedScoreForAllianceNumbers(self, allianceNumbers):
        return self.stdDevPredictedScoreForAlliance(self.teamsForTeamNumbersOnAlliance(allianceNumbers))

    def predictedScoreForAlliance(self, alliance): # TODO: Do we need the checks for None here?
        alliance = map(self.replaceWithAverageIfNecessary, alliance)
        allianceTeleopShotPoints = sum(
            [t.calculatedData.teleopShotAbility for t in alliance if t.calculatedData.teleopShotAbility])
        allianceSiegePoints = sum(
            [t.calculatedData.siegeAbility for t in alliance if t.calculatedData.siegeAbility])
        allianceAutoPoints = sum(
            [t.calculatedData.autoAbility for t in alliance if t.calculatedData.autoAbility])
        alliancePredictedCrossingsRetrievalFunction = lambda c: self.predictedTeleDefensePointsForAllianceForCategory(
            alliance, c)
        allianceDefensePointsTele = sum(map(alliancePredictedCrossingsRetrievalFunction, self.categories))
        total = allianceTeleopShotPoints + allianceSiegePoints + allianceAutoPoints + allianceDefensePointsTele
        if not math.isnan(total): return total

    def stanDevForDefenseCategoryForKeyRetrievalFunctionForTeam(self, team, keyRetrievalFunction, category):
        values = map(lambda dKey: keyRetrievalFunction(team)[dKey], self.defenseDictionary[category])
        return math.sqrt(np.mean(map(lambda x: x ** 2, values)))

    def stanDevSumForDefenseCategoryForRetrievalFunctionForAlliance(self, alliance, keyRetrievalFunction, category):
        return utils.rms(map(
            lambda t: self.stanDevForDefenseCategoryForKeyRetrievalFunctionForTeam(t, keyRetrievalFunction, category),
            alliance))

    # def getStandardDeviationForAllianceForRetrievalFunction(self, alliance, retrievalFunction):
    #     return utils.rms(map(retrievalFunction, alliance))

    def standardDeviationForRetrievalFunctionForAlliance(self, retrievalFunction, alliance):
        return utils.sumStdDevs(map(retrievalFunction, alliance))

    def getStandardDeviationForDefenseCrossingsForTeam(self, team, defenseKey):
        return utils.stdDictSum(team.calculatedData.sdSuccessfulDefenseCrossesAuto, team.calculatedData.sdSuccessfulDefenseCrossesTele)[defenseKey]

    def standardDeviationForDefenseCrossingsForAlliance(self, defenseKey, alliance):
        return self.standardDeviationForRetrievalFunctionForAlliance(lambda t: self.getStandardDeviationForDefenseCrossingsForTeam(t, defenseKey), alliance)

    def standardDeviationForTeamForCategory(self, team, category):
        sumDefenseCrossingsDict = utils.dictSum(team.calculatedData.avgSuccessfulTimesCrossedDefensesAuto, team.calculatedData.avgSuccessfulTimesCrossedDefensesTele)
        return utils.rms(map(lambda dKey: sumDefenseCrossingsDict[dKey], self.defenseDictionary[category]))

    def getDefenseDamageChanceForAllianceForCategory(self, alliance, category):
        crossings = sum(map(lambda t: self.predictedCrossingsForDefenseCategory(t, category), alliance))
        stdDev = utils.sumStdDevs(map(lambda t: self.standardDeviationForTeamForCategory(t, category), alliance))
        return self.probabilityDensity(2.0, crossings, stdDev)

    def breachChanceForAlliance(self, alliance):
        defenseDamageChances = [self.getDefenseDamageChanceForAllianceForCategory(alliance, cKey) for cKey in self.categories]
        defenseDamageChances.remove(min(defenseDamageChances))
        return np.prod(defenseDamageChances)

    def shotsForTeam(self, team):
        t = team.calculatedData
        return [t.avgHighShotsAuto, t.avgHighShotsTele, t.avgLowShotsAuto, t.avgLowShotsTele]

    def numShotsForTeam(self, team):
        return sum(filter(lambda x: x != None, self.shotsForTeam(team)))

    def stdDevNumShotsForTeam(self, team):
        return utils.sumStdDevs(filter(lambda x: x != None, self.shotsForTeam(team)))

    def numShotsForAlliance(self, alliance):
        return sum(map(self.numShotsForTeam, alliance))

    def stdDevNumShotsForAlliance(self, alliance):
        return self.standardDeviationForRetrievalFunctionForAlliance(self.stdDevNumShotsForTeam, alliance)

    def captureChanceForAlliance(self, alliance):
        return self.probabilityDensity(8.0, self.numShotsForAlliance(alliance), self.stdDevNumShotsForAlliance(alliance))

    def predictedRPsForAllianceForMatch(self, allianceIsRed, match):
        alliance = self.getAllianceForMatch(match, allianceIsRed)
        breachRPs = self.breachChanceForAlliance(alliance)
        captureRPs = self.captureChanceForAlliance(alliance)

        predictedScore  = self.predictedScoreForMatchForAlliance(match, allianceIsRed)
        opposingPredictedScore = self.predictedScoreForMatchForAlliance(match, not allianceIsRed)
        sdPredictedScore = self.sdPredictedScoreForMatchForAlliance(match, allianceIsRed)
        sdOpposingPredictedScore = self.sdPredictedScoreForMatchForAlliance(match, not allianceIsRed)
        sampleSize = self.sampleSizeForMatchForAlliance(match, allianceIsRed)
        opposingSampleSize = self.sampleSizeForMatchForAlliance(match, not allianceIsRed)

        scoreRPs = 2 * self.welchsTest(predictedScore,
                                       opposingPredictedScore,
                                       sdPredictedScore,
                                       sdOpposingPredictedScore,
                                       sampleSize,
                                       opposingSampleSize)

        return breachRPs + captureRPs + scoreRPs

    def welchsTest(self, mean1, mean2, std1, std2, sampleSize1, sampleSize2):
        numerator = mean1 - mean2
        denominator = ((std1 ** 2) / sampleSize1 + (std2 ** 2) / sampleSize2) ** 0.5
        return numerator / denominator

    def citrusDPR(self, team):
        teamsInValidMatches = self.teamsWithMatchesCompleted()
        numTimesTogetherFunction = lambda t1, t2: sum(
            map(lambda m: self.teamsAreOnSameAllianceInMatch(t1, t2, m), self.getCompletedMatchesForTeam(t1)))
        getRowForTeamFunction = lambda t1: map(lambda t: numTimesTogetherFunction(t1, t), teamsInValidMatches)
        matrixOfMatchesTogether = np.matrix(map(getRowForTeamFunction, teamsInValidMatches))
        try:
            inverseMatrixOfMatchOccurrences = np.linalg.inv(matrixOfMatchesTogether)
        except:
            print 'Cannot invert matrix.'
            return None
        deltaFunction = lambda t: sum(map(self.predictedScoreForAlliance, self.getAllTeamOppositionAlliances(t))) - sum(
            self.getTeamMatchScores(t))
        teamDeltas = map(deltaFunction, teamsInValidMatches)
        return np.dot(np.matrix(teamDeltas), inverseMatrixOfMatchOccurrences)

    def citrusDPRForTIMD(self, timd):
        ATeam = self.getTeamForNumber(timd.teamNumber)
        teamsWithMatchesPlayed = []
        for team in self.comp.teams:
            if len(self.getCompletedTIMDsForTeam(team)) > 0:
                teamsWithMatchesPlayed.append(team)
        matrixOfMatches = np.zeros((len(teamsWithMatchesPlayed), len(teamsWithMatchesPlayed)))
        for team1 in teamsWithMatchesPlayed:  # Create an array where the values correspond to how many matches two teams played together in the same alliance
            for team2 in teamsWithMatchesPlayed:
                occurrence = 0
                for match in self.matches:
                    if (
                                    team1.number in match.blueAllianceTeamNumbers and team2.number in match.blueAllianceTeamNumbers) or (
                                    team1.number in match.redAllianceTeamNumbers and team2.number in match.redAllianceTeamNumbers):
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
            teamDeltas = np.append(teamDeltas,
                                   teamDelta)  # Calculate delta of each team (delta(team) = sum of predicted scores - sum of actual scores)
        teamDeltas.shape = (len(teamsWithMatchesPlayed), 1)
        citrusDPRMatrix = np.dot(inverseMatrixOfMatchOccurrences, teamDeltas)

        return citrusDPRMatrix

    def firstPickAbility(self, team):
        ourTeam = self.getTeamForNumber(self.ourTeamNum)
        if self.predictedScoreForAlliance([ourTeam, team]) == None or math.isnan(self.predictedScoreForAlliance([ourTeam, team])): return 
        return self.predictedScoreForAlliance([ourTeam, team])

    def teamInMatchFirstPickAbility(self, team, match):
        ourTeam = self.getTeamForNumber(self.ourTeamNum)
        alliance = [ourTeam, team]
        predictedScoreCustomAlliance = self.predictedScoreCustomAlliance(alliance)
        if math.isnan(predictedScoreCustomAlliance):
            return None
        return self.predictedScoreCustomAlliance(alliance)

    def allianceWithTeamRemoved(self, team, alliance):
        return filter(lambda t: t.number != team.number)

    def scoreContributionToTeamOnAlliance(self, team, alliance):
        return self.predictedScoreForAlliance(alliance) - self.predictedScoreForAlliance(
            self.allianceWithTeamRemoved(team, alliance))

    def secondPickAbilityForTeamWithTeam(self, team1, team2):
        gamma = 0.5
        if gamma != None and team1.calculatedData.citrusDPR != None and self.predictedScoreForAlliance(
                [self.getOurTeam(), team2, team1]) != None:
            return gamma * team1.calculatedData.citrusDPR + (1 - gamma) * self.predictedScoreForAlliance(
                [self.getOurTeam(), team2, team1])

    def secondPickAbility(self, team):
        secondPickAbilityDict = {}
        secondPickAbilityFunction = lambda t: utils.setDictionaryValue(secondPickAbilityDict, t.number,
                                                                       self.secondPickAbilityForTeamWithTeam(team, t))
        map(secondPickAbilityFunction, self.teamsWithMatchesCompleted())
        return secondPickAbilityDict


    def teamsSortedByRetrievalFunctions(self, retrievalFunctions, teamsRetrievalFunction=teamsWithMatchesCompleted):
        teams = teamsRetrievalFunction()
        mappableRetrievalFunction = lambda f: teams.sort(key=f)
        map(mappableRetrievalFunction, retrievalFunctions[::-1])
        return teams

    def breachPercentage(self, team):
        breachPercentage = 0
        for match in self.team.matches:
            if team.number in match.blueAllianceTeamNumbers and match.blueScore != None:
                if match.blueAllianceDidBreach == True:
                    breachPercentage += 1
            elif team.number in match.redAllianceTeamNumbers and match.blueScore != None:
                if match.redAllianceDidBreach == True:
                    breachPercentage += 1
        return breachPercentage / len(self.team.matches)

    def numDefensesCrossedInMatch(self, allianceIsRed, match):
        alliance = map(self.getTeamForNumber, match.redAllianceTeamNumbers) if allianceIsRed else map(
            self.getTeamForNumber, match.blueAllianceTeamNumbers)
        numCrossesDictForTeamFunction = lambda t: utils.dictSum(t.calculatedData.avgSuccessfulTimesCrossedDefensesAuto,
                                                                t.calculatedData.avgSuccessfulTimesCrossedDefensesTele)
        numCrossesForTeamFunction = lambda t: sum(numCrossesDictForTeamFunction(t).values())
        return sum(map(numCrossesForTeamFunction, alliance))

    def getPredictedNumRPsForTeamForMatch(self, team, match):
        teamIsOnRedAlliance = self.getTeamAllianceIsRedInMatch(team, match)
        return match.calculatedData.predictedRedRPs if teamIsOnRedAlliance else match.calculatedData.predictedBlueRPs

    def getUpdatedNumRPsForTeamForMatch(self, team, match):
        return self.getActualNumRPsForTeamForMatch(team, match) if self.matchIsCompleted(match) else self.getPredictedNumRPsForTeamForMatch(team, match)

    def predictedNumberOfRPs(self, team):
        return sum([self.getUpdatedNumRPsForTeamForMatch(team, m) for m in self.getMatchesForTeam(team)])

    def getActualNumRPsForTeamForMatch(self, team, match):
        teamIsOnRedAlliance = self.getTeamAllianceIsRedInMatch(team, match)
        return match.calculatedData.actualRedRPs if teamIsOnRedAlliance else match.calculatedData.actualBlueRPs

    def actualNumberOfRPs(self, team):
        return sum([self.getActualNumRPsForTeamForMatch(team, m) for m in self.getCompletedMatchesForTeam(team)])

    def getFieldsForAllianceForMatch(self, allianceIsRed, match):
        return (match.redScore, match.redAllianceDidBreach, match.redAllianceDidCapture) if allianceIsRed else (
            match.blueScore, match.blueAllianceDidBreach, match.blueAllianceDidCapture)

    def scoreRPsGainedFromMatchWithScores(self, score, opposingScore):
        if score > opposingScore:
            return 2
        elif score == opposingScore:
            return 1
        else:
            return 0

    def getTeamScoreInMatch(self, team, match):
        return self.getFieldsForAllianceForMatch(self.getTeamAllianceIsRedInMatch(team, match), match)[0]

    def getTeamMatchScores(self, team):
        return map(lambda m: self.getTeamMatchScores(team, m), self.getCompletedMatchesForTeam(team))

    def RPsGainedFromMatchForAlliance(self, allianceIsRed, match):
        numRPs = 0
        ourFields = self.getFieldsForAllianceForMatch(allianceIsRed, match)
        opposingFields = self.getFieldsForAllianceForMatch(not allianceIsRed, match)
        numRPs += self.scoreRPsGainedFromMatchWithScores(ourFields[0], opposingFields[0])
        numRPs += int(utils.convertFirebaseBoolean(ourFields[1]))
        numRPs += int(utils.convertFirebaseBoolean(ourFields[2]))
        return numRPs

    def getTeamAllianceIsRedInMatch(self, team, match):
        if team.number == -1:
            return True
        if team.number in match.redAllianceTeamNumbers:
            return True
        elif team.number in match.blueAllianceTeamNumbers:
            return False
        else:
            raise ValueError('Team ' + str(team.number) + ' is not in match ' + str(match.number))

    def predictedScoreForMatchForAlliance(self, match, allianceIsRed):
        return match.calculatedData.predictedRedScore if allianceIsRed else match.calculatedData.predictedBlueScore

    def sdPredictedScoreForMatchForAlliance(self, match, allianceIsRed):
        return match.calculatedData.sdPredictedRedScore if allianceIsRed else match.calculatedData.sdPredictedBlueScore

    def getAvgNumCompletedTIMDsForTeamsOnAlliance(self, alliance):
        return np.mean(map(lambda t: len(self.getCompletedTIMDsForTeam(t)), alliance))

    def getAvgNumCompletedTIMDsForMatchForAllianceIsRed(self, match, allianceIsRed):
        return self.getAvgNumCompletedTIMDsForTeamsOnAlliance(self.getAllianceForMatch(match, allianceIsRed))

    def sampleSizeForMatchForAlliance(self, match, allianceIsRed):
        return self.getAvgNumCompletedTIMDsForMatchForAllianceIsRed(match, allianceIsRed)

    def RPsGainedFromMatchForTeam(self, match, team):
        return self.RPsGainedFromMatchForAlliance(self.getTeamAllianceIsRedInMatch(team, match), match)

    # Competition wide Metrics
    def avgCompScore(self):
        a = [(match.redScore + match.blueScore) for match in self.matches if
             (match.blueScore != None and match.redScore != None)]
        return sum(a) / len(self.matches)

    def numPlayedMatchesInCompetition(self):
        return len([match for match in self.matches if self.matchIsPlayed(match)])

    def getRankingForTeamByRetrievalFunctions(self, team, retrievalFunctions):
        if team in self.teamsWithCalculatedData():
            return self.teamsSortedByRetrievalFunctions(retrievalFunctions, teamsRetrievalFunction=self.teamsWithCalculatedData).index(team)

    def getSeedingFunctions(self):
        return [lambda t: t.calculatedData.numRPs, lambda t: t.calculatedData.autoAbility,
                lambda t: t.calculatedData.siegeAbility]

    def getPredictedSeedingFunctions(self):
        predictedAutoPointsFunction = lambda t: self.getPredictedResultOfRetrievalFunctionForTeam(t, lambda
            t2: t2.calculatedData.autoAbility)
        predictedSiegePointsFunction = lambda t: self.getPredictedResultOfRetrievalFunctionForTeam(t, lambda
            t2: t2.calculatedData.siegeAbility)
        return [lambda t: t.calculatedData.predictedNumRPs, predictedAutoPointsFunction, predictedSiegePointsFunction]

    def teamsForTeamNumbersOnAlliance(self, alliance):
        return map(self.getTeamForNumber, alliance)

    def getAllianceForMatch(self, match, allianceIsRed):
        return self.teamsForTeamNumbersOnAlliance(
            match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers)

    def getAllianceForTeamInMatch(self, team, match):
        return self.getAllianceForMatch(match, self.getTeamAllianceIsRedInMatch(team, match))

    def getPredictedResultOfRetrievalFunctionForAlliance(self, retrievalFunction, alliance):
        return sum(map(retrievalFunction, alliance))

    def getPredictedResultOfRetrievalFunctionForTeamInMatch(self, team, match, retrievalFunction):
        return self.getPredictedResultOfRetrievalFunctionForAlliance(retrievalFunction,
                                                                     self.getAllianceForTeamInMatch(team, match))

    def getPredictedResultOfRetrievalFunctionForTeam(self, retrievalFunction, team):
        return np.mean(map(retrievalFunction, self.getMatchesForTeam(team)))

    def getDefenseLength(self, dict, defenseKey):
        return len(dict[defenseKey]) if defenseKey in dict and dict[defenseKey] != None else 0

    def defenseKeysThatAreNotNone(self, defenseDict):
        return filter(lambda dKey: defenseDict[dKey] != None, defenseDict)

    def teamInMatchDatasThatHaveDefenseValueNotNoneForTeam(self, team, retrievalFunction, defenseKey):
        return filter(lambda timd: defenseKey in retrievalFunction(timd), self.getCompletedTIMDsForTeam(team))

    def getDefensesThatTeamHasCrossedForRetrievalFunction(self, team, retrievalFunction):
        return self.retrievalFunctions(team).keys()

    def getAverageForDefenseDataFunctionForTeam(self, team, retrievalFunction, defenseKey, dataFunction):
        return np.mean(map(dataFunction,
                           self.teamInMatchDatasThatHaveDefenseValueNotNoneForTeam(team, retrievalFunction,
                                                                                   defenseKey)))

    def getAverageAcrossMatchesTeamSawDefense(self, team, defenseKey, retrievalFunction):
        return np.mean(map(retrievalFunction, self.timdsWhereTeamFacedDefense(team, defenseKey)))

    def getStdDevAcrossMatchesTeamSawDefense(self, team, defenseKey, retrievalFunction):
        return np.std(map(retrievalFunction, self.timdsWhereTeamFacedDefense(team, defenseKey)))

    def setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForTeam(self, team,
                                                                                                        keyRetrievalFunction,
                                                                                                        valueRetrievalFunction,
                                                                                                        dataPointModificationFunction,
                                                                                                        applyFunction):
        keyDict = keyRetrievalFunction(team)
        protectedModifiedDataPointFunction = lambda x: dataPointModificationFunction(x)
        getModifiedDataPointFunction = lambda dKey, timd: protectedModifiedDataPointFunction(
            valueRetrievalFunction(timd)[dKey] if dKey in valueRetrievalFunction(timd) else None)
        getAverageFunction = lambda dKey: applyFunction(team, dKey, lambda
            timd: getModifiedDataPointFunction(dKey, timd))
        protectedGetAverageFunction = lambda dKey: getAverageFunction(dKey) if not math.isnan(
            getAverageFunction(dKey)) else None
        dictionarySetFunction = lambda dKey: utils.setDictionaryValue(keyDict, dKey, protectedGetAverageFunction(dKey))
        map(dictionarySetFunction, self.defenseList)

    def setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForCompetition(self,
                                                                                                               team,
                                                                                                               keyRetrievalFunction,
                                                                                                               valueRetrievalFunction,
                                                                                                               dataPointModificationFunction):
        keyDict = keyRetrievalFunction(team)
        protectedModifiedDataPointFunction = lambda x: dataPointModificationFunction(x)
        getModifiedDataPointFunction = lambda dKey, timd: protectedModifiedDataPointFunction(
            valueRetrievalFunction(timd)[dKey] if dKey in valueRetrievalFunction(timd) else None)
        getAverageFunction = lambda dKey: self.getAverageAcrossCompetitionTeamSawDefense(team, dKey, lambda
            timd: getModifiedDataPointFunction(dKey, timd))
        protectedGetAverageFunction = lambda dKey: getAverageFunction(dKey) if not math.isnan(
            getAverageFunction(dKey)) else None
        dictionarySetFunction = lambda dKey: utils.setDictionaryValue(keyDict, dKey, protectedGetAverageFunction(dKey))
        map(dictionarySetFunction, self.defenseList)

    def timdsWithDefense(self, defenseKey):
        return filter(lambda t: self.defenseFacedForTIMD(t, defenseKey), self.getCompletedTIMDsInCompetition())

    def getAverageAcrossCompetitionTeamSawDefense(self, team, defenseKey, retrievalFunction):
        return np.mean(map(retrievalFunction, self.timdsWithDefense(defenseKey)))

    def setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForCompetition(self, team,
                                                                                        keyRetrievalFunction,
                                                                                        valuesRetrievalFunction):
        dict = keyRetrievalFunction(team)
        someFunction = lambda dKey, timd: self.getDefenseLength(valuesRetrievalFunction(timd), dKey)
        getAverageFunction = lambda dKey: self.getAverageForDefenseDataFunctionForTeam(team, lambda
            timd: valuesRetrievalFunction(timd), dKey, lambda timd: someFunction(dKey, timd))
        protectedGetAverageFunction = lambda dKey: getAverageFunction(dKey) if not math.isnan(
            getAverageFunction(dKey)) else None
        dictionarySetFunction = lambda dKey: utils.setDictionaryValue(dict, dKey, protectedGetAverageFunction(dKey))
        map(dictionarySetFunction, self.defenseList)

    def setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForTeam(self, team, keyRetrievalFunction,
                                                                                 valuesRetrievalFunction):
        dict = keyRetrievalFunction(team)
        someFunction = lambda dKey, timd: self.getDefenseLength(valuesRetrievalFunction(timd), dKey)
        getAverageFunction = lambda dKey: self.getAverageForDefenseDataFunctionForTeam(team, lambda
            timd: valuesRetrievalFunction(timd), dKey, lambda timd: someFunction(dKey, timd))
        protectedGetAverageFunction = lambda dKey: getAverageFunction(dKey) if not math.isnan(
            getAverageFunction(dKey)) else None
        dictionarySetFunction = lambda dKey: utils.setDictionaryValue(dict, dKey, protectedGetAverageFunction(dKey))
        map(dictionarySetFunction, self.defenseList)

    def getAvgOfDefensesForRetrievalFunctionForTeam(self, team, teamRetrievalFunction):
        defenseRetrievalFunctions = self.getDefenseRetrievalFunctions(teamRetrievalFunction)
        return np.mean(map(lambda retrievalFunction: retrievalFunction(team), defenseRetrievalFunctions))

    def setDefenseValuesForTeam(self, team, keyRetrievalFunction, valueRetrievalFunction,
                                dataPointModificationFunction):
        dict = keyRetrievalFunction(team)
        defenseRetrievalFunctions = map(
            lambda dKey: self.getDefenseRetrievalFunctionForDefense(valueRetrievalFunction, dKey), self.defenseList)
        defenseModifiedFunctions = map(dataPointModificationFunction, defenseRetrievalFunctions)

        for d in self.defenseList:
            defenseRetrievalFunction = self.getDefenseRetrievalFunctionForDefense(valueRetrievalFunction, d)
            defenseLengthFunction = lambda t: len(defenseRetrievalFunction(t))
            print self.getDefenseRetrievalFunctionForDefense(valueRetrievalFunction, 'pc')
            self.getAverageForDataFunctionForTeam(team, defenseLengthFunction)

        defenseValueFunctions = map(len, self.getDefenseRetrievalFunctions(valueRetrievalFunction))
        defenseModifiedFunctions = map(dataPointModificationFunction, defenseValueFunctions)
        setFunction = lambda dKey: utils.setDictionaryValue(dict, dKey, defenseModifiedFunctions)
        map(setFunction, self.defenseList)
        defenseSetFunction = lambda dp: utils.setDictionaryKey(keyRetrievalFunction(team),
                                                               dataPointModificationFunction(
                                                                   self.getDefenseRetrievalFunctionForDefensePairing(
                                                                       valueRetrievalFunction, dp)))
        defenseRetrievalFunctions = map(self.getDefenseRetrievalFunctionForDefensePairing, self.getDefensePairings())
        map(defenseSetFunction, self.getDefensePairings())

    def totalAvgDefenseCrosses(self, team):
        t = team.calculatedData
        return sum(map(lambda k: t.avgSuccessfulTimesCrossedDefensesAuto[k] + t.avgSuccessfulTimesCrossedDefensesTele,
                       self.defenseList))

    def teamDidBreachInMatch(self, team, match):
        return match.redAllianceDidBreach if self.getTeamAllianceIsRedInMatch(team,
                                                                              match) else match.blueAllianceDidBreach

    def getTIMDTeleopShotAbility(self, timd):
        return 5 * timd.numHighShotsMadeTele + 2 * timd.numLowShotsMadeTele


    def getAverageOfDataFunctionAcrossCompetition(self, dataFunction):
        return np.mean(map(lambda timd: dataFunction(timd), self.getCompletedTIMDsInCompetition()))

    def getStandardDeviationOfDataFunctionAcrossCompetition(self, dataFunction):
        return np.std(map(lambda timd: dataFunction(timd), self.getCompletedTIMDsInCompetition()))

    def getAverageTeam(self):
        self.doFirstCalculationsForTeam(self.averageTeam)
        self.doSecondCalculationsForTeam(self.averageTeam)
        # team = self.averageTeam
        # t = team.calculatedData
        # cachedData = self.cachedTeamDatas[team.number]
        # map(lambda dKey: utils.setDictionaryValue(cachedData.alphas, dKey, self.alphaForTeamForDefense(team, dKey)),
        #     self.defenseList)

        # t.avgTorque = self.getAverageOfDataFunctionAcrossCompetition(lambda timd: timd.rankTorque)  # Checked
        # t.avgSpeed = self.getAverageOfDataFunctionAcrossCompetition(lambda timd: timd.rankSpeed)  # Checked
        # t.avgEvasion = self.getAverageOfDataFunctionAcrossCompetition(lambda timd: timd.rankEvasion)  # Checked
        # t.avgDefense = self.getAverageOfDataFunctionAcrossCompetition(lambda timd: timd.rankDefense)  # Checked
        # t.avgBallControl = self.getAverageOfDataFunctionAcrossCompetition(lambda timd: timd.rankBallControl)  # Checked

        # t.disabledPercentage = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: int(utils.convertFirebaseBoolean(timd.didGetDisabled)))
        # t.incapacitatedPercentage = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: int(utils.convertFirebaseBoolean(timd.didGetIncapacitated)))
        # t.disfunctionalPercentage = t.disabledPercentage + t.incapacitatedPercentage

        # # Auto
        # t.autoAbility = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.calculatedData.autoAbility)
        # t.avgHighShotsAuto = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.numHighShotsMadeAuto)  # Checked
        # t.avgLowShotsAuto = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.numLowShotsMadeAuto)  # Checked	
        # t.reachPercentage = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: int(utils.convertFirebaseBoolean(timd.didReachAuto)))
        # t.highShotAccuracyAuto = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.calculatedData.highShotAccuracyAuto)  # Checked
        # t.lowShotAccuracyAuto = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.calculatedData.lowShotAccuracyAuto)  # Checked
        # t.numAutoPoints = self.getAverageOfDataFunctionAcrossCompetition(self.numAutoPointsForTIMD)  # Checked
        # t.avgMidlineBallsIntakedAuto = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: len(timd.ballsIntakedAuto))
        # t.sdHighShotsAuto = self.getStandardDeviationOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.numHighShotsMadeAuto)  # Checked
        # t.sdLowShotsAuto = self.getStandardDeviationOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.numLowShotsMadeAuto)  # Checked
        # # t.sdMidlineBallsIntakedAuto = self.getStandardDeviationForDataFunctionForTeam(team, 'ballsIntakedAuto')
        # t.sdMidlineBallsIntakedAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: len(
        #     timd.ballsIntakedAuto))
        # t.sdBallsKnockedOffMidlineAuto = self.getStandardDeviationOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.numBallsKnockedOffMidlineAuto)  # Checked\
        # self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForCompetition(
        #     team, lambda tm: tm.calculatedData.avgSuccessfulTimesCrossedDefensesAuto,
        #     lambda timd: timd.timesSuccessfulCrossedDefensesAuto, lambda x: len(x) if x != None else 0)
        # self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForCompetition(
        #     team, lambda tm: tm.calculatedData.avgSuccessfulTimesCrossedDefensesTele,
        #     lambda timd: timd.timesSuccessfulCrossedDefensesTele, lambda x: len(x) if x != None else 0)
        # self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForCompetition(
        #     team, lambda tm: tm.calculatedData.avgFailedTimesCrossedDefensesAuto,
        #     lambda timd: timd.timesFailedCrossedDefensesAuto, lambda x: len(x) if x != None else 0)
        # self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForCompetition(
        #     team, lambda tm: tm.calculatedData.avgFailedTimesCrossedDefensesTele,
        #     lambda timd: timd.timesFailedCrossedDefensesTele, lambda x: len(x) if x != None else 0)
        # self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForCompetition(
        #     team, lambda tm: tm.calculatedData.avgTimeForDefenseCrossAuto,
        #     lambda timd: timd.timesSuccessfulCrossedDefensesAuto, lambda x: np.mean(x) if x != None and x != [] else 0)
        # self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForCompetition(
        #     team, lambda tm: tm.calculatedData.avgTimeForDefenseCrossTele,
        #     lambda timd: timd.timesSuccessfulCrossedDefensesTele, lambda x: np.mean(x) if x != None and x != [] else 0)
        # # self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForTeam(team, lambda tm: tm.calculatedData.avgSuccessfulTimesCrossedDefensesAuto, lambda timd: timd.timesSuccessfulCrossedDefensesAuto)
        # # self.setDefenseValuesForTeam(team, lambda t1: t1.calculatedData.avgSuccessfulTimesCrossedDefensesAuto, lambda timd: timd.timesSuccessfulCrossedDefensesAuto, lambda rF: self.getAverageForDataFunctionForTeam(team, lambda timd: len(rF(timd))))				

        # # #Tele
        # t.scalePercentage = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: int(utils.convertFirebaseBoolean(timd.didScaleTele)))
        # t.challengePercentage = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: int(utils.convertFirebaseBoolean(timd.didChallengeTele)))
        # t.avgGroundIntakes = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.numGroundIntakesTele)  # Checked
        # t.avgBallsKnockedOffMidlineAuto = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.numBallsKnockedOffMidlineAuto)  # Checked
        # t.avgShotsBlocked = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.numShotsBlockedTele)  # Checked
        # t.avgHighShotsTele = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.numHighShotsMadeTele)  # Checked
        # t.avgLowShotsTele = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.numLowShotsMadeTele)  # Checked
        # t.highShotAccuracyTele = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.calculatedData.highShotAccuracyTele)  # Checked
        # t.lowShotAccuracyTele = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.calculatedData.lowShotAccuracyAuto)  # Checked
        # # t.blockingAbility = self.blockingAbility(team)  # TODO: Move this later
        # t.teleopShotAbility = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.calculatedData.teleopShotAbility)
        # t.siegeConsistency = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.calculatedData.siegeConsistency)
        # t.siegeAbility = self.getAverageOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.calculatedData.siegeAbility)
        # t.sdHighShotsTele = self.getStandardDeviationOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.numHighShotsMadeTele)  # Checked
        # t.sdLowShotsTele = self.getStandardDeviationOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.numLowShotsMadeTele)  # Checked
        # t.sdGroundIntakes = self.getStandardDeviationOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.numGroundIntakesTele)  # Checked
        # t.sdShotsBlocked = self.getStandardDeviationOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.numShotsBlockedTele)  # Checked
        # t.sdTeleopShotAbility  = self.getStandardDeviationOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.calculatedData.teleopShotAbility)
        # t.sdAutoAbility  = self.getStandardDeviationOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.calculatedData.autoAbility)
        # t.sdSiegeAbility  = self.getStandardDeviationOfDataFunctionAcrossCompetition(
        #     lambda timd: timd.calculatedData.siegeAbility)
        # t.numRPs = self.numRPsForTeam(team)  # Checked
        # t.numScaleAndChallengePoints = self.numScaleAndChallengePointsForTeam(team)  # Checked

    def doFirstCalculationsForTeam(self, team):
        if len(self.getCompletedTIMDsForTeam(team)) <= 0:
            print "No Complete TIMDs for team " + str(team.number) + ", " + str(team.name)
        else:
            print("Beginning first calculations for team: " + str(team.number) + ", " + str(team.name))
            # Super Scout Averages

            if not self.calculatedDataHasValues(team.calculatedData):
                team.calculatedData = DataModel.CalculatedTeamData()
            t = team.calculatedData

            cachedData = self.cachedTeamDatas[team.number]
            map(lambda dKey: utils.setDictionaryValue(cachedData.alphas, dKey, self.alphaForTeamForDefense(team, dKey)),
                self.defenseList)

            t.avgTorque = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankTorque)  # Checked
            t.avgSpeed = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankSpeed)  # Checked
            t.avgEvasion = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankEvasion)  # Checked
            t.avgDefense = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankDefense)  # Checked
            t.avgBallControl = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankBallControl)  # Checked

            t.disabledPercentage = self.getAverageForDataFunctionForTeam(team, lambda timd: int(
                utils.convertFirebaseBoolean(timd.didGetDisabled)))
            t.incapacitatedPercentage = self.getAverageForDataFunctionForTeam(team, lambda timd: int(
                utils.convertFirebaseBoolean(timd.didGetIncapacitated)))
            t.disfunctionalPercentage = t.disabledPercentage + t.incapacitatedPercentage

            # Auto
            t.autoAbility = self.getAverageForDataFunctionForTeam(team,
                lambda timd: timd.calculatedData.autoAbility)
            t.avgHighShotsAuto = self.getAverageForDataFunctionForTeam(team, 
                lambda timd: timd.numHighShotsMadeAuto)  # Checked
            t.avgLowShotsAuto = self.getAverageForDataFunctionForTeam(team,
                                                                      lambda timd: timd.numLowShotsMadeAuto)  # Checked	
            t.reachPercentage = self.getAverageForDataFunctionForTeam(team, lambda timd: int(
                utils.convertFirebaseBoolean(timd.didReachAuto)))
            t.highShotAccuracyAuto = self.getAverageForDataFunctionForTeam(team,
                                                                           self.getTIMDHighShotAccuracyAuto)  # Checked
            t.lowShotAccuracyAuto = self.getAverageForDataFunctionForTeam(team,
                                                                          self.getTIMDLowShotAccuracyAuto)  # Checked
            t.numAutoPoints = self.getAverageForDataFunctionForTeam(team, self.numAutoPointsForTIMD)  # Checked
            t.avgMidlineBallsIntakedAuto = self.getAverageForDataFunctionForTeam(team, lambda timd: len(
                timd.ballsIntakedAuto))
            t.sdMidlineBallsIntakedAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: len(
                timd.ballsIntakedAuto))
            t.sdHighShotsAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda
                timd: timd.numHighShotsMadeAuto)  # Checked
            t.sdLowShotsAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda
                timd: timd.numLowShotsMadeAuto)  # Checked
            # t.sdMidlineBallsIntakedAuto = self.getStandardDeviationForDataFunctionForTeam(team, 'ballsIntakedAuto')
            t.sdBallsKnockedOffMidlineAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda
                timd: timd.numBallsKnockedOffMidlineAuto)  # Checked\

            self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForTeam( # TODO: Format all of the defenses this way (Abhi)
                team,
                lambda tm: tm.calculatedData.avgSuccessfulTimesCrossedDefensesAuto,
                lambda timd: timd.timesSuccessfulCrossedDefensesAuto,
                lambda x: len(x) if x != None else 0,
                self.getAverageAcrossMatchesTeamSawDefense)
            
            self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForTeam(
                team,
                lambda tm: tm.calculatedData.avgFailedTimesCrossedDefensesAuto, 
                lambda timd: timd.timesFailedCrossedDefensesAuto,
                lambda x: len(x) if x != None else 0,
                self.getAverageAcrossMatchesTeamSawDefense)
            
            self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForTeam(
                team,
                lambda tm: tm.calculatedData.avgTimeForDefenseCrossAuto,
                lambda timd: timd.timesSuccessfulCrossedDefensesAuto,
                lambda x: np.mean(x) if x != None and x != [] else 0,
                self.getAverageAcrossMatchesTeamSawDefense)
            

            # #Tele
            t.scalePercentage = self.getAverageForDataFunctionForTeam(team, lambda timd: int(
                utils.convertFirebaseBoolean(timd.didScaleTele)))
            t.challengePercentage = self.getAverageForDataFunctionForTeam(team, lambda timd: int(
                utils.convertFirebaseBoolean(timd.didChallengeTele)))
            t.avgGroundIntakes = self.getAverageForDataFunctionForTeam(team, lambda
                timd: timd.numGroundIntakesTele)  # Checked
            t.avgBallsKnockedOffMidlineAuto = self.getAverageForDataFunctionForTeam(team, lambda
                timd: timd.numBallsKnockedOffMidlineAuto)  # Checked
            t.avgShotsBlocked = self.getAverageForDataFunctionForTeam(team,
                                                                      lambda timd: timd.numShotsBlockedTele)  # Checked
            t.avgHighShotsTele = self.getAverageForDataFunctionForTeam(team, lambda
                timd: timd.numHighShotsMadeTele)  # Checked
            t.avgLowShotsTele = self.getAverageForDataFunctionForTeam(team,
                                                                      lambda timd: timd.numLowShotsMadeTele)  # Checked
            t.highShotAccuracyTele = self.getAverageForDataFunctionForTeam(team,
                                                                           self.getTIMDHighShotAccuracyTele)  # Checked
            t.lowShotAccuracyTele = self.getAverageForDataFunctionForTeam(team,
                                                                          self.getTIMDLowShotAccuracyTele)  # Checked
            t.teleopShotAbility = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.calculatedData.teleopShotAbility)  # Checked
            t.siegeConsistency = self.getAverageForDataFunctionForTeam(team, lambda timd: utils.convertFirebaseBoolean(timd.didChallengeTele) or utils.convertFirebaseBoolean(timd.didScaleTele))  # Checked
            t.siegeAbility = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.calculatedData.siegeAbility)  # Checked


            t.sdHighShotsTele = self.getStandardDeviationForDataFunctionForTeam(team, lambda
                timd: timd.numHighShotsMadeTele)  # Checked
            t.sdLowShotsTele = self.getStandardDeviationForDataFunctionForTeam(team, lambda
                timd: timd.numLowShotsMadeTele)  # Checked
            t.sdGroundIntakes = self.getStandardDeviationForDataFunctionForTeam(team, lambda
                timd: timd.numGroundIntakesTele)  # Checked
            t.sdShotsBlocked = self.getStandardDeviationForDataFunctionForTeam(team, lambda
                timd: timd.numShotsBlockedTele)  # Checked
            t.sdTeleopShotAbility = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.calculatedData.teleopShotAbility)
            t.sdSiegeAbility = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.calculatedData.siegeAbility)
            t.sdAutoAbility = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.calculatedData.autoAbility)
            t.numRPs = self.numRPsForTeam(team)  # Checked
            t.numScaleAndChallengePoints = self.numScaleAndChallengePointsForTeam(team)  # Checked
            t.breachPercentage = self.getAverageForDataFunctionForTeam(team, lambda timd: int(
                utils.convertFirebaseBoolean(self.teamDidBreachInMatch(team, self.getMatchForNumber(timd.matchNumber)))))

            self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForTeam(
                team,
                lambda tm: tm.calculatedData.avgSuccessfulTimesCrossedDefensesTele,
                lambda timd: timd.timesSuccessfulCrossedDefensesTele,
                lambda x: len(x) if x != None else 0,
                self.getAverageAcrossMatchesTeamSawDefense)
            self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForTeam(
                team,
                lambda tm: tm.calculatedData.avgFailedTimesCrossedDefensesTele,
                lambda timd: timd.timesFailedCrossedDefensesTele,
                lambda x: len(x) if x != None else 0,
                self.getAverageAcrossMatchesTeamSawDefense)
            self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForTeam(
                team,
                lambda tm: tm.calculatedData.avgTimeForDefenseCrossTele,
                lambda timd: timd.timesSuccessfulCrossedDefensesTele,
                lambda x: np.mean(x) if x != None and x != [] else 0,
                self.getAverageAcrossMatchesTeamSawDefense)
            self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForTeam(
                team,
                lambda tm: tm.calculatedData.sdSuccessfulDefenseCrossesTele,
                lambda timd: timd.timesSuccessfulCrossedDefensesTele,
                lambda x: len(x) if x != None else 0,
                self.getStdDevAcrossMatchesTeamSawDefense)

    def doSecondCalculationsForTeam(self, team):
        if len(self.getCompletedTIMDsForTeam(team)) <= 0:
            print "No Complete TIMDs for team " + str(team.number) + ", " + str(team.name)
        else:
            print("Beginning second calculations for team: " + str(team.number) + ", " + str(team.name))
            #print("#")
            t = team.calculatedData
            t.RScoreTorque = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankTorque)
            t.RScoreSpeed = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankSpeed)
            t.RScoreEvasion = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankEvasion)
            t.RScoreDefense = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankDefense)
            t.RScoreBallControl = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankBallControl)
            t.RScoreDrivingAbility = self.RScoreForTeamForRetrievalFunction(team, self.drivingAbilityForTIMD)
            t.avgSuccessfulTimesCrossedDefenses = utils.dictSum(t.avgSuccessfulTimesCrossedDefensesAuto,
                                                                t.avgSuccessfulTimesCrossedDefensesTele)
            t.firstPickAbility = self.firstPickAbility(team)
            t.secondPickAbility = {}
            [utils.setDictionaryValue(t.secondPickAbility, team.number, 15.0) for team in self.comp.teams]
            t.overallSecondPickAbility = 15.0
            t.citrusDPR = 12.0
            t.predictedNumRPs = self.predictedNumberOfRPs(team)
            t.actualNumRPs = self.actualNumberOfRPs(team)
            t.firstPickAbility = self.firstPickAbility(team) # Checked	
            t.secondPickAbility = self.secondPickAbility(team) # Checked
            t.overallSecondPickAbility = self.overallSecondPickAbility(team) # Checked
            t.citrusDPR = self.citrusDPR(team)
            t.actualSeed = self.getRankingForTeamByRetrievalFunctions(team, self.getSeedingFunctions()) # Checked
            t.predictedSeed = self.getRankingForTeamByRetrievalFunctions(team, self.getPredictedSeedingFunctions()) # Checked

    def doFirstCalculationsForTIMD(self, timd):
        if (not self.timdIsCompleted(timd)):
            print "TIMD is not complete for team " + str(timd.teamNumber) + " in match " + str(timd.matchNumber)
        else:
            print "Beginning first calculations for team " + str(timd.teamNumber) + " in match " + str(timd.matchNumber)
            team = self.getTeamForNumber(timd.teamNumber)
            match = self.getMatchForNumber(timd.matchNumber)


            if not self.calculatedDataHasValues(
                    timd.calculatedData): timd.calculatedData = DataModel.CalculatedTeamInMatchData()
            c = timd.calculatedData
            c.teleopShotAbility = self.getTIMDTeleopShotAbility(timd)
            c.highShotAccuracyTele = self.getTIMDHighShotAccuracyTele(timd)  # Checked
            c.highShotAccuracyAuto = self.getTIMDHighShotAccuracyAuto(timd)  # Checked
            c.lowShotAccuracyTele = self.getTIMDLowShotAccuracyTele(timd)  # Checked
            c.lowShotAccuracyAuto = self.getTIMDLowShotAccuracyAuto(timd)  # Checked
            c.siegeAbility = self.singleSiegeAbility(timd)
            c.autoAbility = self.autoAbility(timd)
            c.siegeConsistency = utils.convertFirebaseBoolean(timd.didChallengeTele) + utils.convertFirebaseBoolean(timd.didScaleTele)


            c.numAutoPoints = self.numAutoPointsForTIMD(timd)
            c.numScaleAndChallengePoints = c.siegeAbility  # they are the same
            c.numBallsIntakedOffMidlineAuto = self.getAverageForDataFunctionForTeam(team, lambda timd: len(
                timd.ballsIntakedAuto))
            self.restoreComp()

    def doSecondCalculationsForTIMD(self, timd):
        if (not self.timdIsCompleted(timd)):
            print "TIMD is not complete for team " + str(timd.teamNumber) + " in match " + str(timd.matchNumber)
        else:
            print "Beginning second calculations for team " + str(timd.teamNumber) + " in match " + str(
                timd.matchNumber)
            c = timd.calculatedData
            team = self.getTeamForNumber(timd.teamNumber)

            self.TIMDs = filter(lambda t: (t.teamNumber != timd.teamNumber) == (t.matchNumber != timd.matchNumber),
                                self.comp.TIMDs)
            self.matches = filter(lambda m: (not self.teamInMatch(team, m)) == (timd.matchNumber != m.number),
                                  self.comp.matches)

            self.doFirstTeamCalculations()
            self.doMatchesCalculations()
            self.doSecondTeamCalculations()

            c.RScoreTorque = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankTorque)
            c.RScoreSpeed = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankSpeed)
            c.RScoreEvasion = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankEvasion)
            c.RScoreDefense = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankDefense)
            c.RScoreBallControl = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankBallControl)
            c.RScoreDrivingAbility = self.RScoreForTeamForRetrievalFunction(team, self.drivingAbilityForTIMD)
            c.firstPickAbility = 6.0
            c.secondPickAbility = {}
            [utils.setDictionaryValue(c.secondPickAbility, team.number, 15.0) for team in self.comp.teams]
            c.overallSecondPickAbility = 15.0
            self.restoreComp()

    def doFirstCalculationsForMatch(self, match):
        if not self.matchIsCompleted(match):
            print "Match " + str(match.number) + " has not been played yet."
            match.calculatedData.predictedBlueScore = self.predictedScoreForAllianceWithNumbers(match.blueAllianceTeamNumbers)
            match.calculatedData.predictedRedScore = self.predictedScoreForAllianceWithNumbers(match.redAllianceTeamNumbers)
            match.calculatedData.sdPredictedBlueScore = self.stdDevPredictedScoreForAllianceNumbers(match.blueAllianceTeamNumbers)
            match.calculatedData.sdPredictedRedScore = self.stdDevPredictedScoreForAllianceNumbers(match.redAllianceTeamNumbers)
            match.calculatedData.predictedBlueRPs = self.predictedRPsForAllianceForMatch(False, match)
            match.calculatedData.predictedRedRPs = self.predictedRPsForAllianceForMatch(True, match)
        else:
            print "Beginning calculations for match " + str(match.number) + "..."
            match.calculatedData.predictedBlueScore = self.predictedScoreForAllianceWithNumbers(match.blueAllianceTeamNumbers)
            match.calculatedData.predictedRedScore = self.predictedScoreForAllianceWithNumbers(match.redAllianceTeamNumbers)
            match.calculatedData.sdPredictedBlueScore = self.stdDevPredictedScoreForAllianceNumbers(match.blueAllianceTeamNumbers)
            match.calculatedData.sdPredictedRedScore = self.stdDevPredictedScoreForAllianceNumbers(match.redAllianceTeamNumbers)
            match.calculatedData.predictedBlueRPs = self.predictedRPsForAllianceForMatch(False, match)
            match.calculatedData.predictedRedRPs = self.predictedRPsForAllianceForMatch(True, match)
            match.calculatedData.numDefensesCrossedByBlue = self.numDefensesCrossedInMatch(False, match)
            match.calculatedData.numDefensesCrossedByRed = self.numDefensesCrossedInMatch(True, match)
            match.calculatedData.actualBlueRPs = self.RPsGainedFromMatchForAlliance(True, match)
            match.calculatedData.actualRedRPs = self.RPsGainedFromMatchForAlliance(False, match)

    def restoreComp(self):
        self.TIMDs = self.comp.TIMDs
        self.matches = self.comp.matches

    def doFirstTeamCalculations(self):
        for team in self.comp.teams:
            self.doFirstCalculationsForTeam(team)
        self.getAverageTeam()

    def doSecondTeamCalculations(self):
        for team in self.comp.teams:
            self.doSecondCalculationsForTeam(team)
        self.getAverageTeam()

    def doMatchesCalculations(self):
        for match in self.comp.matches:
            self.doFirstCalculationsForMatch(match)

    def doCalculations(self, FBC):
        self.comp.sdRScores = self.sdOfRValuesAcrossCompetition()
        for timd in self.comp.TIMDs:
        	self.doFirstCalculationsForTIMD(timd)
        for timd in self.comp.TIMDs:
        	self.doSecondCalculationsForTIMD(timd)
        self.restoreComp()
        for team in self.comp.teams:
            self.doFirstCalculationsForTeam(team)
        self.doFirstCalculationsForTeam(self.averageTeam)
        self.restoreComp()
        for match in self.comp.matches:
            self.doFirstCalculationsForMatch(match)
        for team in self.comp.teams:
            self.doSecondCalculationsForTeam(team)
        self.doSecondCalculationsForTeam(self.averageTeam)
        for team in self.comp.teams:
            if team in self.teamsWithMatchesCompleted():
                print "Writing team " + str(team.number) + " to Firebase..."
                FBC.addCalculatedTeamDataToFirebase(team)
        for timd in self.comp.TIMDs:
            if self.timdIsCompleted(timd):
                print "Writing team " + str(timd.teamNumber) + " in match " + str(timd.matchNumber) + " to Firebase..."
                FBC.addCalculatedTIMDataToFirebase(timd)
        for match in self.comp.matches:
            if self.matchIsCompleted(match):
                print "Writing match " + str(match.number) + " to Firebase..."
                FBC.addCalculatedMatchDataToFirebase(match)

                # for team in self.comp.teams:
                # timds = self.getCompletedTIMDsForTeam(team)
                #
                # print("Calculating TIMDs for team " + str(team.number)) + "... "
                # for timd in timds:

        # Competition metrics
        if self.numPlayedMatchesInCompetition() > 0:
            self.comp.averageScore = self.avgCompScore()
