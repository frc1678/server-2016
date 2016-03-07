import math
from operator import attrgetter
import pdb

import numpy as np
import scipy as sp
import scipy.stats as stats
import matplotlib.pyplot as plt

import CacheModel as cache
import DataModel
import utils
import time


class Calculator(object):
    """docstring for Calculator"""

    def __init__(self, competition):
        super(Calculator, self).__init__()
        self.comp = competition
        # self.comp.TIMDs = filter(lambda timd: timd.matchNumber <= 12, self.comp.TIMDs)
        # self.comp.matches = filter(lambda m: m.number <= 12, self.comp.matches)
        self.categories = ['a', 'b', 'c', 'd', 'e']
        self.ourTeamNum = 4767
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
        self.averageTeam.name = 'Average Team'
        self.cachedComp = cache.CachedCompetitionData()
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
        return self.cachedComp.teamsWithMatchesCompleted

    def findTeamsWithMatchesCompleted(self):
        return [team for team in self.comp.teams if len(self.getCompletedTIMDsForTeam(team)) > 0]

    def teamsWhoHaveFacedDefense(self, defenseKey):
        return filter(lambda t: self.teamFacedDefense(t, defenseKey), self.comp.teams)

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
        return len(self.getCompletedTIMDsForMatchNumber(match.number)) == 6 and self.matchHasValuesSet(match)

    def getAllTIMDsForMatch(self, match):
        return [timd for timd in self.TIMDs if timd.matchNumber == match.number]

    def matchHasAllTeams(self, match):
        return len(self.getAllTIMDsForMatch(match)) == 6

    # TIMD utility functions
    def getTIMDsForTeamNumber(self, teamNumber):
        if teamNumber == -1:
            return self.TIMDs
        return [timd for timd in self.TIMDs if timd.teamNumber == teamNumber]

    def getCompletedTIMDsForTeamNumber(self, teamNumber):
        return filter(self.timdIsCompleted, self.getTIMDsForTeamNumber(teamNumber))

    def getCompletedTIMDsForTeam(self, team):
        cachedData = self.cachedTeamDatas[team.number]
        return cachedData.completedTIMDs

    def getTIMDsForMatchNumber(self, matchNumber):
        return [timd for timd in self.TIMDs if timd.matchNumber == matchNumber]

    def getCompletedTIMDsForMatchNumber(self, matchNumber):
        return filter(self.timdIsCompleted, self.getTIMDsForMatchNumber(matchNumber))

    def getTIMDForTeamNumberAndMatchNumber(self, teamNumber, matchNumber):
        return [timd for timd in self.getTIMDsForTeamNumber(teamNumber) if timd.matchNumber == matchNumber][0]

    def getCompletedTIMDsInCompetition(self):
        return [timd for timd in self.TIMDs if self.timdIsCompleted(timd)]

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
        m = self.getMatchForNumber(timd.matchNumber)
        isCompleted = m.redDefensePositions != None and m.blueDefensePositions != None
        for key, value in utils.makeDictFromTIMD(timd).items():
            if key not in self.exceptedKeys and value == None:
                isCompleted = False
        return isCompleted

    matchExceptedKeys = ['calculatedData']
    def matchHasValuesSet(self, match):
        isCompleted = True
        for key, value in utils.makeDictFromMatch(match).items():
            if key not in self.matchExceptedKeys and value == None:
                isCompleted = False
        return isCompleted

    def retrieveCompletedTIMDsForTeam(self, team):
        return self.getCompletedTIMDsForTeamNumber(team.number)

    # Calculated Team Data
    def getAverageForDataFunctionForTeam(self, team, dataFunction):
        # validTIMDs = filter(lambda timd: dataFunction(timd) != None, self.getCompletedTIMDsForTeam(team))
        return np.mean(map(dataFunction, self.getCompletedTIMDsForTeam(team)))

    def getSumForDataFunctionForTeam(self, team, dataFunction):
        return sum(map(dataFunction, self.getCompletedTIMDsForTeam(team)))

    def getStandardDeviationForDataFunctionForTeam(self, team, dataFunction):
        validTIMDs = filter(lambda timd: dataFunction(timd) != None, self.getCompletedTIMDsForTeam(team))
        return np.std(map(dataFunction, validTIMDs))

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
        return utils.rms([team.calculatedData.sdSuccessfulDefenseCrossesTele[dKey] for dKey in self.defenseDictionary[category] if self.teamFacedDefense(team, dKey)])

    def stdDevForPredictedDefenseScoreForAllianceForCategory(self, alliance, category):
        mean = self.predictedTeleDefensePointsForAllianceForCategory(alliance, category)
        getStdDevFunction = lambda t: self.stdDevNumCrossingsTeleForTeamForCategory(t, category)
        stdDev = utils.sumStdDevs(map(getStdDevFunction, alliance))
        value = self.monteCarloForMeanForStDevForValueFunction(mean, stdDev, lambda crossings: 5 * min(crossings, 2))
        return value

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

    def getTeamFacedDefense(self, team, defenseKey):
        return self.numTimesTeamFacedDefense(team, defenseKey) > 0 

    def teamFacedDefense(self, team, defenseKey):
        return defenseKey in self.cachedTeamDatas[team.number].defensesFaced

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
            [defenseRetrievalFunction(t) for t in self.teamsWhoHaveFacedDefense(defenseKey)])
        teamAverageDefenseCrossings = defenseRetrievalFunction(team) if defenseRetrievalFunction(team) != None else 0
        competitionDefenseSightings = self.numTimesCompetitionFacedDefense(defenseKey)
        if competitionDefenseSightings == 0:
            return None
        teamDefenseSightings = self.numTimesTeamFacedDefense(team, defenseKey)
        competitionTotalNumberOfDefenseSightings = 5 * len(self.getCompletedTIMDsInCompetition())
        teamTotalNumberOfDefenseSightings = 5 * len(self.getCompletedTIMDsForTeam(team))
        proportionOfCompetitionDefenseSightings = competitionDefenseSightings / competitionTotalNumberOfDefenseSightings if competitionTotalNumberOfDefenseSightings > 0 else 0
        proportionOfTeamDefenseSightings = teamDefenseSightings / teamTotalNumberOfDefenseSightings if teamTotalNumberOfDefenseSightings > 0 else 0
        theta = sum([self.betaForTeamForDefense(team, dKey) for dKey in self.defenseList if
                     self.betaForTeamForDefense(team, dKey) != None])  # TODO: Rename theta something better
        return (averageOfDefenseCrossingsAcrossCompetition * theta + teamAverageDefenseCrossings * teamDefenseSightings) / (teamDefenseSightings + 1)

    def listOfSuperDataPointsForTIMD(self, timd):
        return [timd.rankTorque, timd.rankSpeed, timd.rankEvasion, timd.rankDefense, timd.rankBallControl]

    def rValuesForAverageFunctionForDict(self, averageFunction, d):
        impossible = True
        values = map(averageFunction, self.teamsWithMatchesCompleted())
        initialValue = values[0]
        for value in values[1:]:
            if value != initialValue: impossible == False
        if impossible: 
            zscores = [0.0 for v in values]
        else: 
            zscores = stats.zscore(values)
        for i in range(len(self.teamsWithMatchesCompleted())):
            d[self.teamsWithMatchesCompleted()[i].number] = zscores[i]

    torqueWeight = 0.2
    ballControlWeight = 0.2
    evasionWeight = 0.2
    defenseWeight = 0.2
    speedWeight = 0.2
    def drivingAbilityForTIMD(self, timd):
        return (self.torqueWeight * timd.rankTorque) + (
            self.ballControlWeight * timd.rankBallControl) + (
            self.evasionWeight * timd.rankEvasion) + (
            self.defenseWeight * timd.rankDefense) + (
            self.speedWeight * timd.rankSpeed)

    def drivingAbility(self, team, match):
        return self.drivingAbilityForTIMD(self.getTIMDForTeamNumberAndMatchNumber(team, match))

    def predictedCrossingsForDefenseCategory(self, team, category):
        return np.mean([team.calculatedData.predictedSuccessfulCrossingsForDefenseTele[dKey] for dKey in self.defenseDictionary[category] if self.teamFacedDefense(team, dKey)]) # TODO: Update with actual correct key

    def predictedCrossingsForDefense(self, team, defenseKey):
        return team.calculatedData.predictedSuccessfulCrossingsForDefenseTele[defenseKey]

    def getPredictedCrossingsForAllianceForDefense(self, alliance, defenseKey):
        predictedCrossingsRetrievalFunction = lambda t: self.predictedCrossingsForDefense(t, defenseKey)
        return sum(map(predictedCrossingsRetrievalFunction, alliance))

    def getPredictedCrossingsForAllianceForCategory(self, alliance, category):
        predictedCrossingsRetrievalFunction = lambda t: self.predictedCrossingsForDefenseCategory(t, category)
        return sum(map(predictedCrossingsRetrievalFunction, alliance))

    def predictedTeleDefensePointsForAllianceForCategory(self, alliance, category):
        return 5 * min(self.getPredictedCrossingsForAllianceForCategory(alliance, category), 2)

    def predictedTeleDefensePointsForAllianceForDefense(self, alliance, defenseKey):
        return 5 * min(self.getPredictedCrossingsForAllianceForDefense(alliance, defenseKey), 2)

    def predictedScoreForAllianceWithNumbers(self, allianceNumbers):
        return self.predictedScoreForAlliance(self.teamsForTeamNumbersOnAlliance(allianceNumbers))

    def replaceWithAverageIfNecessary(self, team):
        return team if self.calculatedDataHasValues(team.calculatedData) else self.averageTeam

    def stdDevPredictedScoreForAlliance(self, alliance):
        alliance = map(self.replaceWithAverageIfNecessary, alliance)
        # print "Tele"
        allianceTeleopShotPointStdDev = utils.sumStdDevs(map(lambda t: t.calculatedData.sdTeleopShotAbility, alliance))
        # print "Siege"
        allianceSiegePointsStdDev = utils.sumStdDevs(map(lambda t: t.calculatedData.sdSiegeAbility, alliance))
        # print "Auto"
        allianceAutoPointsStdDev = utils.sumStdDevs(map(lambda t: t.calculatedData.sdAutoAbility, alliance))
        # print "Defense"
        allianceDefensePointsTeleStdDev = utils.sumStdDevs(map(lambda cKey: self.stdDevForPredictedDefenseScoreForAllianceForCategory(alliance, cKey), self.categories))
        # print "Done"
        return utils.sumStdDevs([allianceTeleopShotPointStdDev,
                                 allianceSiegePointsStdDev,
                                 allianceAutoPointsStdDev,
                                 allianceDefensePointsTeleStdDev])


    def stdDevPredictedScoreForAllianceNumbers(self, allianceNumbers):
        return self.stdDevPredictedScoreForAlliance(self.teamsForTeamNumbersOnAlliance(allianceNumbers))

    def predictedScoreForAlliance(self, alliance):
        alliance = map(self.replaceWithAverageIfNecessary, alliance)
        # print "Starting!"
        allianceTeleopShotPoints = sum(
            [t.calculatedData.teleopShotAbility for t in alliance if t.calculatedData.teleopShotAbility])
        # print "Teleop"
        allianceSiegePoints = sum(
            [t.calculatedData.siegeAbility for t in alliance if t.calculatedData.siegeAbility])
        # print "Siege"
        allianceAutoPoints = sum(
            [t.calculatedData.autoAbility for t in alliance if t.calculatedData.autoAbility])
        # print "Auto"
        alliancePredictedCrossingsRetrievalFunction = lambda c: self.predictedTeleDefensePointsForAllianceForCategory(alliance, c)
        allianceDefensePointsTele = sum(map(alliancePredictedCrossingsRetrievalFunction, self.categories))
        # print "Predicted Crossings"
        return allianceTeleopShotPoints + allianceSiegePoints + allianceAutoPoints + allianceDefensePointsTele
        

    def predictedScoreForAllianceWithDefenseCombination(self, alliance, defenses):
        alliance = map(self.replaceWithAverageIfNecessary, alliance)
        # print "Starting!"
        allianceTeleopShotPoints = sum(
            [t.calculatedData.teleopShotAbility for t in alliance if t.calculatedData.teleopShotAbility])
        # print "Teleop"
        allianceSiegePoints = sum(
            [t.calculatedData.siegeAbility for t in alliance if t.calculatedData.siegeAbility])
        # print "Siege"
        allianceAutoPoints = sum(
            [t.calculatedData.autoAbility for t in alliance if t.calculatedData.autoAbility])
        # print "Auto"
        alliancePredictedCrossingsRetrievalFunction = lambda dKey: self.predictedTeleDefensePointsForAllianceForDefense(
            alliance, dKey)
        allianceDefensePointsTele = sum(map(alliancePredictedCrossingsRetrievalFunction, defenses))
        # print "Predicted Crossings"
        total = allianceTeleopShotPoints + allianceSiegePoints + allianceAutoPoints + allianceDefensePointsTele
        return total

    def defenseCombinations(self):
        return self.getDefenseCombinations(self.categories)

    def getDefenseCombinations(self, categories):
        if len(categories) == 0:
            return []
        combos = []
        for defense in self.defenseDictionary[categories[0]]:
            for combo in self.getDefenseCombinations(categories[1:]):
                combos.append([defense].append(combo))
        return combos

    def stanDevForDefenseCategoryForKeyRetrievalFunctionForTeam(self, team, keyRetrievalFunction, category):
        values = map(lambda dKey: keyRetrievalFunction(team)[dKey], self.defenseDictionary[category])
        return utils.rms(values)

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
        return utils.rms(map(lambda dKey: sumDefenseCrossingsDict[dKey], filter(lambda d: self.teamFacedDefense(team, d), self.defenseDictionary[category])))

    def getDefenseDamageChanceForAllianceForCategory(self, alliance, category):
        crossings = sum(map(lambda t: self.predictedCrossingsForDefenseCategory(t, category), alliance))
        stdDev = utils.sumStdDevs(map(lambda t: self.standardDeviationForTeamForCategory(t, category), alliance))
        return self.probabilityDensity(2.0, crossings, stdDev)

    def breachChanceForAlliance(self, alliance):
        alliance = map(self.replaceWithAverageIfNecessary, alliance)
        defenseDamageChances = [self.getDefenseDamageChanceForAllianceForCategory(alliance, cKey) for cKey in self.categories]
        defenseDamageChances.remove(min(defenseDamageChances))
        return np.prod(defenseDamageChances)

    def breachChanceForAllianceNumbers(self, allianceNumbers):
        return self.breachChanceForAlliance(self.teamsForTeamNumbersOnAlliance(allianceNumbers))

    def getBreachChanceForMatchForAllianceIsRed(self, match, allianceIsRed):
        return match.calculatedData.redBreachChance if allianceIsRed else match.calculatedData.blueBreachChance

    def getCaptureChanceForMatchForAllianceIsRed(self, match, allianceIsRed):
        return match.calculatedData.redCaptureChance if allianceIsRed else match.calculatedData.blueCaptureChance

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
        alliance = map(self.replaceWithAverageIfNecessary, alliance)
        return self.probabilityDensity(8.0, self.numShotsForAlliance(alliance), self.stdDevNumShotsForAlliance(alliance))

    def captureChanceForAllianceNumbers(self, allianceNumbers):
        return self.captureChanceForAlliance(self.teamsForTeamNumbersOnAlliance(allianceNumbers))

    def predictedRPsForAllianceForMatch(self, allianceIsRed, match):
        alliance = self.getAllianceForMatch(match, allianceIsRed)
        alliance = map(self.replaceWithAverageIfNecessary, alliance)

        breachRPs = self.getBreachChanceForMatchForAllianceIsRed(match, allianceIsRed)
        captureRPs = self.getCaptureChanceForMatchForAllianceIsRed(match, allianceIsRed)

        predictedScore  = self.predictedScoreForMatchForAlliance(match, allianceIsRed)
        opposingPredictedScore = self.predictedScoreForMatchForAlliance(match, not allianceIsRed)
        sdPredictedScore = self.sdPredictedScoreForMatchForAlliance(match, allianceIsRed)
        sdOpposingPredictedScore = self.sdPredictedScoreForMatchForAlliance(match, not allianceIsRed)
        sampleSize = self.sampleSizeForMatchForAlliance(alliance)
        opposingSampleSize = self.sampleSizeForMatchForAlliance(alliance)
        tscoreRPs = self.welchsTest(predictedScore,
                                       opposingPredictedScore,
                                       sdPredictedScore,
                                       sdOpposingPredictedScore,
                                       sampleSize,
                                       opposingSampleSize)

        scoreRPs = tscoreRPs * stats.t.pdf(tscoreRPs, np.mean([sampleSize, opposingSampleSize]))
        return breachRPs + captureRPs + scoreRPs

    def welchsTest(self, mean1, mean2, std1, std2, sampleSize1, sampleSize2):
        if std1 == 0.0 or std2 == 0.0:
            return float(mean1 > mean2)
        numerator = mean1 - mean2
        denominator = ((std1 ** 2) / sampleSize1 + (std2 ** 2) / sampleSize2) ** 0.5
        return numerator / denominator

    def calculateCitrusDPRs(self):
        teamsInValidMatches = self.teamsWithMatchesCompleted()
        numTimesTogetherFunction = lambda t1, t2: sum(
            map(lambda m: self.teamsAreOnSameAllianceInMatch(t1, t2, m), self.getCompletedMatchesForTeam(t1)))
        getRowForTeamFunction = lambda t1: map(lambda t: numTimesTogetherFunction(t1, t), teamsInValidMatches)
        matrixOfMatchesTogether = np.matrix(map(getRowForTeamFunction, teamsInValidMatches))
        if np.linalg.det(matrixOfMatchesTogether) == 0:
            print 'Cannot invert matrix.'
            return None
        else:
            inverseMatrixOfMatchOccurrences = np.linalg.inv(matrixOfMatchesTogether)
        deltaFunction = lambda t: [sum(map(self.predictedScoreForAlliance, self.getAllTeamOppositionAlliances(t))) - sum(
            self.getTeamMatchScores(t))]
        teamDeltas = map(deltaFunction, teamsInValidMatches)
        citrusDPRMatrix = np.dot(inverseMatrixOfMatchOccurrences, teamDeltas)
        for i in range(len(teamsInValidMatches)):
            self.cachedComp.citrusDPRs[teamsInValidMatches[i].number] = citrusDPRMatrix.item(i, 0)
        self.cachedComp.citrusDPRs[-1] = np.mean(citrusDPRMatrix)

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

    def getOurTeam(self):
        return self.getTeamForNumber(self.ourTeamNum)

    gamma = 0.5
    def secondPickAbilityForTeamWithTeam(self, team1, team2):
        if team1.calculatedData.citrusDPR != None:
            return self.gamma * team1.calculatedData.citrusDPR + (1 - self.gamma) * self.predictedScoreForAlliance([self.getOurTeam(), team2, team1])
        else:
            return self.predictedScoreForAlliance([self.getOurTeam(), team2, team1])

    def secondPickAbility(self, team):
        secondPickAbilityDict = {}
        secondPickAbilityFunction = lambda t: utils.setDictionaryValue(secondPickAbilityDict, t.number,
                                                                       self.secondPickAbilityForTeamWithTeam(team, t))
        map(secondPickAbilityFunction, self.teamsWithMatchesCompleted())
        return secondPickAbilityDict

    def overallSecondPickAbility(self, team):
        calcData = team.calculatedData
        teams = self.teamsSortedByRetrievalFunctions([lambda t: calcData.secondPickAbility[t.number]])[:16]
        return np.mean(map(lambda t: calcData.secondPickAbility[t.number], teams))

    def teamsSortedByRetrievalFunctions(self, retrievalFunctions):
        teams = self.teamsWithMatchesCompleted()
        mappableRetrievalFunction = lambda f: teams.sort(key=f)
        map(mappableRetrievalFunction, retrievalFunctions[::-1])
        return teams       

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
        return map(lambda m: self.getTeamScoreInMatch(team, m), self.getCompletedMatchesForTeam(team))

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
        return np.sum(map(lambda t: len(self.getCompletedTIMDsForTeam(t)), alliance)) # TODO:WATCHOUT!!!

    def getAvgNumCompletedTIMDsForAlliance(self, alliance):
        return self.getAvgNumCompletedTIMDsForTeamsOnAlliance(alliance)

    def sampleSizeForMatchForAlliance(self, alliance):
        return self.getAvgNumCompletedTIMDsForAlliance(alliance)

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
            return self.teamsSortedByRetrievalFunctions(retrievalFunctions).index(team)

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

    def setDefenseValuesForForAverageTeam(self, retrievalFunction, dataModification):
        keyDict = retrievalFunction(self.averageTeam)
        getValueFunc = lambda x, dKey: retrievalFunction(x)[dKey] if self.teamFacedDefense(x, dKey) else None
        avgFunc = lambda dKey: dataModification([getValueFunc(t, dKey) for t in self.teamsWithCalculatedData() if getValueFunc(t, dKey) != None])
        dictSetFunction = lambda dKey: utils.setDictionaryValue(keyDict, dKey, avgFunc(dKey))
        map(dictSetFunction, self.defenseList)

    def timdsWithDefense(self, defenseKey):
        return filter(lambda t: self.defenseFacedForTIMD(t, defenseKey), self.getCompletedTIMDsInCompetition())

    def getAverageAcrossCompetitionTeamSawDefense(self, team, defenseKey, retrievalFunction):
        return np.mean(map(retrievalFunction, self.timdsWithDefense(defenseKey)))

    def getAvgOfDefensesForRetrievalFunctionForTeam(self, team, teamRetrievalFunction):
        defenseRetrievalFunctions = self.getDefenseRetrievalFunctions(teamRetrievalFunction)
        return np.mean(map(lambda retrievalFunction: retrievalFunction(team), defenseRetrievalFunctions))

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
        return np.mean(map(dataFunction, self.teamsWithCalculatedData()))

    def getStandardDeviationOfDataFunctionAcrossCompetition(self, dataFunction):
        return utils.rms(map(dataFunction, self.teamsWithCalculatedData()))

    def cacheFirstTeamData(self):
        for team in self.comp.teams:
            self.doCachingForTeam(team)
        self.doCachingForTeam(self.averageTeam)
        self.cachedComp.teamsWithMatchesCompleted = self.findTeamsWithMatchesCompleted()
        # self.comp.sdRScores = self.sdOfRValuesAcrossCompetition()

    def scoreContributionForTeamForMatch(self, team, match):
        alliance = self.getAllianceForTeamInMatch(team, match)
        alliance.remove(team)
        return self.getTeamScoreInMatch(team, match) - self.predictedScoreForAlliance(alliance)

    def rScoreParams(self):
        return [(lambda t: t.calculatedData.avgSpeed, self.cachedComp.speedZScores),
                    (lambda t: t.calculatedData.avgTorque, self.cachedComp.torqueZScores),
                    (lambda t: t.calculatedData.avgEvasion, self.cachedComp.evasionZScores),
                    (lambda t: t.calculatedData.avgDefense, self.cachedComp.defenseZScores),
                    (lambda t: t.calculatedData.avgBallControl, self.cachedComp.ballControlZScores),
                    (lambda t: t.calculatedData.avgDrivingAbility, self.cachedComp.drivingAbilityZScores)]

    def cacheSecondTeamData(self):
        # for func, dictionary in self.rScoreParams():
        #     self.rValuesForAverageFunctionForDict(func, dictionary)
        map(lambda (func, dictionary): self.rValuesForAverageFunctionForDict(func, dictionary), self.rScoreParams())
        for team in self.comp.teams:
            self.doSecondCachingForTeam(team)
        self.doSecondCachingForTeam(self.averageTeam)

    def doCachingForTeam(self, team):
        cachedData = self.cachedTeamDatas[team.number]
        cachedData.completedTIMDs = self.retrieveCompletedTIMDsForTeam(team)
        cachedData.defensesFaced = filter(lambda dKey: self.getTeamFacedDefense(team, dKey), self.defenseList)

    def doSecondCachingForTeam(self, team):
        cachedData = self.cachedTeamDatas[team.number]
        map(lambda dKey: utils.setDictionaryValue(cachedData.alphas, dKey, self.alphaForTeamForDefense(team, dKey)), self.defenseList)

    def getFirstCalculationsForAverageTeam(self): 
        print "Beginning first calculations for team: " + str(self.averageTeam.number) + ", " + self.averageTeam.name
        a = self.averageTeam.calculatedData

        #Super Averages
        a.avgTorque = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgTorque)  # Checked
        a.avgSpeed = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgSpeed)
        a.avgEvasion = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgEvasion)  # Checked
        a.avgDefense = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgDefense)  # Checked
        a.avgBallControl = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgBallControl)  # Checked
        a.avgDrivingAbility = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgDrivingAbility)

        a.disabledPercentage = self.getAverageOfDataFunctionAcrossCompetition( 
            lambda t: t.calculatedData.disabledPercentage)
        a.incapacitatedPercentage = self.getAverageOfDataFunctionAcrossCompetition( 
            lambda t: t.calculatedData.incapacitatedPercentage)
        a.disfunctionalPercentage = a.disabledPercentage + a.incapacitatedPercentage

        #Auto
        a.autoAbility = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.autoAbility)
        a.avgHighShotsAuto = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgHighShotsAuto)  # Checked
        a.avgLowShotsAuto = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgLowShotsAuto)  # Checked 
        a.reachPercentage = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.reachPercentage) 
        a.highShotAccuracyAuto = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.highShotAccuracyAuto)  # Checked
        a.lowShotAccuracyAuto = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.lowShotAccuracyAuto)  # Checked
        a.numAutoPoints = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.numAutoPoints)  # Checked
        a.avgMidlineBallsIntakedAuto = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgMidlineBallsIntakedAuto)
        a.sdMidlineBallsIntakedAuto = self.getStandardDeviationOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.sdMidlineBallsIntakedAuto)
        a.sdHighShotsAuto = self.getStandardDeviationOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.sdHighShotsAuto)  # Checked
        a.sdLowShotsAuto = self.getStandardDeviationOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.sdLowShotsAuto)  # Checked
        a.sdBallsKnockedOffMidlineAuto = self.getStandardDeviationOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.sdBallsKnockedOffMidlineAuto)  # Checked
        self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.avgSuccessfulTimesCrossedDefensesAuto, lambda x: np.mean(x))
        self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.avgFailedTimesCrossedDefensesAuto, lambda x: np.mean(x))
        self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.avgTimeForDefenseCrossAuto, lambda x: np.mean(x))
        self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.sdSuccessfulDefenseCrossesAuto, lambda x: utils.rms(x))
        self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.sdFailedDefenseCrossesTele, lambda x: utils.rms(x))

        #Tele
        a.scalePercentage = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.scalePercentage)
        a.challengePercentage = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.challengePercentage)
        a.avgGroundIntakes = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgGroundIntakes)
        a.avgBallsKnockedOffMidlineAuto = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgBallsKnockedOffMidlineAuto)  # Checked
        a.avgShotsBlocked = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgShotsBlocked)  # Checked
        a.avgHighShotsTele = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgHighShotsTele)
        a.avgLowShotsTele = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgLowShotsTele)  # Checked
        a.highShotAccuracyTele = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.highShotAccuracyTele)
        a.lowShotAccuracyTele = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.lowShotAccuracyTele)
        a.teleopShotAbility = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.teleopShotAbility)  # Checked
        a.siegeConsistency = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.challengePercentage + t.calculatedData.scalePercentage)  # Checked
        a.siegeAbility = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.siegeAbility)  # Checked
        a.sdHighShotsTele = self.getAverageOfDataFunctionAcrossCompetition(lambda
            t: t.calculatedData.sdHighShotsTele)  # Checked
        a.sdLowShotsTele = self.getAverageOfDataFunctionAcrossCompetition(lambda
            t: t.calculatedData.sdLowShotsTele)  # Checked
        a.sdGroundIntakes = self.getAverageOfDataFunctionAcrossCompetition(lambda
            t: t.calculatedData.sdGroundIntakes)  # Checked
        a.sdShotsBlocked = self.getAverageOfDataFunctionAcrossCompetition(lambda
            t: t.calculatedData.sdShotsBlocked)  # Checked
        a.sdTeleopShotAbility = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.teleopShotAbility)
        a.sdSiegeAbility = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.siegeAbility)
        a.sdAutoAbility = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.autoAbility)
        self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.avgSuccessfulTimesCrossedDefensesTele, lambda x: np.mean(x))
        self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.avgFailedTimesCrossedDefensesTele, lambda x: np.mean(x))
        self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.avgTimeForDefenseCrossTele, lambda x: np.mean(x))
        self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.sdSuccessfulDefenseCrossesTele, lambda x: utils.rms(x))
        self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.sdFailedDefenseCrossesTele, lambda x: utils.rms(x))

        a.numScaleAndChallengePoints = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.numScaleAndChallengePoints) # Checked
        a.breachPercentage = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.breachPercentage)

    def getSecondCalculationsForAverageTeam(self):
        a = self.averageTeam.calculatedData

        a.RScoreTorque = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.RScoreTorque)
        a.RScoreSpeed = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.RScoreSpeed)
        a.RScoreEvasion = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.RScoreEvasion)
        a.RScoreDefense = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.RScoreDefense)
        a.RScoreBallControl = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.RScoreBallControl)
        a.RScoreDrivingAbility = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.RScoreDrivingAbility)
        a.avgSuccessfulTimesCrossedDefenses = utils.dictSum(a.avgSuccessfulTimesCrossedDefensesAuto,
                                                            a.avgSuccessfulTimesCrossedDefensesTele)
        a.firstPickAbility = self.firstPickAbility(self.averageTeam)
        a.numRPs = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.numRPs)
        a.predictedNumRPs = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.predictedNumRPs)




    def doFirstCalculationsForTeam(self, team):
        if len(self.getCompletedTIMDsForTeam(team)) <= 0:
            print "No Complete TIMDs for team " + str(team.number) + ", " + str(team.name)
        else:
            print("Beginning first calculations for team: " + str(team.number) + ", " + str(team.name))
            # Super Scout Averages

            if not self.calculatedDataHasValues(team.calculatedData):
                team.calculatedData = DataModel.CalculatedTeamData()
            t = team.calculatedData

            t.avgTorque = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankTorque)  # Checked
            t.avgSpeed = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankSpeed)
            t.avgEvasion = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankEvasion)  # Checked
            t.avgDefense = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankDefense)  # Checked
            t.avgBallControl = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankBallControl)  # Checked
            t.avgDrivingAbility = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.calculatedData.drivingAbility)

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
            t.numScaleAndChallengePoints = self.numScaleAndChallengePointsForTeam(team)  # Checked
            t.breachPercentage = self.getAverageForDataFunctionForTeam(team, lambda timd: 
                utils.convertFirebaseBoolean(self.teamDidBreachInMatch(team, self.getMatchForNumber(timd.matchNumber))))

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
           
    def doBetweenFirstAndSecondCalculationsForTeams(self):
        for team in self.comp.teams:
            self.doBetweenFirstAndSecondCalculationsForTeam(team)
        self.doBetweenFirstAndSecondCalculationsForTeam(self.averageTeam)

    def doBetweenFirstAndSecondCalculationsForTeam(self, team):
        if len(self.getCompletedTIMDsForTeam(team)) <= 0:
            print "No Complete TIMDs for team " + str(team.number) + ", " + str(team.name)
        else:
            print("Beginning second calculations for team: " + str(team.number) + ", " + str(team.name))
            #print("#")
            map(lambda dKey: utils.setDictionaryValue(
                team.calculatedData.predictedSuccessfulCrossingsForDefenseTele, # TODO: Update with the correct key
                dKey, 
                self.predictedCrosses(team, dKey)),
                self.defenseList)


    def doSecondCalculationsForTeam(self, team):
        if len(self.getCompletedTIMDsForTeam(team)) <= 0:
            print "No Complete TIMDs for team " + str(team.number) + ", " + str(team.name)
        else:
            print("Beginning second calculations for team: " + str(team.number) + ", " + str(team.name))
            #print("#")

            t = team.calculatedData
            t.RScoreTorque = self.cachedComp.torqueZScores[team.number]
            t.RScoreSpeed = self.cachedComp.speedZScores[team.number]
            t.RScoreEvasion = self.cachedComp.evasionZScores[team.number]
            t.RScoreDefense = self.cachedComp.defenseZScores[team.number]
            t.RScoreBallControl = self.cachedComp.ballControlZScores[team.number]
            t.RScoreDrivingAbility = self.cachedComp.drivingAbilityZScores[team.number]
            t.avgSuccessfulTimesCrossedDefenses = utils.dictSum(t.avgSuccessfulTimesCrossedDefensesAuto,
                                                                t.avgSuccessfulTimesCrossedDefensesTele)
            t.firstPickAbility = self.firstPickAbility(team)
            # t.citrusDPR = 12.0
            t.predictedNumRPs = self.predictedNumberOfRPs(team)
            t.actualNumRPs = self.actualNumberOfRPs(team)
            t.firstPickAbility = self.firstPickAbility(team) # Checked	
            t.secondPickAbility = self.secondPickAbility(team) # Checked
            t.overallSecondPickAbility = self.overallSecondPickAbility(team) # Checked
            if team.number in self.cachedComp.citrusDPRs: t.citrusDPR = self.cachedComp.citrusDPRs[team.number]
            t.numRPs = self.getSumForDataFunctionForTeam(team, lambda timd: timd.calculatedData.numRPs)
            t.actualSeed = self.getRankingForTeamByRetrievalFunctions(team, self.getSeedingFunctions()) # Checked
            t.predictedSeed = self.getRankingForTeamByRetrievalFunctions(team, self.getPredictedSeedingFunctions()) # Checked

    def doThirdCalculationsForTeam(self, team):
        if len(self.getCompletedTIMDsForTeam(team)) <= 0:
            print "No Complete TIMDs for team " + str(team.number) + ", " + str(team.name)
        else:
            print("Beginning third calculations for team: " + str(team.number) + ", " + str(team.name))
            t = team.calculatedData
            t.secondPickAbility = self.secondPickAbility(team) # Checked
            t.overallSecondPickAbility = self.overallSecondPickAbility(team) # Checked

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
            c.drivingAbility = self.drivingAbilityForTIMD(timd)
            c.siegeConsistency = utils.convertFirebaseBoolean(timd.didChallengeTele) + utils.convertFirebaseBoolean(timd.didScaleTele)
            c.numRPs = self.RPsGainedFromMatchForTeam(match, team)
            c.numAutoPoints = self.numAutoPointsForTIMD(timd)
            c.numScaleAndChallengePoints = c.siegeAbility  # they are the same
            c.numBallsIntakedOffMidlineAuto = 0.0
            # c.numBallsIntakedOffMidlineAuto = self.getAverageForDataFunctionForTeam(team, lambda timd: len(timd.ballsIntakedAuto if timd.ballsIntakedAuto != None else []))
            self.restoreComp()

    def doSecondCalculationsForTIMD(self, timd):
        if (not self.timdIsCompleted(timd)):
            print "TIMD is not complete for team " + str(timd.teamNumber) + " in match " + str(timd.matchNumber)
        else:
            print "Beginning second calculations for team " + str(timd.teamNumber) + " in match " + str(
                timd.matchNumber)
            c = timd.calculatedData
            team = self.getTeamForNumber(timd.teamNumber)
            match = self.getMatchForNumber(timd.matchNumber)


            self.matches = filter(lambda m: not self.teamInMatch(team, m) == (timd.matchNumber != m.number), self.comp.matches)
            self.TIMDs = filter(lambda t: t.matchNumber in [m.number for m in self.matches], self.comp.TIMDs)

            self.cacheFirstTeamData()
            self.doFirstTeamCalculations()
            self.cacheSecondTeamData()
            self.doBetweenFirstAndSecondCalculationsForTeams()
            self.doMatchesCalculations()
            self.calculateCitrusDPRs()
            self.doSecondTeamCalculations()

            c.RScoreTorque = team.calculatedData.RScoreTorque
            c.RScoreSpeed = team.calculatedData.RScoreSpeed
            c.RScoreEvasion = team.calculatedData.RScoreEvasion
            c.RScoreDefense = team.calculatedData.RScoreDefense
            c.RScoreBallControl = team.calculatedData.RScoreBallControl
            c.RScoreDrivingAbility = team.calculatedData.RScoreDrivingAbility
            c.firstPickAbility = team.calculatedData.firstPickAbility
            # c.secondPickAbility = team.calculatedData.secondPickAbility
            # c.citrusDPR = team.calculatedData.citrusDPR
            c.scoreContribution = self.scoreContributionForTeamForMatch(team, match)

            # c.secondPickAbility = {}
            # [utils.setDictionaryValue(c.secondPickAbility, team.number, 15.0) for team in self.comp.teams]
            # c.overallSecondPickAbility = team.calculatedData.overallSecondPickAbility
            self.restoreComp()


    def getOptimalDefensesForAlliance(self, alliance):
        optimalDefenseCombination, optimalScore = 100000, 100000
        defenseCombos = self.defenseCombinations()
        for combo in defenseCombos:
            comboScore = self.predictedScoreForAllianceWithDefenseCombination(combo)
            if comboScore < optimalScore:
                optimalDefenseCombination, optimalScore = combo, comboScore
        return optimalDefenseCombination

    def getOptimalDefensesForAllianceIsRedForMatch(self, allianceIsRed, match):
        alliance = self.getAllianceForMatch(match, allianceIsRed)
        alliance = map(self.replaceWithAverageIfNecessary, alliance)
        return self.getOptimalDefensesForAlliance(alliance)

    def doFirstCalculationsForMatch(self, match):
        print "Performing calculations for match Q" + str(match.number)
        if self.matchIsCompleted(match):
            match.calculatedData.actualBlueRPs = self.RPsGainedFromMatchForAlliance(True, match)
            match.calculatedData.actualRedRPs = self.RPsGainedFromMatchForAlliance(False, match)
            match.calculatedData.numDefensesCrossedByBlue = self.numDefensesCrossedInMatch(False, match)
            match.calculatedData.numDefensesCrossedByRed = self.numDefensesCrossedInMatch(True, match)
        # print "Breach Chance"
        match.calculatedData.blueBreachChance = self.breachChanceForAllianceNumbers(match.blueAllianceTeamNumbers)
        match.calculatedData.redBreachChance = self.breachChanceForAllianceNumbers(match.redAllianceTeamNumbers)
        # print "Capture Chance"
        match.calculatedData.blueCaptureChance = self.captureChanceForAllianceNumbers(match.blueAllianceTeamNumbers)
        match.calculatedData.redCaptureChance = self.captureChanceForAllianceNumbers(match.blueAllianceTeamNumbers)
        # print "Predicted Score"
        match.calculatedData.predictedBlueScore = self.predictedScoreForAllianceWithNumbers(match.blueAllianceTeamNumbers)
        match.calculatedData.predictedRedScore = self.predictedScoreForAllianceWithNumbers(match.redAllianceTeamNumbers)
        # print "SD Predicted Score"
        match.calculatedData.sdPredictedBlueScore = self.stdDevPredictedScoreForAllianceNumbers(match.blueAllianceTeamNumbers)
        match.calculatedData.sdPredictedRedScore = self.stdDevPredictedScoreForAllianceNumbers(match.redAllianceTeamNumbers)
        # print "Predicted RPs"
        match.calculatedData.predictedBlueRPs = self.predictedRPsForAllianceForMatch(False, match)
        match.calculatedData.predictedRedRPs = self.predictedRPsForAllianceForMatch(True, match)
        # print "Optimal"
        match.calculatedData.optimalBlueDefenses = self.getOptimalDefensesForAllianceIsRedForMatch(False, match)
        match.calculatedData.optimalRedDefenses = self.getOptimalDefensesForAllianceIsRedForMatch(True, match)
        # print "Done!"


    def restoreComp(self):
        self.TIMDs = self.comp.TIMDs
        self.matches = self.comp.matches

    def doFirstTeamCalculations(self):
        map(self.doFirstCalculationsForTeam, self.comp.teams)
        self.getFirstCalculationsForAverageTeam()

    def doSecondTeamCalculations(self):
        map(self.doSecondCalculationsForTeam, self.comp.teams)
        self.getSecondCalculationsForAverageTeam()

    def doMatchesCalculations(self):
        for match in self.comp.matches:
            self.doFirstCalculationsForMatch(match)
    def writeCalculationDiagnostic(self, time):
        with open('./diagnostics.txt', 'a') as file:
            file.write('Time: ' + str(time) + '    TIMDs: ' + str(len(self.getCompletedTIMDsInCompetition())) + '\n')
            file.close()

    def doCalculations(self, FBC):
        isData = len(self.getCompletedTIMDsInCompetition()) > 0
        if isData:
            startTime = time.time()
            for timd in self.comp.TIMDs:
            	self.doFirstCalculationsForTIMD(timd)
            for timd in self.comp.TIMDs:
            	self.doSecondCalculationsForTIMD(timd)
            self.restoreComp()
            self.cacheFirstTeamData()
            self.doFirstTeamCalculations()
            self.cacheSecondTeamData()
            self.doBetweenFirstAndSecondCalculationsForTeams()
            self.doMatchesCalculations()
            self.calculateCitrusDPRs()
            self.doSecondTeamCalculations()
            endTime = time.time()
            self.writeCalculationDiagnostic(endTime - startTime)
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
            # Competition metrics
            if self.numPlayedMatchesInCompetition() > 0:
                self.comp.averageScore = self.avgCompScore()
        else:
            print "No Data"



        
