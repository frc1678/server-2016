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

import multiprocessing
import copy
import warnings


class FirstTIMDThread(multiprocessing.Process):
    def __init__(self, timd, calculatedTIMDsList, calculator):
        super(FirstTIMDThread, self).__init__()
        self.timd = timd
        self.calculatedTIMDsList = calculatedTIMDsList
        self.calculator = calculator
        warnings.simplefilter('error', RuntimeWarning)

    def run(self):
        if (not self.calculator.timdIsCompleted(self.timd)):
            print "TIMD is not complete for team " + str(self.timd.teamNumber) + " in match " + str(self.timd.matchNumber)
            self.calculatedTIMDsList.append(self.timd)
        else:
            print "Beginning first calculations for team " + str(self.timd.teamNumber) + " in match " + str(self.timd.matchNumber)
            team = self.calculator.getTeamForNumber(self.timd.teamNumber)
            match = self.calculator.getMatchForNumber(self.timd.matchNumber)

            self.calculator.matches = filter(lambda m: not self.calculator.teamInMatch(team, m) == (self.timd.matchNumber != m.number), self.calculator.comp.matches)
            self.calculator.TIMDs = filter(lambda t: t.matchNumber in [m.number for m in self.calculator.matches], self.calculator.comp.TIMDs)

            if not self.calculator.TIMCalculatedDataHasValues(
                    self.timd.calculatedData): self.timd.calculatedData = DataModel.CalculatedTeamInMatchData()
            c = self.timd.calculatedData
            c.teleopShotAbility = self.calculator.getTIMDTeleopShotAbility(self.timd)
            c.highShotAccuracyTele = self.calculator.getTIMDHighShotAccuracyTele(self.timd)  # Checked
            c.highShotAccuracyAuto = self.calculator.getTIMDHighShotAccuracyAuto(self.timd)  # Checked
            c.lowShotAccuracyTele = self.calculator.getTIMDLowShotAccuracyTele(self.timd)  # Checked
            c.lowShotAccuracyAuto = self.calculator.getTIMDLowShotAccuracyAuto(self.timd)  # Checked
            c.siegeAbility = self.calculator.singleSiegeAbility(self.timd)
            c.autoAbility = self.calculator.autoAbility(self.timd)
            c.drivingAbility = self.calculator.drivingAbilityForTIMD(self.timd)
            c.siegeConsistency = utils.convertFirebaseBoolean(self.timd.didChallengeTele) + utils.convertFirebaseBoolean(self.timd.didScaleTele)
            c.numRPs = self.calculator.RPsGainedFromMatchForTeam(match, team)
            c.numAutoPoints = self.calculator.numAutoPointsForTIMD(self.timd)
            c.numScaleAndChallengePoints = c.siegeAbility  # they are the same
            c.highShotsAttemptedTele = self.timd.numHighShotsMadeTele + self.timd.numHighShotsMissedTele
            c.lowShotsAttemptedTele = self.timd.numLowShotsMadeTele + self.timd.numLowShotsMissedTele
            c.numBallsIntakedOffMidlineAuto = float(0.0)
            c.numTimesSuccesfulCrossedDefensesAuto = self.calculator.numCrossingsForTIMD(self.timd, self.timd.timesSuccessfulCrossedDefensesAuto)
            c.numTimesFailedCrossedDefensesAuto = self.calculator.numCrossingsForTIMD(self.timd, self.timd.timesFailedCrossedDefensesAuto)
            c.numTimesSuccesfulCrossedDefensesTele = self.calculator.numCrossingsForTIMD(self.timd, self.timd.timesSuccessfulCrossedDefensesTele)
            c.numTimesFailedCrossedDefensesTele = self.calculator.numCrossingsForTIMD(self.timd, self.timd.timesFailedCrossedDefensesTele)
            c.crossingsForDefensePercentageAuto = utils.dictQuotient(c.numTimesSuccesfulCrossedDefensesAuto, utils.dictSum(c.numTimesSuccesfulCrossedDefensesAuto, c.numTimesFailedCrossedDefensesAuto))
            c.crossingsForDefensePercentageTele = utils.dictQuotient(c.numTimesSuccesfulCrossedDefensesTele, utils.dictSum(c.numTimesSuccesfulCrossedDefensesTele, c.numTimesFailedCrossedDefensesTele))
            c.crossingTimeForDefenseAuto = self.calculator.valueCrossingsForTIMD(self.timd, self.timd.timesSuccessfulCrossedDefensesAuto)
            c.crossingTimeForDefenseTele = self.calculator.valueCrossingsForTIMD(self.timd, self.timd.timesSuccessfulCrossedDefensesTele)
            self.calculatedTIMDsList.append(self.timd)
            return 
            

class SecondTIMDThread(multiprocessing.Process):
    def __init__(self, timd, calculator):
        super(SecondTIMDThread, self).__init__()
        self.timd = timd
        self.calculator = calculator
        warnings.simplefilter('error', RuntimeWarning)

    def run(self):
        if (not self.calculator.timdIsCompleted(self.timd)):
            print "TIMD is not complete for team " + str(self.timd.teamNumber) + " in match " + str(self.timd.matchNumber)
        else:
            print "Beginning second calculations for team " + str(self.timd.teamNumber) + " in match " + str(
                self.timd.matchNumber)
            # print utils.makeDictFromTIMD(self.timd)
            c = self.timd.calculatedData
            team = self.calculator.getTeamForNumber(self.timd.teamNumber)
            match = self.calculator.getMatchForNumber(self.timd.matchNumber)
            # for match2 in self.calculator.comp.matches:
                # print utils.makeDictFromMatch(match2)
            self.calculator.cacheFirstTeamData()
            # print  "1"
            self.calculator.doFirstTeamCalculations()
            self.calculator.TIMDs = self.calculator.comp.TIMDs
            # print [t.calculatedData.avgSuccessfulTimesCrossedDefensesTele for t in self.calculator.comp.teams]
            # print  "2"
            self.calculator.cacheSecondTeamData()
            # print  "3"
            # print calculator.cachedTeamDatas[team.number].defensesFaced
            self.calculator.doBetweenFirstAndSecondCalculationsForTeams()
            # print  "4"
            self.calculator.doMatchesCalculations()
            # print  "5"
            self.calculator.calculateCitrusDPRs()
            # print  "6"
            self.calculator.doSecondTeamCalculations()

            # print  "7"
            c.RScoreTorque = team.calculatedData.RScoreTorque
            # print  "8"
            c.RScoreSpeed = team.calculatedData.RScoreSpeed
            # print  "9"
            c.RScoreEvasion = team.calculatedData.RScoreEvasion
            # print  "10"
            c.RScoreDefense = team.calculatedData.RScoreDefense
            # print  "11"
            c.RScoreBallControl = team.calculatedData.RScoreBallControl
            # print  "12"
            c.RScoreDrivingAbility = team.calculatedData.RScoreDrivingAbility
            # print  "13"
            c.firstPickAbility = team.calculatedData.firstPickAbility
            # print  "14"
            c.scoreContribution = self.calculator.scoreContributionForTeamForMatch(team, match)
            # print  "15"
            

            

class Calculator(object):
    """docstring for Calculator"""

    def __init__(self, competition):
        super(Calculator, self).__init__()
        warnings.simplefilter('error', RuntimeWarning)

        self.comp = competition
        # self.comp.TIMDs = filter(lambda timd: timd.matchNumber <= 12, self.comp.TIMDs)
        # self.comp.matches = filter(lambda m: m.number <= 12, self.comp.matches)
        self.categories = ['a', 'b', 'c', 'd', 'e']
        self.ourTeamNum = 1678
        self.monteCarloIterations = 100
        self.defenseList = ['pc', 'cdf', 'mt', 'rt', 'rw', 'lb', 'rp', 'sp', 'db']
        self.defenseDictionary = {'a': ['pc', 'cdf'],
                                  'b': ['mt', 'rp'],
                                  'c': ['sp', 'db'],
                                  'd': ['rw', 'rt'],
                                  'e': ['lb']
                                  }

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
        return filter(lambda t: self.teamCalculatedDataHasValues(t.calculatedData), self.comp.teams)

    def getMatchesForTeam(self, team):
        return [match for match in self.comp.matches if self.teamInMatch(team, match)]

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
        return [match for match in self.comp.matches if match.number == matchNumber][0]

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
        return [timd for timd in self.comp.TIMDs if timd.matchNumber == match.number]

    def matchHasAllTeams(self, match):
        return len(self.getAllTIMDsForMatch(match)) == 6

    # TIMD utility functions
    def getTIMDsForTeamNumber(self, teamNumber):
        if teamNumber == -1:
            return self.comp.TIMDs
        return [timd for timd in self.comp.TIMDs if timd.teamNumber == teamNumber]

    def getCompletedTIMDsForTeamNumber(self, teamNumber):
        return filter(self.timdIsCompleted, self.getTIMDsForTeamNumber(teamNumber))

    def getCompletedTIMDsForTeam(self, team):
        cachedData = self.cachedTeamDatas[team.number]
        return cachedData.completedTIMDs

    def getTIMDsForMatchNumber(self, matchNumber):
        return [timd for timd in self.comp.TIMDs if timd.matchNumber == matchNumber]

    def getCompletedTIMDsForMatchNumber(self, matchNumber):
        return filter(self.timdIsCompleted, self.getTIMDsForMatchNumber(matchNumber))

    def getTIMDForTeamNumberAndMatchNumber(self, teamNumber, matchNumber):
        return [timd for timd in self.getTIMDsForTeamNumber(teamNumber) if timd.matchNumber == matchNumber][0]

    def getCompletedTIMDsInCompetition(self):
        return [timd for timd in self.comp.TIMDs if self.timdIsCompleted(timd)]

    def teamCalculatedDataHasValues(self, calculatedData):
        return calculatedData.siegeAbility != None

    def TIMCalculatedDataHasValues(self, calculatedData):
        return calculatedData.drivingAbility != None
        # hasValues = False
        # for key, value in utils.makeDictFromObject(calculatedData).items():
        #     if value != None and not 'Defense' in key and not 'defense' in key and not 'second' in key and not "ballsIntakedAuto" in key:
        #         hasValues = True
        # return hasValues

    def timdIsPlayed(self, timd):
        return timd.rankTorque != None and timd.numHighShotsMadeTele != None
        # isPlayed = False
        # for key, value in utils.makeDictFromTIMD(timd).items():
        #     if value != None:
        #         isPlayed = True
        # return isPlayed

    def teamsAreOnSameAllianceInMatch(self, team1, team2, match):
        areInSameMatch = False
        alliances = [match.redAllianceTeamNumbers, match.blueAllianceTeamNumbers]
        for alliance in alliances:
            if team1.number in alliance and team2.number in alliance:
                areInSameMatch = True
        return areInSameMatch

    exceptedKeys = ['calculatedData', 'ballsIntakedAuto', 'superNotes']

    def timdIsCompleted(self, timd):
        return timd.rankTorque != None and timd.numHighShotsMadeTele != None
        # isCompleted = True
        # m = self.getMatchForNumber(timd.matchNumber)
        # isCompleted = m.redDefensePositions != None and m.blueDefensePositions != None
        # for key, value in utils.makeDictFromTIMD(timd).items():
        #     if key not in self.exceptedKeys and value == None:
        #         isCompleted = False
        # return isCompleted

    matchExceptedKeys = ['calculatedData']
    def matchHasValuesSet(self, match):
        return match.redScore != None and match.blueScore != None
        # isCompleted = True
        # for key, value in utils.makeDictFromMatch(match).items():
        #     if key not in self.matchExceptedKeys and value == None:
        #         isCompleted = False
        # return isCompleted

    def retrieveCompletedTIMDsForTeam(self, team):
        return self.getCompletedTIMDsForTeamNumber(team.number)

    # Calculated Team Data
    def getAverageForDataFunctionForTeam(self, team, dataFunction):
        # validTIMDs = filter(lambda timd: dataFunction(timd) != None, self.getCompletedTIMDsForTeam(team))
        values = map(dataFunction, self.getCompletedTIMDsForTeam(team))
        if len(values) > 0:
            return np.mean(values)

    def getSumForDataFunctionForTeam(self, team, dataFunction):
        return sum(map(dataFunction, self.getCompletedTIMDsForTeam(team)))

    def getStandardDeviationForDataFunctionForTeam(self, team, dataFunction):
        validTIMDs = filter(lambda timd: dataFunction(timd) != None, self.getCompletedTIMDsForTeam(team))
        if len(validTIMDs) == 0:
            return None
        return np.std(map(dataFunction, validTIMDs))

    def getAccuracyForTIMDForMadeFunctionForMissedFunction(self, timd, madeFunction, missedFunction):
        denominator = madeFunction(timd) + missedFunction(timd)
        return (float(madeFunction(timd)) / float(denominator)) if denominator != 0 else 0

    def getTIMDHighShotAccuracyTele(self, timd):
        madeFunction = lambda t: float(t.numHighShotsMadeTele)
        missedFunction = lambda t: float(t.numHighShotsMissedTele)
        return self.getAccuracyForTIMDForMadeFunctionForMissedFunction(timd, madeFunction, missedFunction)

    def getTIMDLowShotAccuracyTele(self, timd):
        madeFunction = lambda t: float(t.numLowShotsMadeTele)
        missedFunction = lambda t: float(t.numLowShotsMissedTele)
        return self.getAccuracyForTIMDForMadeFunctionForMissedFunction(timd, madeFunction, missedFunction)

    def getTIMDHighShotAccuracyAuto(self, timd):
        madeFunction = lambda t: float(t.numHighShotsMadeAuto)
        missedFunction = lambda t: float(t.numHighShotsMissedAuto)
        return self.getAccuracyForTIMDForMadeFunctionForMissedFunction(timd, madeFunction, missedFunction)

    def getTIMDLowShotAccuracyAuto(self, timd):
        madeFunction = lambda t: float(t.numLowShotsMadeAuto)
        missedFunction = lambda t: float(t.numLowShotsMissedAuto)
        return self.getAccuracyForTIMDForMadeFunctionForMissedFunction(timd, madeFunction, missedFunction)

    def twoBallAutoTIMDsForTeam(self, team):
        return filter(lambda timd: timd.calculatedData.highShotsAttemptedTele > 2, self.getCompletedTIMDsForTeam(team))

    def twoBallAutoTriedPercentage(self, team):
        return len(self.twoBallAutoTIMDsForTeam(team)) / len(self.getCompletedTIMDsForTeam(team)) 

    def twoBallAutoAccuracy(self, team):
        timds = self.twoBallAutoTIMDsForTeam(team)
        if len(timds) > 0:
            return np.mean([timd.calculatedData.highShotAccuracyAuto for timd in timds])

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
        return 10 * int(timd.numHighShotsMadeAuto) + 5 * int(timd.numLowShotsMadeAuto) + 2 * utils.convertFirebaseBoolean(timd.didReachAuto) + 10 * int(defenseCrossesInAuto)

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
        if x != None and mu != None and sigma != None: return 1.0 - stats.norm.cdf(x, mu, sigma)

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

    # def defenseCrossesInTIMD(self, timd):
    #     for defense in seldefensesFacedInTIMD:

    def defenseFacedForTIMD(self, timd, defenseKey):
        return defenseKey in self.defensesFacedInTIMD(timd)

    def defensesFacedInTIMD(self, timd):
        match = self.getMatchForNumber(timd.matchNumber)
        team = self.getTeamForNumber(timd.teamNumber)
        return match.redDefensePositions if self.getTeamAllianceIsRedInMatch(team, match) else match.blueDefensePositions

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
        competitionDefenseSightings = self.numTimesCompetitionFacedDefense(defenseKey)
        if competitionDefenseSightings == 0:
            return None
        defenseRetrievalFunction = lambda t: t.calculatedData.avgSuccessfulTimesCrossedDefensesTele[defenseKey]
        averageOfDefenseCrossingsAcrossCompetition = np.mean(
            [defenseRetrievalFunction(t) for t in self.teamsWhoHaveFacedDefense(defenseKey)])
        teamAverageDefenseCrossings = defenseRetrievalFunction(team) if defenseRetrievalFunction(team) != None else 0
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
            if value != initialValue: impossible = False
        if impossible: 
            zscores = [0.0 for v in values]
        else: 
            zscores = stats.zscore(values)
        for i in range(len(self.teamsWithMatchesCompleted())):
            d[self.teamsWithMatchesCompleted()[i].number] = zscores[i]

    torqueWeight = 0.1
    ballControlWeight = 0.2
    evasionWeight = 0.25
    defenseWeight = 0.35
    speedWeight = 0.1
    def drivingAbilityForTIMD(self, timd):
        return (self.torqueWeight * timd.rankTorque) + (
            self.ballControlWeight * timd.rankBallControl) + (
            self.evasionWeight * timd.rankEvasion) + (
            self.defenseWeight * timd.rankDefense) + (
            self.speedWeight * timd.rankSpeed)

    def drivingAbility(self, team, match):
        return self.drivingAbilityForTIMD(self.getTIMDForTeamNumberAndMatchNumber(team, match))

    def predictedCrossingsForDefenseCategory(self, team, category):
        return np.mean([team.calculatedData.predictedSuccessfulCrossingsForDefenseTele[dKey] for dKey in self.defenseDictionary[category] if self.teamFacedDefense(team, dKey) and team.calculatedData.predictedSuccessfulCrossingsForDefenseTele[dKey] != None]) # TODO: Update with actual correct key

    def predictedCrossingsForDefense(self, team, defenseKey):
        return team.calculatedData.predictedSuccessfulCrossingsForDefenseTele[defenseKey]

    def getPredictedCrossingsForAllianceForDefense(self, alliance, defenseKey):
        if self.numTimesCompetitionFacedDefense(defenseKey) <= 0:
            return None
        predictedCrossingsRetrievalFunction = lambda t: self.predictedCrossingsForDefense(t, defenseKey)
        return sum(map(predictedCrossingsRetrievalFunction, alliance))

    def getPredictedCrossingsForAllianceForCategory(self, alliance, category):
        predictedCrossingsRetrievalFunction = lambda t: self.predictedCrossingsForDefenseCategory(t, category)
        return sum(map(predictedCrossingsRetrievalFunction, alliance))

    def predictedTeleDefensePointsForAllianceForCategory(self, alliance, category):
        return 5 * min(self.getPredictedCrossingsForAllianceForCategory(alliance, category), 2)

    def predictedTeleDefensePointsForAllianceForDefense(self, alliance, defenseKey):
        predCrosses = self.getPredictedCrossingsForAllianceForDefense(alliance, defenseKey)
        if predCrosses == None:
            return None
        return 5 * min(self.getPredictedCrossingsForAllianceForDefense(alliance, defenseKey), 2)

    def predictedScoreForAllianceWithNumbers(self, allianceNumbers):
        return self.predictedScoreForAlliance(self.teamsForTeamNumbersOnAlliance(allianceNumbers))

    def replaceWithAverageIfNecessary(self, team):
        return team if self.teamCalculatedDataHasValues(team.calculatedData) else self.averageTeam

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
            alliance, dKey) if self.numTimesCompetitionFacedDefense(dKey) > 0 else None
        allianceDefensePointsTele = sum(map(alliancePredictedCrossingsRetrievalFunction, defenses))
        # print "Predicted Crossings"
        total = allianceTeleopShotPoints + allianceSiegePoints + allianceAutoPoints + allianceDefensePointsTele
        return total

    def defenseCombinations(self):
        return self.getDefenseCombinations(self.categories)

    def getDefenseCombinations(self, categories):
        # pdb.set_trace()
        if len(categories) == 1:
            return [self.defenseDictionary[categories[0]]]
        combos = []
        for defense in self.defenseDictionary[categories[0]]:
            if self.numTimesCompetitionFacedDefense(defense) > 0:
                for combo in self.getDefenseCombinations(categories[1:]):
                    newCombo = [defense]
                    newCombo.extend(combo)
                    combos.append(newCombo)

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

    def autoCrossingsForCategory(self, team, category):
        return np.mean([team.calculatedData.avgSuccessfulTimesCrossedDefensesAuto[defense] if team.calculatedData.avgSuccessfulTimesCrossedDefensesAuto[defense] != None else 0.0 for defense in self.defenseDictionary[category]])

    def stdAutoCrossingsForCategory(self, team, category):
        return utils.rms(filter(lambda x: x != None, [team.calculatedData.sdSuccessfulDefenseCrossesAuto[defense] for defense in self.defenseDictionary[category]]))

    def getDefenseDamageChanceForAllianceForCategory(self, alliance, category):
        crossings = sum(map(lambda t: self.predictedCrossingsForDefenseCategory(t, category), alliance))
        stdDev = utils.sumStdDevs(map(lambda t: self.standardDeviationForTeamForCategory(t, category), alliance))
        autoCrossings = sum(map(lambda t: self.autoCrossingsForCategory(t, category), alliance))
        autoStd = utils.sumStdDevs(map(lambda t: self.stdAutoCrossingsForCategory(t, category), alliance))
        return self.probabilityDensity(2.0, crossings + autoCrossings, utils.sumStdDevs([stdDev, autoStd]))

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

    def getWinChanceForMatchForAllianceIsRed(self, match, allianceIsRed):
        winChance = match.calculatedData.redWinChance if allianceIsRed else match.calculatedData.blueWinChance
        return winChance if not math.isnan(winChance) else None

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
        siegeChance = np.prod([t.calculatedData.siegeConsistency for t in alliance])
        return siegeChance * self.probabilityDensity(8.0, self.numShotsForAlliance(alliance), self.stdDevNumShotsForAlliance(alliance))

    def captureChanceForAllianceNumbers(self, allianceNumbers):
        return self.captureChanceForAlliance(self.teamsForTeamNumbersOnAlliance(allianceNumbers))

    def winChanceForMatchForAllianceIsRed(self, match, allianceIsRed):
        alliance = self.getAllianceForMatch(match, allianceIsRed)
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
        return stats.t.cdf(tscoreRPs, np.mean([sampleSize, opposingSampleSize]))

    def predictedRPsForAllianceForMatch(self, allianceIsRed, match):
        alliance = self.getAllianceForMatch(match, allianceIsRed)
        alliance = map(self.replaceWithAverageIfNecessary, alliance)

        breachRPs = self.getBreachChanceForMatchForAllianceIsRed(match, allianceIsRed)
        captureRPs = self.getCaptureChanceForMatchForAllianceIsRed(match, allianceIsRed)


        scoreRPs = 2 * self.getWinChanceForMatchForAllianceIsRed(match, allianceIsRed)
        RPs = breachRPs + captureRPs + scoreRPs
        return RPs if not math.isnan(RPs) else None

    def welchsTest(self, mean1, mean2, std1, std2, sampleSize1, sampleSize2):
        if std1 == 0.0 or std2 == 0.0 or sampleSize1 <= 0 or sampleSize2 <= 0:
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
        #if team1.calculatedData.citrusDPR != None:
         #   return self.gamma * team1.calculatedData.citrusDPR + (1 - self.gamma) * self.predictedScoreForAlliance([self.getOurTeam(), team2, team1])
        #else:
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
        return teams[::-1]       

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
        # print [m.calculatedData.predictedRedScore for m in self.getMatchesForTeam(team)]
        # print [self.getUpdatedNumRPsForTeamForMatch(team, m) for m in self.getMatchesForTeam(team)]
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
        a = [(match.redScore + match.blueScore) for match in self.comp.matches if
             (match.blueScore != None and match.redScore != None)]
        return sum(a) / len(self.comp.matches)

    def numPlayedMatchesInCompetition(self):
        return len([match for match in self.comp.matches if self.matchIsPlayed(match)])

    def getRankingForTeamByRetrievalFunctions(self, team, retrievalFunctions):
        if team in self.teamsWithCalculatedData():
            return self.teamsSortedByRetrievalFunctions(retrievalFunctions).index(team) + 1

    def getSeedingFunctions(self):
        return [lambda t: t.calculatedData.actualNumRPs, self.cumulativeSumAutoPointsForTeam,
                self.cumulativeSumSiegePointsForTeam]

    def numDefensesCrossedForTimeDict(self, timdDict):
        numCrossed = 0
        for value, key in timdDict.iteritems():
            numCrossed += len(value)
        return numCrossed

    def didCrossDefenseAutoForTIMD(self, timd):
        return self.numDefensesCrossedForTimeDict(timd.timesSuccessfulCrossedDefensesAuto) > 0

    def getAutoPointsForMatchForAllianceIsRed(self, match, allianceIsRed):
        timds = [self.getTIMDForTeamNumberAndMatchNumber(t.number, match.number) for t in self.getAllianceForMatch(match, allianceIsRed)]
        reachPoints = sum([2 * utils.convertFirebaseBoolean(timd.didReachAuto) for timd in timds])
        highShotPoints = sum([10 * timd.numHighShotsMadeAuto for timd in timds])
        lowShotPoints = sum([5 * timd.numLowShotsMadeAuto for timd in timds])
        defensePoints = sum([self.didCrossDefenseAutoForTIMD(timd) for timd in timds]) # Not perfect, since all three teams could theoretically cross the same defense
        return reachPoints + highShotPoints + lowShotPoints + defensePoints

    def getAutoPointsForTeamAllianceInMatch(self, team, match):
        return self.getAutoPointsForMatchForAllianceIsRed(match, self.getTeamAllianceIsRedInMatch(team, match))

    def cumulativeSumAutoPointsForTeam(self, team):
        return sum([self.getAutoPointsForTeamAllianceInMatch(team, m) for m in self.getCompletedMatchesForTeam(team)])

    def getSiegePointsForMatchForAllianceIsRed(self, match, allianceIsRed):
        timds = [self.getTIMDForTeamNumberAndMatchNumber(t.number, match.number) for t in self.getAllianceForMatch(match, allianceIsRed)]
        capturePoints = sum([15 * utils.convertFirebaseBoolean(timd.didScaleTele) for timd in timds])
        challengePoints = sum([5 * utils.convertFirebaseBoolean(timd.didChallengeTele) for timd in timds])
        return capturePoints + challengePoints

    def getSiegePointsForTeamAllianceInMatch(self, team, match):
        return self.getSiegePointsForMatchForAllianceIsRed(match, self.getTeamAllianceIsRedInMatch(team, match))

    def cumulativeSumSiegePointsForTeam(self, team):
        return sum([self.getSiegePointsForTeamAllianceInMatch(team, m) for m in self.getCompletedMatchesForTeam(team)])        

    def getPredictedAutoPointsForMatchForAllianceIsRed(self, match, allianceIsRed):
        return sum([t.calculatedData.autoAbility for t in self.getAllianceForMatch(match, allianceIsRed)])

    def getPredictedAutoPointsForTeamAllianceInMatch(self, team, match):
        return self.getPredictedAutoPointsForMatchForAllianceIsRed(match, self.getTeamAllianceIsRedInMatch(team, match))

    def cumulativeSumPredictedAutoPointsForTeam(self, team):
        return sum([self.getPredictedAutoPointsForTeamAllianceInMatch(team, m) for m in self.getCompletedMatchesForTeam(team)])

    def getPredictedSiegePointsForMatchForAllianceIsRed(self, match, allianceIsRed):
        return sum([t.calculatedData.siegeAbility for t in self.getAllianceForMatch(match, allianceIsRed)])

    def getPredictedSiegePointsForTeamAllianceInMatch(self, team, match):
        return self.getPredictedSiegePointsForTeamAllianceInMatch(match, self.getTeamAllianceIsRedInMatch(team, match))

    def cumulativeSumPredictedSiegePointsForTeam(self, team):
        return sum([self.getPredictedSiegePointsForTeamAllianceInMatch(team, m) for m in self.getCompletedMatchesForTeam(team)])  

    def getPredictedSeedingFunctions(self):
        return [lambda t: t.calculatedData.predictedNumRPs, self.cumulativeSumAutoPointsForTeam, self.cumulativeSumSiegePointsForTeam]

    def teamsForTeamNumbersOnAlliance(self, alliance):
        return map(self.getTeamForNumber, alliance)

    def getAllianceForMatch(self, match, allianceIsRed):
        return self.teamsForTeamNumbersOnAlliance(
            match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers)

    def getAllianceForTeamInMatch(self, team, match):
        return self.getAllianceForMatch(match, self.getTeamAllianceIsRedInMatch(team, match))

    def getPredictedResultOfRetrievalFunctionForAlliance(self, alliance, retrievalFunction):
        return sum(map(retrievalFunction, alliance))

    def getPredictedResultOfRetrievalFunctionForTeamInMatch(self, team, match, retrievalFunction):
        return self.getPredictedResultOfRetrievalFunctionForAlliance(self.getAllianceForTeamInMatch(team, match), retrievalFunction)

    def getPredictedResultOfRetrievalFunctionForTeam(self, team, retrievalFunction):
        # print team.number
        # print self.getMatchesForTeam(team)
        # print map(retrievalFunction, self.getMatchesForTeam(team))
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

    


        # keyDict = keyRetrievalFunction(team)
        # getModifiedDataPointFunction = lambda dKey, timd: dataPointModificationFunction(valueRetrievalFunction(timd)[dKey] if dKey in valueRetrievalFunction(timd) else None)
        # getAverageFunction = lambda dKey: self.getAverageAcrossCompetitionTeamSawDefense(team, dKey, lambda
        #     timd: getModifiedDataPointFunction(dKey, timd))
        # protectedGetAverageFunction = lambda dKey: getAverageFunction(dKey) if not math.isnan(
        #     getAverageFunction(dKey)) else None
        # dictionarySetFunction = lambda dKey: utils.setDictionaryValue(keyDict, dKey, protectedGetAverageFunction(dKey))
        # map(dictionarySetFunction, self.defenseList)

    def defenseValuesForAverageTeam(self, retrievalFunction, combinationFunction):
        defenseDict = {}
        for defense in self.defenseList:
            dataPoints = []
            for team in self.teamsWhoHaveFacedDefense(defense):
                dataPoints.append(retrievalFunction(team)[defense])
            defenseDict[defense] = combinationFunction(dataPoints) if len(dataPoints) > 0 else None
        return defenseDict


    def setDefenseValuesForForAverageTeam(self, retrievalFunction, dataModification):
        keyDict = retrievalFunction(self.averageTeam)
        getValueFunc = lambda x, dKey: retrievalFunction(x)[dKey] if self.teamFacedDefense(x, dKey) else None
        avgFunc = lambda dKey: dataModification([getValueFunc(t, dKey) for t in self.teamsWithCalculatedData() if getValueFunc(t, dKey) != None])
        dictSetFunction = lambda dKey: utils.setDictionaryValue(keyDict, dKey, avgFunc(dKey))
        map(dictSetFunction, self.defenseList)

    def timdsWithDefense(self, defenseKey):
        return filter(lambda t: self.defenseFacedForTIMD(t, defenseKey), self.getCompletedTIMDsInCompetition())

    def getAverageAcrossCompetitionTeamSawDefense(self, team, defenseKey, retrievalFunction):
        return np.mean(map(retrievalFunction, self.comp.TIMDsWithDefense(defenseKey)))

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
        # print "Caching"
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
        # print "Beginning first calculations for team: " + str(self.averageTeam.number) + ", " + self.averageTeam.name
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
        a.avgSuccessfulTimesCrossedDefensesAuto = self.defenseValuesForAverageTeam(lambda t: t.calculatedData.avgSuccessfulTimesCrossedDefensesAuto, np.mean)
        # self.defenseValuesForAverageTeam(lambda t: t.calculatedData.avgFailedTimesCrossedDefensesAuto, np.mean)
        # self.defenseValuesForAverageTeam(lambda t: t.calculatedData.avgTimeForDefenseCrossAuto, np.mean)
        a.avgSuccessfulTimesCrossedDefensesTele = self.defenseValuesForAverageTeam(lambda t: t.calculatedData.avgSuccessfulTimesCrossedDefensesTele, np.mean)
        # self.defenseValuesForAverageTeam(lambda t: t.calculatedData.avgFailedTimesCrossedDefensesTele, np.mean)
        # self.defenseValuesForAverageTeam(lambda t: t.calculatedData.avgTimeForDefenseCrossTele, np.mean)
        a.sdSuccessfulDefenseCrossesAuto = self.defenseValuesForAverageTeam(lambda t: t.calculatedData.sdSuccessfulDefenseCrossesAuto, utils.rms)
        # self.defenseValuesForAverageTeam(lamdba t: t.calculatedData.sdFailedDefenseCrossesAuto, utils.rms)
        a.sdSuccessfulDefenseCrossesTele = self.defenseValuesForAverageTeam(lambda t: t.calculatedData.sdSuccessfulDefenseCrossesTele, utils.rms)
        # self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.avgSuccessfulTimesCrossedDefensesAuto, lambda x: np.mean(x))
        # self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.avgFailedTimesCrossedDefensesAuto, lambda x: np.mean(x))
        # self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.avgTimeForDefenseCrossAuto, lambda x: np.mean(x))
        # self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.sdSuccessfulDefenseCrossesAuto, lambda x: utils.rms(x))
        # self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.sdFailedDefenseCrossesTele, lambda x: utils.rms(x))
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
        # self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.avgSuccessfulTimesCrossedDefensesTele, lambda x: np.mean(x))
        # self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.avgFailedTimesCrossedDefensesTele, lambda x: np.mean(x))
        # self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.avgTimeForDefenseCrossTele, lambda x: np.mean(x))
        # self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.sdSuccessfulDefenseCrossesTele, lambda x: utils.rms(x))
        # self.setDefenseValuesForForAverageTeam(lambda t: t.calculatedData.sdFailedDefenseCrossesTele, lambda x: utils.rms(x))
        a.numScaleAndChallengePoints = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.numScaleAndChallengePoints) # Checked
        
        a.breachPercentage = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.breachPercentage)
        #here

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
        # a. = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.numRPs)
        a.predictedNumRPs = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.predictedNumRPs)




    def doFirstCalculationsForTeam(self, team):
        if not len(self.getCompletedTIMDsForTeam(team)) <= 0:
            # print "No Complete TIMDs for team " + str(team.number) + ", " + str(team.name)
        # else:
            # print("Beginning first calculations for team: " + str(team.number) + ", " + str(team.name))
            # Super Scout Averages
            # print map(utils.makeDictFromMatch, self.getCompletedTIMDsForTeam(team))
            if not self.teamCalculatedDataHasValues(team.calculatedData):
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
            t.avgSuccessfulTimesCrossedDefensesTele = self.getAverageNumberDefenseValues(team, lambda timd: timd.timesSuccessfulCrossedDefensesTele)
            t.avgSuccessfulTimesCrossedDefensesAuto = self.getAverageNumberDefenseValues(team, lambda timd: timd.timesSuccessfulCrossedDefensesAuto)
            t.avgFailedTimesCrossedDefensesAuto = self.getAverageNumberDefenseValues(team, lambda timd: timd.timesFailedCrossedDefensesAuto)
            t.avgFailedTimesCrossedDefensesTele = self.getAverageNumberDefenseValues(team, lambda timd: timd.timesFailedCrossedDefensesTele)
            t.avgTimeForDefenseCrossAuto = self.getAverageTimeDefenseValues(team, lambda timd: timd.timesSuccessfulCrossedDefensesAuto)
            t.avgTimeForDefenseCrossTele = self.getAverageTimeDefenseValues(team, lambda timd: timd.timesSuccessfulCrossedDefensesTele)
            t.sdSuccessfulDefenseCrossesAuto = self.getStdNumberDefenseValues(team, lambda timd: timd.timesSuccessfulCrossedDefensesAuto)
            t.sdSuccessfulDefenseCrossesTele = self.getStdNumberDefenseValues(team, lambda timd: timd.timesSuccessfulCrossedDefensesTele)
            t.sdFailedDefenseCrossesAuto = self.getStdNumberDefenseValues(team, lambda timd: timd.timesFailedCrossedDefensesAuto)
            t.sdFailedDefenseCrossesTele = self.getStdNumberDefenseValues(team, lambda timd: timd.timesFailedCrossedDefensesTele)
            t.crossingsSuccessRateForDefenseAuto = utils.dictQuotient(t.avgSuccessfulTimesCrossedDefensesAuto, utils.dictSum(t.avgSuccessfulTimesCrossedDefensesAuto, t.avgFailedTimesCrossedDefensesAuto))
            t.crossingsSuccessRateForDefenseTele = utils.dictQuotient(t.avgSuccessfulTimesCrossedDefensesTele, utils.dictSum(t.avgSuccessfulTimesCrossedDefensesTele, t.avgFailedTimesCrossedDefensesTele))
            # t.predictedSuccessfulCrossingsForDefenseTele = 

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
            t.avgHighShotsAttemptedTele = self.getAverageForDataFunctionForTeam(team,
                lambda timd: timd.calculatedData.highShotsAttemptedTele)
            t.avgLowShotsAttemptedTele = self.getAverageForDataFunctionForTeam(team,
                lambda timd: timd.calculatedData.lowShotsAttemptedTele)
            t.twoBallAutoTriedPercentage = self.twoBallAutoTriedPercentage(team)
            t.twoBallAutoAccuracy = self.twoBallAutoAccuracy(team)
            # self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForTeam(
            #     team,
            #     lambda tm: tm.calculatedData.avgSuccessfulTimesCrossedDefensesTele,
            #     lambda timd: timd.timesSuccessfulCrossedDefensesTele,
            #     lambda x: len(x) if x != None else 0,
            #     self.getAverageAcrossMatchesTeamSawDefense)
            # self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForTeam(
            #     team,
            #     lambda tm: tm.calculatedData.avgFailedTimesCrossedDefensesTele,
            #     lambda timd: timd.timesFailedCrossedDefensesTele,
            #     lambda x: len(x) if x != None else 0,
            #     self.getAverageAcrossMatchesTeamSawDefense)
            # self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForTeam(
            #     team,
            #     lambda tm: tm.calculatedData.avgTimeForDefenseCrossTele,
            #     lambda timd: timd.timesSuccessfulCrossedDefensesTele,
            #     lambda x: np.mean(x) if x != None and x != [] else 0,
            #     self.getAverageAcrossMatchesTeamSawDefense)
            # self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForModificationFunctionForTeam(
            #     team,
            #     lambda tm: tm.calculatedData.sdSuccessfulDefenseCrossesTele,
            #     lambda timd: timd.timesSuccessfulCrossedDefensesTele,
            #     lambda x: len(x) if x != None else 0,
            #     self.getStdDevAcrossMatchesTeamSawDefense) 
        else: print "No TIMDs for team " + str(team.number)
    
    def numCrossingsForTIMD(self, timd, dataDict):
        valuesDict = {}
        for defense in self.defensesFacedInTIMD(timd):
            valuesDict[defense] = len(dataDict[defense]) if defense in dataDict and dataDict[defense] != None else 0
        return valuesDict

    def valueCrossingsForTIMD(self, timd, dataDict):
        valuesDict = {}
        for defense in self.defensesFacedInTIMD(timd):
            if defense in dataDict and dataDict[defense] != None and dataDict[defense] != []:
                valuesDict[defense] = np.mean(dataDict[defense])
        return valuesDict

    def getAverageNumberDefenseValues(self, team, valueRetrievalFunction):
        valuesDict = {}
        for defense in self.defenseList:
            values = []
            # if team.number == 6004:
                # print [defense + ': ' + str(timd.matchNumber) for timd in self.comp.TIMDsWhereTeamFacedDefense(team, defense)]
            for timd in self.timdsWhereTeamFacedDefense(team, defense):
                valueDict = valueRetrievalFunction(timd)
                if defense in valueDict:
                    values.append(len(valueDict[defense] if valueDict[defense] != None else []))
                else: values.append(0)
            valuesDict[defense] = np.mean(values) if len(values) > 0 else None
        return valuesDict

    def getStdNumberDefenseValues(self, team, valueRetrievalFunction):
        valuesDict = {}
        for defense in self.defenseList:
            values = []
            # if team.number == 6004:
                # print [defense + ': ' + str(timd.matchNumber) for timd in self.comp.TIMDsWhereTeamFacedDefense(team, defense)]
            for timd in self.timdsWhereTeamFacedDefense(team, defense):
                valueDict = valueRetrievalFunction(timd)
                if defense in valueDict:
                    values.append(len(valueDict[defense] if valueDict[defense] != None else []))
                else: values.append(0)
            valuesDict[defense] = np.std(values) if len(values) > 0 else None
        return valuesDict

    def getAverageTimeDefenseValues(self, team, valueRetrievalFunction):
        valuesDict = {}
        for defense in self.defenseList:
            values = []
            for timd in self.timdsWhereTeamFacedDefense(team, defense):
                valueDict = valueRetrievalFunction(timd)
                if defense in valueDict:
                    if valueDict[defense] != None and valueDict[defense] != []:
                        values.append(np.mean(valueDict[defense]))
            valuesDict[defense] = np.mean(values) if len(values) > 0 else None
        return valuesDict
                

    # def setDefenseValues(self, team,
    #                     calculatedDataPoints,
    #                     valueRetrievalFunction,
    #                     dataPointModificationFunction,
    #                     secondDataPointModificationFunction):                                                                           
    #     dataPoints = {}
    #     for dKey in self.defenseList:
    #         dataPoints[dKey] = []
    #     for timd in self.getCompletedTIMDsForTeam(team):
    #         # print valueRetrievalFunction(timd)
    #         # print dataPoints
    #         for defense in self.defensesFacedInTIMD(timd):
    #             value = valueRetrievalFunction(timd)[defense]
    #             if 
    #             dataPoints[defense].append(dataPointModificationFunction(valueRetrievalFunction(timd)[defense]))
    #     for key in dataPoints:
    #         print dataPoints
    #         calculatedDataPoints[key] = secondDataPointModificationFunction(dataPoints[key])

    def doBetweenFirstAndSecondCalculationsForTeams(self):
        for team in self.comp.teams:
            self.doBetweenFirstAndSecondCalculationsForTeam(team)
        self.doBetweenFirstAndSecondCalculationsForTeam(self.averageTeam)

    def doBetweenFirstAndSecondCalculationsForTeam(self, team):
        if not len(self.getCompletedTIMDsForTeam(team)) <= 0:
            # print "No Complete TIMDs for team " + str(team.number) + ", " + str(team.name)
        # else:
            # print("Beginning second calculations for team: " + str(team.number) + ", " + str(team.name))
            #print("#")
            for defense in self.defenseList:
                team.calculatedData.predictedSuccessfulCrossingsForDefenseTele[defense] = self.predictedCrosses(team, defense)
            # map(lambda dKey: utils.setDictionaryValue(
            #     team.calculatedData.predictedSuccessfulCrossingsForDefenseTele, # TODO: Update with the correct key
            #     dKey, 
            #     self.predictedCrosses(team, dKey)),
            #     self.defenseList)


    def doSecondCalculationsForTeam(self, team):
        if not len(self.getCompletedTIMDsForTeam(team)) <= 0:
            # print "No Complete TIMDs for team " + str(team.number) + ", " + str(team.name)
        # else:
            # print("Beginning second calculations for team: " + str(team.number) + ", " + str(team.name))
            #print("#")

            t = team.calculatedData
           # print sum(filter(t.averagen))
	    t.RScoreTorque = self.cachedComp.torqueZScores[team.number]
            t.RScoreSpeed = self.cachedComp.speedZScores[team.number]
            t.RScoreEvasion = self.cachedComp.evasionZScores[team.number]
            t.RScoreDefense = self.cachedComp.defenseZScores[team.number]
            t.RScoreBallControl = self.cachedComp.ballControlZScores[team.number]
            t.RScoreDrivingAbility = self.cachedComp.drivingAbilityZScores[team.number]
            t.avgSuccessfulTimesCrossedDefenses = utils.dictSum(t.avgSuccessfulTimesCrossedDefensesAuto,
                                                                t.avgSuccessfulTimesCrossedDefensesTele)
            t.blockingAbility = (t.avgShotsBlocked - self.averageTeam.calculatedData.avgShotsBlocked) * self.averageTeam.calculatedData.highShotAccuracyTele * 5
            t.predictedNumRPs = self.predictedNumberOfRPs(team)
            t.actualNumRPs = self.actualNumberOfRPs(team)
            t.firstPickAbility = self.firstPickAbility(team) # Checked	
            t.secondPickAbility = self.secondPickAbility(team) # Checked
            t.overallSecondPickAbility = self.overallSecondPickAbility(team) # Checked
            if team.number in self.cachedComp.citrusDPRs: t.citrusDPR = self.cachedComp.citrusDPRs[team.number]
            t.actualNumRPs = self.getSumForDataFunctionForTeam(team, lambda timd: timd.calculatedData.numRPs)
            t.actualSeed = self.getRankingForTeamByRetrievalFunctions(team, self.getSeedingFunctions()) # Checked
            t.predictedSeed = self.getRankingForTeamByRetrievalFunctions(team, self.getPredictedSeedingFunctions()) # Checked

    # def doThirdCalculationsForTeam(self, team):
    #     if not len(self.getCompletedTIMDsForTeam(team)) <= 0:
    #         # print "No Complete TIMDs for team " + str(team.number) + ", " + str(team.name)
    #     # else:
    #         # print("Beginning third calculations for team: " + str(team.number) + ", " + str(team.name))
    #         t = team.calculatedData
    #         t.secondPickAbility = self.secondPickAbility(team) # Checked
    #         t.overallSecondPickAbility = self.overallSecondPickAbility(team) # Checked        


    def getOptimalDefensesForAlliance(self, alliance):
        optimalDefenseCombination, optimalScore = None, 100000
        defenseCombos = self.defenseCombinations()
        for combo in defenseCombos:
            comboScore = self.predictedScoreForAllianceWithDefenseCombination(alliance, combo)
            if comboScore < optimalScore:
                optimalDefenseCombination, optimalScore = combo, comboScore
        return optimalDefenseCombination[:-1]

    def getOptimalDefensesForAllianceIsRedForMatch(self, allianceIsRed, match):
        alliance = self.getAllianceForMatch(match, allianceIsRed)
        alliance = map(self.replaceWithAverageIfNecessary, alliance)
        return self.getOptimalDefensesForAlliance(alliance)

    def doFirstCalculationsForMatch(self, match): #This entire thing being looped is what takes a while
        # print "Performing calculations for match Q" + str(match.number)
        if self.matchIsCompleted(match):
            match.calculatedData.actualBlueRPs = self.RPsGainedFromMatchForAlliance(True, match)
            #print "a"
            match.calculatedData.actualRedRPs = self.RPsGainedFromMatchForAlliance(False, match)
            #print "b"
            match.calculatedData.numDefensesCrossedByBlue = self.numDefensesCrossedInMatch(False, match)
            #print "c"
            match.calculatedData.numDefensesCrossedByRed = self.numDefensesCrossedInMatch(True, match)
        #print "Breach Chance"
        match.calculatedData.blueBreachChance = self.breachChanceForAllianceNumbers(match.blueAllianceTeamNumbers)
        match.calculatedData.redBreachChance = self.breachChanceForAllianceNumbers(match.redAllianceTeamNumbers)
        #print "Capture Chance"
        match.calculatedData.blueCaptureChance = self.captureChanceForAllianceNumbers(match.blueAllianceTeamNumbers)
        match.calculatedData.redCaptureChance = self.captureChanceForAllianceNumbers(match.blueAllianceTeamNumbers)
        #print "Predicted Score"
        match.calculatedData.predictedBlueScore = self.predictedScoreForAllianceWithNumbers(match.blueAllianceTeamNumbers)
        match.calculatedData.predictedRedScore = self.predictedScoreForAllianceWithNumbers(match.redAllianceTeamNumbers)
        #print "SD Predicted Score"
        match.calculatedData.sdPredictedBlueScore = self.stdDevPredictedScoreForAllianceNumbers(match.blueAllianceTeamNumbers)
        match.calculatedData.sdPredictedRedScore = self.stdDevPredictedScoreForAllianceNumbers(match.redAllianceTeamNumbers)
        #print "Predicted RPs"
        match.calculatedData.blueWinChance = self.winChanceForMatchForAllianceIsRed(match, False)
        match.calculatedData.redWinChance = self.winChanceForMatchForAllianceIsRed(match, True)

        match.calculatedData.predictedBlueRPs = self.predictedRPsForAllianceForMatch(False, match)
        match.calculatedData.predictedRedRPs = self.predictedRPsForAllianceForMatch(True, match)
        
        match.calculatedData.optimalBlueDefenses = self.getOptimalDefensesForAllianceIsRedForMatch(False, match)
        match.calculatedData.optimalRedDefenses = self.getOptimalDefensesForAllianceIsRedForMatch(True, match)

        print "Done! Match " + str(match.number)


    def restoreComp(self):
        self.comp.TIMDs = self.comp.TIMDs
        self.comp.matches = self.comp.matches

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

    def replaceFunction(self, t, v):
	if not t.didGetIncapacitated:
	    if not t.didGetDisabled:
		if v == 0 or v == 0.0:
		    return 2
	return v

    def replaceSuperValues(self, timd):
	#replaceFunction = lambda t, v: 2 if ((not t.didGetIncapacitated) and (not t.didGetDisabled) and (v == 0)) else 0
	
	print(self.replaceFunction(timd, timd.rankTorque))
	timd.rankTorque = self.replaceFunction(timd, timd.rankTorque)
	timd.rankDefense = self.replaceFunction(timd, timd.rankDefense)
	timd.rankBallControl = self.replaceFunction(timd, timd.rankBallControl)
	timd.rankEvasion = self.replaceFunction(timd, timd.rankEvasion)
	timd.rankSpeed = self.replaceFunction(timd, timd.rankSpeed)
	return timd
	

    def doCalculations(self, FBC):
        isData = len(self.getCompletedTIMDsInCompetition()) > 0
        if isData:
            startTime = time.time()
            threads = []
            manager = multiprocessing.Manager()
            calculatedTIMDs = manager.list()
            numTIMDsCalculating = 0
            #for timd in self.comp.TIMDs:
		#timd = self.replaceSuperValues(timd)
	    for timd in self.comp.TIMDs:
            	thread = FirstTIMDThread(timd, calculatedTIMDs, self)
                threads.append(thread)
                thread.start()
            map(lambda t: t.join(), threads)
            # print len(calculatedTIMDs)
            # print type(calculatedTIMDs)
            self.comp.TIMDs = [timd for timd in calculatedTIMDs]
            # threads2 = []
            # for timd in self.comp.TIMDs:
            #     thread = SecondTIMDThread(timd, self)
            #     threads2.append(thread)
            #     thread.start()
            # map(lambda t: t.join(), threads2)

            # while True in map(lambda t: t.isAlive(),)
            # threads2 = []
            # for timd in self.comp.TIMDs:
            # 	thread2 = SecondTIMDThread(timd, copy.deepcopy(self))
            #     threads2.append(thread2)
            #     thread2.start()
            # map(lambda t: t.join(), threads2)
            self.restoreComp()
            self.cacheFirstTeamData()
            self.doFirstTeamCalculations()
            self.cacheSecondTeamData()
            self.doBetweenFirstAndSecondCalculationsForTeams()
            print "a"
            self.doMatchesCalculations() #here
            print "b"

            self.calculateCitrusDPRs()
            print "c"

            self.doSecondTeamCalculations()
            print "d"

            endTime = time.time()
            print "e"

            self.writeCalculationDiagnostic(endTime - startTime)

            
            for team in self.comp.teams:
                # if team in self.teamsWithMatchesCompleted():
                print "Writing team " + str(team.number) + " to Firebase..."
                FBC.addCalculatedTeamDataToFirebase(team)
            for timd in self.comp.TIMDs:
                # if self.timdIsCompleted(timd):
                print "Writing team " + str(timd.teamNumber) + " in match " + str(timd.matchNumber) + " to Firebase..."
                FBC.addCalculatedTIMDataToFirebase(timd)
            for match in self.comp.matches:
                # if self.matchIsCompleted(match):
                if match.calculatedData != None and match.calculatedData != DataModel.CalculatedMatchData():
                    print "Writing match " + str(match.number) + " to Firebase..."
                    FBC.addCalculatedMatchDataToFirebase(match)
            
            # Competition metrics
            if self.numPlayedMatchesInCompetition() > 0:
                self.comp.averageScore = self.avgCompScore()
        else:
            print "No Data"



        
