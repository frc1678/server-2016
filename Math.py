import math
from operator import attrgetter
import re
import pdb
import time

import numpy as np
import scipy as sp
import scipy.stats as stats
import matplotlib.pyplot as plt

import CacheModel as cache
import DataModel
import utils
import time
import TBACommunicator

import multiprocessing
import copy
import warnings
from FirstTIMDProcess import FirstTIMDProcess
from FirebaseWriterProcess import FirebaseWriteObjectProcess

class Calculator(object):
    """docstring for Calculator"""

    def __init__(self, competition):
        super(Calculator, self).__init__()
        warnings.simplefilter('error', RuntimeWarning)

        self.comp = competition
        self.TBAC = TBACommunicator.TBACommunicator()
        self.TBAC.eventCode = self.comp.code
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
        self.defenseCombos = []
        self.cachedTeamDatas = {}
        self.averageTeam = DataModel.Team()
        self.averageTeam.number = -1
        self.averageTeam.name = 'Average Team'
        self.surrogateTIMDs = []
        self.cachedComp = cache.CachedCompetitionData()
        self.cachedTeamDatas[self.averageTeam.number] = cache.CachedTeamData(**{'teamNumber': self.averageTeam.number})
        [utils.setDictionaryValue(self.cachedTeamDatas, team.number,
                                  cache.CachedTeamData(**{'teamNumber': team.number})) for team in self.comp.teams]

    def getMissingDataString(self):
        print "CURRENT MATCH NUM = " + str(self.comp.currentMatchNum)
        playedTIMDs = [timd for timd in self.comp.TIMDs if timd.matchNumber < self.comp.currentMatchNum]
        incompletePlayedSuperTIMDs = [timd for timd in playedTIMDs if timd.rankTorque == None]
        incompletePlayedScoutTIMDs = filter(lambda timd: timd.numHighShotsMadeTele == None, playedTIMDs)
        incompletePlayedSuperTIMDStrings = ['Scout: ' + str(timd.teamNumber) + 'Q' + str(timd.matchNumber) for timd in incompletePlayedSuperTIMDs]
        incompletePlayedScoutTIMDStrings = ['Super: ' + str(timd.teamNumber) + 'Q' + str(timd.matchNumber) for timd in incompletePlayedScoutTIMDs]
        incompletePlayedSuperTIMDStrings.extend(incompletePlayedScoutTIMDStrings)
        return incompletePlayedSuperTIMDStrings

    # Team utility functions
    def getTeamForNumber(self, teamNumber):
        try: return [team for team in self.comp.teams if team.number == teamNumber][0]
        except: 
            print str(teamNumber) + " doesn't exist."
            return None

    def teamsWithCalculatedData(self):
        return filter(lambda t: self.teamCalculatedDataHasValues(t.calculatedData), self.comp.teams)

    def getCompletedMatchesForTeam(self, team):
        return filter(self.matchIsCompleted, team.matches)

    def teamsWithMatchesCompleted(self):
        return self.cachedComp.teamsWithMatchesCompleted

    def findTeamsWithMatchesCompleted(self):
        return filter(lambda x: len(self.getCompletedMatchesForTeam(team)) > 0, self.comp.teams)

    def teamsWhoHaveFacedDefense(self, defenseKey):
        return filter(lambda t: self.teamFacedDefense(t, defenseKey), self.comp.teams)

    def teamCalculatedDataHasValues(self, calculatedData):
        return calculatedData.siegeAbility != None

    def replaceWithAverageIfNecessary(self, team):
        return team if self.teamCalculatedDataHasValues(team.calculatedData) else self.averageTeam

    # Match utility functions
    def getMatchForNumber(self, matchNumber):
        return [match for match in self.comp.matches if match.number == matchNumber][0]

    def teamsInMatch(self, match):
        return match.redTeams + match.blueTeams

    def teamInMatch(self, team, match):
        return match in team.matches

    def matchIsCompleted(self, match):
        return len(self.getCompletedTIMDsForMatch(match)) == 6 and self.matchHasValuesSet(match)   

    def getCompletedMatchesInCompetition(self):
        return filter(self.matchIsCompleted, self.comp.matches)

    def teamsAreOnSameAllianceInMatch(self, team1, team2, match):
        return team2 in self.getAllianceForTeamInMatch(team1, match)

    def teamsForTeamNumbersOnAlliance(self, alliance):
        return map(self.getTeamForNumber, alliance)

    def getAllianceForMatch(self, match, allianceIsRed):
        return match.redTeams if allianceIsRed else match.blueTeams

    def getAllianceForTeamInMatch(self, team, match):
        return self.getAllianceForMatch(match, self.getTeamAllianceIsRedInMatch(team, match))

    def getFieldsForAllianceForMatch(self, allianceIsRed, match):
        return (match.redScore, match.redAllianceDidBreach, match.redAllianceDidCapture) if allianceIsRed else (
            match.blueScore, match.blueAllianceDidBreach, match.blueAllianceDidCapture)

    def getTeamAllianceIsRedInMatch(self, team, match):
        if team.number == -1 or team in match.redTeams: return True
        if team in match.blueTeams: return False
        else: raise ValueError(str(team.number) not in "Q" + str(match.number))

    # TIMD utility function

    def getCompletedTIMDsForTeam(self, team):
        return filter(self.timdIsCompleted, team.timds)

    def getTIMDsForMatchForAllianceIsRed(self, match, allianceIsRed):
        return filter(lambda t: t.team in match.redTeams, match.timds) if allianceIsRed else filter(lambda t: t.team in match.blueTeams, match.timds) 

    def getCompletedTIMDsForMatchForAllianceIsRed(self, match, allianceIsRed):
        return filter(self.timdIsCompleted, self.getTIMDsForMatchForAllianceIsRed(match, allianceIsRed))

    def getCompletedTIMDsForTeam(self, team):
        return filter(self.timdIsCompleted, team.timds)

    def getCompletedTIMDsForMatch(self, match):
        return filter(self.timdIsCompleted, match.timds)

    def getTIMDForTeamAndMatch(self, team, match):
        return filter(lambda t: t.team == team and t.match == match, self.comp.TIMDs)

    def getCompletedTIMDsInCompetition(self):
        return filter(self.timdIsCompleted, self.comp.TIMDs)

    def TIMCalculatedDataHasValues(self, calculatedData):
        return calculatedData.drivingAbility != None 

    def timdIsCompleted(self, timd):
        return timd.rankTorque != None and timd.numHighShotsMadeTele != None 

    def matchHasValuesSet(self, match):
        return match.redScore != None and match.blueScore != None
  
    def retrieveCompletedTIMDsForTeam(self, team):
        return self.getCompletedTIMDsForTeamNumber(team.number)

    def isSurrogate(self, team, match):
        timd = self.getTIMDForTeamNumberAndMatchNumber(team.number, match.number)
        return timd in self.surrogateTIMDs


    #Calculated Team Data
    
    #Hardcore Math 

    def getAverageForDataFunctionForTeam(self, team, dataFunction):
        validTIMDs = filter(lambda timd: dataFunction(timd) != None, self.getCompletedTIMDsForTeam(team))
        return np.mean(map(dataFunction, validTIMDs)) if len(validTIMDs) > 0 else None     

    def getSumForDataFunctionForTeam(self, team, dataFunction):
        return sum(map(dataFunction, self.getCompletedTIMDsForTeam(team)))

    def getStandardDeviationForDataFunctionForTeam(self, team, dataFunction):
        validTIMDs = filter(lambda timd: dataFunction(timd) != None, self.getCompletedTIMDsForTeam(team))
        return np.std(map(dataFunction, validTIMDs)) if len(validTIMDs) > 0 else None

    def getAverageOfDataFunctionAcrossCompetition(self, dataFunction):
        validData = filter(lambda x: x != None, map(dataFunction, self.teamsWithCalculatedData()))
        return np.mean(validData) if len(validData) > 0 else None

    def getStandardDeviationOfDataFunctionAcrossCompetition(self, dataFunction):
        return utils.rms(map(dataFunction, self.teamsWithCalculatedData()))

    def standardDeviationForRetrievalFunctionForAlliance(self, retrievalFunction, alliance):
        return utils.sumStdDevs(map(retrievalFunction, alliance))

    def monteCarloForMeanForStDevForValueFunction(self, mean, stDev, valueFunction):
        if stDev == 0.0: return 0.0
        return np.std([valueFunction(np.random.normal(mean, stDev)) for i in range(self.monteCarloIterations)])

    def probabilityDensity(self, x, mu, sigma):
        if sigma == 0.0:
            print "sigma is 0"
            return int(x == mu)
        if x != None and mu != None and sigma != None: return 1.0 - stats.norm.cdf(x, mu, sigma)

    def welchsTest(self, mean1, mean2, std1, std2, sampleSize1, sampleSize2):
        if std1 == 0.0 or std2 == 0.0 or sampleSize1 <= 0 or sampleSize2 <= 0: return float(mean1 > mean2)
        numerator = mean1 - mean2
        denominator = ((std1 ** 2) / sampleSize1 + (std2 ** 2) / sampleSize2) ** 0.5
        return numerator / denominator

    def getAverageForDataFunctionForTIMDValues(self, timds, dataFunction):
        values = [dataFunction(timd) for timd in timds]
        return np.mean(values) if len(values) > 0 else None

     #SHOTS DATA
    def TIMDShotAccuracy(self, made, missed):
        return float(made / float(made + missed)) if made + missed != 0 else None

    def totalSDShotPointsForTeam(self, team):
        return utils.sumStdDevs([5 * team.calculatedData.sdHighShotsTele, 10 * team.calculatedData.sdHighShotsAuto, 5 * team.calculatedData.sdLowShotsAuto, 2 * team.calculatedData.sdLowShotsTele])

    def twoBallAutoTIMDsForTeam(self, team):
        return filter(lambda tm: tm.numHighShotsMadeAuto + tm.numHighShotsMissedAuto >= 2, self.getCompletedTIMDsForTeam(team))

    def twoBallAutoTriedPercentage(self, team):
        return float(len(self.twoBallAutoTIMDsForTeam(team))) / len(self.getCompletedTIMDsForTeam(team))

    def twoBallAutoAccuracy(self, team):
        timds = self.twoBallAutoTIMDsForTeam(team)
        return np.mean([timd.calculatedData.highShotAccuracyAuto for timd in timds]) if len(timds) > 0 else None

    def stdDevTeleopShotAbility(self, team):
        return utils.sumStdDevs(5 * team.calculatedData.sdHighShotsTele, 2 * team.calculatedData.sdLowShotsTele)
 
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

    def getTIMDTeleopShotAbility(self, timd):
        return 5 * timd.numHighShotsMadeTele + 2 * timd.numLowShotsMadeTele
   
    
    #SIEGING DATA   
    
    def siegeAbility(self, team):
        return 15 * team.calculatedData.scalePercentage + 5 * team.calculatedData.challengePercentage

    def singleSiegeAbility(self, timd):
        return (15 * utils.convertFirebaseBoolean(timd.didScaleTele) + 5 * utils.convertFirebaseBoolean(timd.didChallengeTele))

    def siegeConsistency(self, team):
        return team.calculatedData.scalePercentage + team.calculatedData.challengePercentage if team.calculatedData.scalePercentage != None and team.calculatedData.challengePercentage != None else None

    def numScaleAndChallengePointsForTeam(self, team):
        if team.calculatedData.siegeAbility != None:
            return team.calculatedData.siegeAbility * len(self.getCompletedTIMDsForTeam(team))

    def numSiegePointsForTIMD(self, timd):
        return 15 * utils.convertFirebaseBoolean(timd.didScaleTele) + 5 * utils.convertFirebaseBoolean(timd.didChallengeTele) 

    
    
    #Defenses

    def stdDevNumCrossingsTeleForTeamForCategory(self, team, category):
        return utils.rms([team.calculatedData.sdSuccessfulDefenseCrossesTele[dKey] for dKey in self.defenseDictionary[category] if self.teamFacedDefense(team, dKey)])

    def stdDevForPredictedDefenseScoreForAllianceForCategory(self, alliance, category):
        mean = self.predictedTeleDefensePointsForAllianceForCategory(alliance, category)
        getStdDevFunction = lambda t: self.stdDevNumCrossingsTeleForTeamForCategory(t, category)
        stdDev = utils.sumStdDevs(map(getStdDevFunction, alliance))
        value = self.monteCarloForMeanForStDevForValueFunction(mean, stdDev, lambda crossings: 5 * min(crossings, 2))
        return value

    def timdHasDefenseExclusion(self, timd, exclusions):
        return timd if len(filter(lambda x: x in timd.timesSuccessfulCrossedDefensesAuto, exclusions)) == 0 else None 
    
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

    def totalCrossesInAutoForTIMD(self, timd):
        return sum([len(value) for value in timd.timesSuccessfulCrossedDefensesAuto.values() if value != None])

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

    def meanDefenseCrossingTimeForTeam(self, team):
        defenseTimes = filter(lambda time: time != None, team.calculatedData.avgTimeForDefenseCrossTele.values())
        if len(defenseTimes) == 0: return None
        return np.mean(defenseTimes)

    def meanDefenseCrossingTimeForCompetition(self):
        times = [self.meanDefenseCrossingTimeForTeam(t) for t in self.comp.teams if self.meanDefenseCrossingTimeForTeam(t) != None]
        return np.mean(times) if len(times) > 0 else None

    def predictedCrossingsForDefenseCategory(self, team, category):
        l = [team.calculatedData.predictedSuccessfulCrossingsForDefenseTele[dKey] for dKey in self.defenseDictionary[category] if self.teamFacedDefense(team, dKey) and team.calculatedData.predictedSuccessfulCrossingsForDefenseTele[dKey] != None]
        return np.mean(l) if len(l) > 0 else 0

    def predictedCrossingsForDefense(self, team, defenseKey):
        return team.calculatedData.predictedSuccessfulCrossingsForDefenseTele[defenseKey]

    def getPredictedCrossingsForAllianceForDefense(self, alliance, defenseKey):
        if self.numTimesCompetitionFacedDefense(defenseKey) <= 0: return None
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

    def numDefensesCrossedForTimeDict(self, timdDict):
        numCrossed = 0
        for value, key in timdDict.iteritems():
            numCrossed += len(value)
        return numCrossed

    def didCrossDefenseAutoForTIMD(self, timd):
        return self.numDefensesCrossedForTimeDict(timd.timesSuccessfulCrossedDefensesAuto) > 0

    def setDefenseValuesForTeam(self, team, keyDict, valueRetrieval, dataModification, valueModification):
        getValueFunc = lambda x, dKey: valueRetrieval(x)[dKey] if dKey in valueRetrieval(x) else []
        avgFunc = lambda dKey: dataModification([valueModification(getValueFunc(t, dKey)) for t in self.timdsWhereTeamFacedDefense(team, dKey)])
        map(lambda dKey: utils.setDictionaryValue(keyDict, dKey, avgFunc(dKey)), self.defenseList)

    def defenseValuesForAverageTeam(self, keyDict, dataModification):
        defDict = keyDict(self.averageTeam)
        avgFunc = lambda dKey: dataModification(map(lambda x: keyDict(x)[dKey], self.teamsWhoHaveFacedDefense(dKey)))
        setDictValueFunc = lambda dKey: utils.setDictionaryValue(defDict, dKey, avgFunc(dKey))
        map(setDictValueFunc, self.defenseList)
        
    def teamDidBreachInMatch(self, team, match):
        return match.redAllianceDidBreach if self.getTeamAllianceIsRedInMatch(team,
                                                                              match) else match.blueAllianceDidBreach
    def avgNumTimesSlowed(self, team, defenseKey):
        sTotal = 0.0
        oTotal = 0.0
        timds = self.timdsWhereTeamFacedDefense(team, defenseKey)
        for timd in timds:
            sTotal += float(timd.numTimesSlowed) 
            oTotal += float(timd.numTimesBeached) + float(timd.numTimesSlowed) + float(timd.numTimesUnaffected)
        if oTotal == 0: return None
        return sTotal / oTotal    

    def defensesCrossableByTeamForDefenseDict(self, team, defDict):
        func = lambda d: defDict[d]
        return ', '.join([dKey for dKey in self.defenseList if func(dKey) != None and func(dKey) > 0])

    def standardDeviationForTeamForCategory(self, team, category):
        sdCrossFunc = lambda x: utils.sumStdDevs([team.calculatedData.sdSuccessfulDefenseCrossesAuto[x], team.calculatedData.sdSuccessfulDefenseCrossesTele[x]])
        return utils.rms([sdCrossFunc(dKey) for dKey in self.defenseDictionary[category] if self.teamFacedDefense(team, dKey)])

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

    def categoryAAverageForDataFunction(self, team, defenseKey, dataFunction):
        a = self.getAverageForDataFunctionForTIMDValues(self.timdsWhereTeamFacedDefense(team, defenseKey), dataFunction)
        return a

    def categoryAAverageDictForDataFunction(self, team, dataFunction):
        return {
            'pc' : self.categoryAAverageForDataFunction(team, 'pc', dataFunction),
            'cdf' : self.categoryAAverageForDataFunction(team, 'cdf', dataFunction)
        }


    # OVERALL DATA
    def autoAbility(self, timd):
        if timd == None: return
        defensesCrossed = 0
        crossesDict = timd.timesSuccessfulCrossedDefensesAuto
        crossesDict = crossesDict.values() if crossesDict != None else ValueError("noCrossesDict")
        defCross = sum([len(d) for d in crossesDict if d != None])
        defensePoints = 10 if defCross >= 1 else 0
        return ((10 * timd.numHighShotsMadeAuto) + (5 * timd.numLowShotsMadeAuto) + (2 * int(utils.convertFirebaseBoolean(timd.didReachAuto))) + (defensePoints))

    def rValuesForAverageFunctionForDict(self, averageFunction, d):
        impossible = True
        values = map(averageFunction, self.teamsWithMatchesCompleted())
        if len(values) == 0:
            return None
        initialValue = values[0]
        for value in values[1:]:
            if value != initialValue: impossible = False
        if impossible: 
            zscores = [0.0 for v in values]
        else: 
            zscores = stats.zscore(values)
        for i in range(len(self.teamsWithMatchesCompleted())):
            d[self.teamsWithMatchesCompleted()[i].number] = zscores[i]

    def drivingAbility(self, team):
        torqueWeight = 0.1
        ballControlWeight = 0
        agilityWeight = 0.4
        defenseWeight = 0
        speedWeight = 0.4
        crossingTimeWeight = -0.2
        meanDefenseCrossingTimeForTeam = self.meanDefenseCrossingTimeForTeam(team)
        meanDefenseCrossingTimeForCompetition = self.meanDefenseCrossingTimeForCompetition()
        crossProp = ((meanDefenseCrossingTimeForTeam or 0) / meanDefenseCrossingTimeForCompetition) if meanDefenseCrossingTimeForCompetition > 0 else 0
        if meanDefenseCrossingTimeForTeam == None: return 0
        elif meanDefenseCrossingTimeForCompetition == None: return None
        defenseCrossTime = crossingTimeWeight * crossProp * 2

        torque = torqueWeight * team.calculatedData.avgTorque
        agility = agilityWeight * team.calculatedData.avgAgility
        defense = defenseWeight * team.calculatedData.avgDefense
        speed = speedWeight * team.calculatedData.avgSpeed

        
        return defenseCrossTime + torque + agility + defense + speed

    def predictedScoreForAllianceWithNumbers(self, allianceNumbers):
        return self.predictedScoreForAlliance(self.teamsForTeamNumbersOnAlliance(allianceNumbers))

    def stdDevPredictedScoreForAlliance(self, alliance):
        alliance = map(self.replaceWithAverageIfNecessary, alliance)
        allianceTeleopShotPointStdDev = utils.sumStdDevs(map(lambda t: t.calculatedData.sdTeleopShotAbility, alliance))
        allianceSiegePointsStdDev = utils.sumStdDevs(map(lambda t: t.calculatedData.sdSiegeAbility, alliance))
        allianceAutoPointsStdDev = utils.sumStdDevs(map(lambda t: t.calculatedData.sdAutoAbility, alliance))
        allianceDefensePointsTeleStdDev = utils.sumStdDevs(map(lambda cKey: self.stdDevForPredictedDefenseScoreForAllianceForCategory(alliance, cKey), self.categories))          

        return utils.sumStdDevs([allianceTeleopShotPointStdDev,
                                 allianceSiegePointsStdDev,
                                 allianceAutoPointsStdDev,
                                 allianceDefensePointsTeleStdDev])

    def stdDevPredictedScoreForAllianceNumbers(self, allianceNumbers):
        return self.stdDevPredictedScoreForAlliance(self.teamsForTeamNumbersOnAlliance(allianceNumbers))

    def predictedScoreForAlliance(self, alliance):
   
        alliance = map(self.replaceWithAverageIfNecessary, alliance)
        allianceTeleopShotPoints = sum(
            [t.calculatedData.teleopShotAbility for t in alliance if t.calculatedData.teleopShotAbility])
        allianceSiegePoints = sum(
            [t.calculatedData.siegeAbility for t in alliance if t.calculatedData.siegeAbility])
        allianceAutoPoints = sum(
            [t.calculatedData.autoAbility for t in alliance if t.calculatedData.autoAbility])
        alliancePredictedCrossingsRetrievalFunction = lambda c: self.predictedTeleDefensePointsForAllianceForCategory(alliance, c)
        allianceDefensePointsTele = sum(map(alliancePredictedCrossingsRetrievalFunction, self.categories))
        return allianceTeleopShotPoints + allianceSiegePoints + allianceAutoPoints + allianceDefensePointsTele

    def predictedScoreForAllianceWithCaptureAndBreachPoints(self, alliance):
        return 20 * self.breachChanceForAlliance(alliance) + 25 * self.captureChanceForAlliance(alliance) + self.predictedScoreForAlliance(alliance)

    def firstPickAbility(self, team):
        ourTeam = self.getTeamForNumber(self.ourTeamNum)
        if self.predictedScoreForAlliance([ourTeam, team]) == None or math.isnan(self.predictedScoreForAlliance([ourTeam, team])): return 
        return self.predictedScoreForAllianceWithCaptureAndBreachPoints([ourTeam, team])
    
    def overallSecondPickAbility(self, team): 
        functionalPercentage = (1 - team.calculatedData.disfunctionalPercentage)
        autoAndSiege = team.calculatedData.autoAbility + team.calculatedData.siegeAbility
        speed = (team.calculatedData.RScoreSpeed) * 2.4
        agility = (team.calculatedData.RScoreAgility) * 1.2
        time = self.meanDefenseCrossingTimeForTeam(team)
        if time == None: return 0
        defenses = (self.meanDefenseCrossingTimeForTeam(team) / self.meanDefenseCrossingTimeForCompetition()) * -2.4
        return functionalPercentage * (autoAndSiege + speed + agility + defenses)

    def predictedScoreForMatchForAlliance(self, match, allianceIsRed):
        return match.calculatedData.predictedRedScore if allianceIsRed else match.calculatedData.predictedBlueScore

    def sdPredictedScoreForMatchForAlliance(self, match, allianceIsRed):
        return match.calculatedData.sdPredictedRedScore if allianceIsRed else match.calculatedData.sdPredictedBlueScore

    def getAvgNumCompletedTIMDsForTeamsOnAlliance(self, alliance):
        return np.mean(map(lambda t: len(self.getCompletedTIMDsForTeam(t)), alliance)) # TODO:WATCHOUT!!!

    def getAvgNumCompletedTIMDsForAlliance(self, alliance):
        return self.getAvgNumCompletedTIMDsForTeamsOnAlliance(alliance)

    def sampleSizeForMatchForAlliance(self, alliance):
        return self.getAvgNumCompletedTIMDsForAlliance(alliance)

    
    #PROBABILITIES

    def breachChanceForAlliance(self, alliance):
        return max(map(lambda t: t.calculatedData.breachPercentage, alliance))

    def breachChanceForAllianceNumbers(self, allianceNumbers):
        return self.breachChanceForAlliance(self.teamsForTeamNumbersOnAlliance(allianceNumbers))

    def getBreachChanceForMatchForAllianceIsRed(self, match, allianceIsRed):
        return match.calculatedData.redBreachChance if allianceIsRed else match.calculatedData.blueBreachChance

    def getCaptureChanceForMatchForAllianceIsRed(self, match, allianceIsRed):
        return match.calculatedData.redCaptureChance if allianceIsRed else match.calculatedData.blueCaptureChance

    def getWinChanceForMatchForAllianceIsRed(self, match, allianceIsRed):
        winChance = match.calculatedData.redWinChance if allianceIsRed else match.calculatedData.blueWinChance
        return winChance if not math.isnan(winChance) else None

    def captureChanceForAlliance(self, alliance):
        alliance = map(self.replaceWithAverageIfNecessary, alliance)
        siegeConsistencies = filter(lambda sc: sc != None, [t.calculatedData.siegeConsistency for t in alliance])
        if len(siegeConsistencies) == None:
            return self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.siegeConsistency)
        siegeChance = np.prod(siegeConsistencies)
        return siegeChance * self.probabilityDensity(10.0, self.numShotsForAlliance(alliance), self.stdDevNumShotsForAlliance(alliance))

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
        winChance = stats.t.cdf(tscoreRPs, np.mean([sampleSize, opposingSampleSize]))
        return winChance if not math.isnan(winChance) else 0


    # Seeding
    
    def getSeedingFunctions(self):
        return [lambda t: t.calculatedData.actualNumRPs, lambda t: self.cumulativeSumAutoPointsForTeam,
                lambda t: self.cumulativeSumSiegePointsForTeam]

    def getPredictedSeedingFunctions(self):
        return [lambda t: t.calculatedData.predictedNumRPs, self.cumulativeSumPredictedAutoPointsForTeam, self.cumulativeSumPredictedSiegePointsForTeam]

    def predictedNumberOfRPs(self, team):
        predictedRPsFunction = lambda m: self.predictedRPsForAllianceForMatch(self.getTeamAllianceIsRedInMatch(team, m), m)
        predictedRPs = sum([predictedRPsFunction(m) for m in self.getMatchesForTeam(team) if not self.matchIsCompleted(m) and predictedRPsFunction(m) != None])
        return predictedRPs + self.actualNumberOfRPs(team)

    def actualNumberOfRPs(self, team):
        return self.getSumForDataFunctionForTeam(team, lambda tm: tm.calculatedData.numRPs)   

    def scoreRPsGainedFromMatchWithScores(self, score, opposingScore):
        if score > opposingScore: return 2
        elif score == opposingScore: return 1
        else: return 0

    def RPsGainedFromMatchForAlliance(self, allianceIsRed, match):
        ourFields = self.getFieldsForAllianceForMatch(allianceIsRed, match)
        opposingFields = self.getFieldsForAllianceForMatch(not allianceIsRed, match)
        numRPs = self.scoreRPsGainedFromMatchWithScores(ourFields[0], opposingFields[0])
        return numRPs + int(utils.convertFirebaseBoolean(ourFields[1])) + int(utils.convertFirebaseBoolean(ourFields[2])) 

    def RPsGainedFromMatchForTeam(self, team, match):
        return self.RPsGainedFromMatchForAlliance(self.getTeamAllianceIsRedInMatch(team, match), match)

    def getAutoPointsForMatchForAllianceIsRed(self, match, allianceIsRed):
        timds = self.getCompletedTIMDsForMatchForAllianceIsRed(match, allianceIsRed)
        return sum(map(lambda tm: tm.calculatedData.autoAbility or 0, timds))

    def getAutoPointsForTeamAllianceInMatch(self, team, match):
        return self.getAutoPointsForMatchForAllianceIsRed(match, self.getTeamAllianceIsRedInMatch(team, match))

    def cumulativeSumAutoPointsForTeam(self, team):
        return sum([self.getAutoPointsForTeamAllianceInMatch(team, m) for m in self.getCompletedMatchesForTeam(team)])
        
    def getSiegePointsForMatchForAllianceIsRed(self, match, allianceIsRed):
        timds = self.getCompletedTIMDsForMatchForAllianceIsRed(match, allianceIsRed)
        return sum(map(lambda tm: tm.calculatedData.siegeAbility, timds))

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
        return self.getPredictedSiegePointsForMatchForAllianceIsRed(match, self.getTeamAllianceIsRedInMatch(team, match))

    def cumulativeSumPredictedSiegePointsForTeam(self, team):
        return sum([self.getPredictedSiegePointsForTeamAllianceInMatch(team, m) for m in self.getCompletedMatchesForTeam(team)])  

    def predictedRPsForAllianceForMatch(self, allianceIsRed, match):
        alliance = self.getAllianceForMatch(match, allianceIsRed)
        alliance = map(self.replaceWithAverageIfNecessary, alliance)
        breachRPs = self.getBreachChanceForMatchForAllianceIsRed(match, allianceIsRed)
        captureRPs = self.getCaptureChanceForMatchForAllianceIsRed(match, allianceIsRed)
        scoreRPs = 2 * (self.getWinChanceForMatchForAllianceIsRed(match, allianceIsRed) or 0)
        RPs = breachRPs or 0 + captureRPs or 0 + scoreRPs or 0 
        return RPs if not math.isnan(RPs) else None

    def teamsSortedByRetrievalFunctions(self, retrievalFunctions):
        teams = self.teamsWithMatchesCompleted()
        return sorted(teams, key=lambda t: (retrievalFunctions[0](t), retrievalFunctions[1](t), retrievalFunctions[2](t)), reverse=True)  

    def getTeamSeed(self, team):
        return int(filter(lambda x: int(x[1]) == team.number, self.cachedComp.actualSeedings)[0][0])       

    def getTeamRPsFromTBA(self, team):
        return int(float(filter(lambda x: int(x[1]) == team.number, self.cachedComp.actualSeedings)[0][2]))       

    #CACHING

    def cacheFirstTeamData(self):
        for team in self.comp.teams:
            self.doCachingForTeam(team)
        self.doCachingForTeam(self.averageTeam)
        self.cachedComp.teamsWithMatchesCompleted = self.findTeamsWithMatchesCompleted()

    def rScoreParams(self):
        return [(lambda t: t.calculatedData.avgSpeed, self.cachedComp.speedZScores),
                    (lambda t: t.calculatedData.avgTorque, self.cachedComp.torqueZScores),
                    (lambda t: t.calculatedData.avgDefense, self.cachedComp.defenseZScores),
                    (lambda t: t.calculatedData.avgBallControl, self.cachedComp.ballControlZScores),
                    (lambda t: t.calculatedData.avgAgility, self.cachedComp.agilityZScores),
            (lambda t: t.calculatedData.avgDrivingAbility, self.cachedComp.drivingAbilityZScores)]

    def cacheSecondTeamData(self):
        map(lambda (func, dictionary): self.rValuesForAverageFunctionForDict(func, dictionary), self.rScoreParams())
        map(self.doSecondCachingForTeam, self.comp.teams)
        self.cachedComp.actualSeedings = self.TBAC.makeEventRankingsRequest()
        self.cachedComp.predictedSeedings = self.teamsSortedByRetrievalFunctions(self.getPredictedSeedingFunctions()) 
        self.doSecondCachingForTeam(self.averageTeam)

    def doCachingForTeam(self, team):
        cachedData = self.cachedTeamDatas[team.number]
        cachedData.completedTIMDs = self.retrieveCompletedTIMDsForTeam(team)
        cachedData.defensesFaced = filter(lambda dKey: self.getTeamFacedDefense(team, dKey), self.defenseList)

    def doSecondCachingForTeam(self, team):
        cachedData = self.cachedTeamDatas[team.number]
        map(lambda dKey: utils.setDictionaryValue(cachedData.alphas, dKey, self.alphaForTeamForDefense(team, dKey)), self.defenseList)

    def cacheScoutData(self):
        self.cachedComp.TBAMatches = self.makeTBAMatches()
        self.cachedComp.SARs = self.scoutAccRank()


    #CALCULATIONS        

    def getFirstCalculationsForAverageTeam(self): 
        a = self.averageTeam.calculatedData

        #Super Averages
        a.avgTorque = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgTorque)  # Checked
        a.avgSpeed = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgSpeed)
        a.avgAgility = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgAgility)  # Checked
        a.avgDefense = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgDefense)  # Checked
        a.avgBallControl = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.avgBallControl)  # Checked
        a.avgDrivingAbility = self.getAverageOfDataFunctionAcrossCompetition(lambda t: self.drivingAbility(t))
        a.disabledPercentage = self.getAverageOfDataFunctionAcrossCompetition( 
            lambda t: t.calculatedData.disabledPercentage)
        a.incapacitatedPercentage = self.getAverageOfDataFunctionAcrossCompetition( 
            lambda t: t.calculatedData.incapacitatedPercentage)
        a.disfunctionalPercentage = None if None in (a.disabledPercentage, a.incapacitatedPercentage) else a.disabledPercentage + a.incapacitatedPercentage

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
        a.sdHighShotsTele = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.sdHighShotsTele)  # Checked
        a.sdLowShotsTele = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.sdLowShotsTele)  # Checked
        a.sdGroundIntakes = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.sdGroundIntakes)  # Checked
        a.sdShotsBlocked = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.sdShotsBlocked)  # Checked
        a.sdTeleopShotAbility = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.teleopShotAbility)
        a.sdSiegeAbility = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.siegeAbility)
        a.sdAutoAbility = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.autoAbility)
        self.defenseValuesForAverageTeam(lambda t: t.calculatedData.avgSuccessfulTimesCrossedDefensesAuto,lambda x: np.mean(x) if x != None and len(x) != 0 else 0)
        self.defenseValuesForAverageTeam(lambda t: t.calculatedData.avgFailedTimesCrossedDefensesAuto, lambda x: np.mean(x) if x != None and len(x) != 0 else 0)
        self.defenseValuesForAverageTeam(lambda t: t.calculatedData.avgSuccessfulTimesCrossedDefensesTele,lambda x: np.mean(x) if x != None and len(x) != 0 else 0)
        self.defenseValuesForAverageTeam(lambda t: t.calculatedData.avgFailedTimesCrossedDefensesTele, lambda x: np.mean(x) if x != None and len(x) != 0 else 0)
        self.defenseValuesForAverageTeam(lambda t: t.calculatedData.sdSuccessfulDefenseCrossesAuto, lambda x: utils.rms(x) if x != None and len(x) != 0 else 0)
        self.defenseValuesForAverageTeam(lambda t: t.calculatedData.sdFailedDefenseCrossesAuto, lambda x: utils.rms(x) if x != None and len(x) != 0 else 0)
        self.defenseValuesForAverageTeam(lambda t: t.calculatedData.sdSuccessfulDefenseCrossesTele, lambda x: utils.rms(x) if x != None and len(x) != 0 else 0)
        self.defenseValuesForAverageTeam(lambda t: t.calculatedData.sdFailedDefenseCrossesTele, lambda x: utils.rms(x) if x != None and len(x) != 0 else 0)
        a.numScaleAndChallengePoints = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.numScaleAndChallengePoints) # Checked
        a.breachPercentage = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.breachPercentage)

    def getSecondCalculationsForAverageTeam(self):
        a = self.averageTeam.calculatedData

        a.RScoreTorque = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.RScoreTorque)
        a.RScoreSpeed = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.RScoreSpeed)
        a.RScoreDefense = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.RScoreDefense)
        a.RScoreBallControl = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.RScoreBallControl)
        a.RScoreDrivingAbility = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.RScoreDrivingAbility)
        a.avgSuccessfulTimesCrossedDefenses = utils.dictSum(a.avgSuccessfulTimesCrossedDefensesAuto,
                                                            a.avgSuccessfulTimesCrossedDefensesTele)
        a.firstPickAbility = self.firstPickAbility(self.averageTeam)
        a.actualNumRPs = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.actualNumRPs)
        a.predictedNumRPs = self.getAverageOfDataFunctionAcrossCompetition(lambda t: t.calculatedData.predictedNumRPs)




    def doFirstCalculationsForTeam(self, team):
        if not len(self.getCompletedTIMDsForTeam(team)) <= 0:
            if not self.teamCalculatedDataHasValues(team.calculatedData):
                team.calculatedData = DataModel.CalculatedTeamData()
            t = team.calculatedData
            t.avgTorque = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankTorque)  # Checked
            t.avgSpeed = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankSpeed)
            t.avgAgility = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankAgility)  # Checked
            t.avgDefense = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankDefense)  # Checked
            t.avgBallControl = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankBallControl)  # Checked
            t.avgDrivingAbility = self.drivingAbility(team)
            t.disabledPercentage = self.getAverageForDataFunctionForTeam(team, lambda timd: utils.convertFirebaseBoolean(timd.didGetDisabled))
            t.incapacitatedPercentage = self.getAverageForDataFunctionForTeam(team, lambda timd: utils.convertFirebaseBoolean(timd.didGetIncapacitated))
            t.disfunctionalPercentage = t.disabledPercentage + t.incapacitatedPercentage
            
            # Auto
            t.autoAbility = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.calculatedData.autoAbility)
            t.autoAbilityExcludeD = self.getAverageForDataFunctionForTeam(team, 
                                    lambda timd: self.autoAbility(self.timdHasDefenseExclusion(timd, self.defenseDictionary['d'])))
            t.autoAbilityExcludeLB = self.getAverageForDataFunctionForTeam(team, 
                                    lambda timd: self.autoAbility(self.timdHasDefenseExclusion(timd, self.defenseDictionary['e'])))
            t.avgHighShotsAuto = self.getAverageForDataFunctionForTeam(team,  lambda timd: timd.numHighShotsMadeAuto)  # Checked
            t.avgLowShotsAuto = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numLowShotsMadeAuto)  # Checked   
            t.reachPercentage = self.getAverageForDataFunctionForTeam(team, lambda timd: utils.convertFirebaseBoolean(timd.didReachAuto))
            t.highShotAccuracyAuto = self.getAverageForDataFunctionForTeam(team, 
                                    lambda timd: self.TIMDShotAccuracy(timd.numHighShotsMadeAuto, timd.numHighShotsMissedAuto))# Checked
            t.lowShotAccuracyAuto = self.getAverageForDataFunctionForTeam(team, 
                                    lambda timd: self.TIMDShotAccuracy(timd.numLowShotsMadeAuto, timd.numLowShotsMissedAuto)) # Checked
            t.numAutoPoints = self.getAverageForDataFunctionForTeam(team, self.autoAbility)  # Checked
            t.avgMidlineBallsIntakedAuto = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.calculatedData.numBallsIntakedOffMidlineAuto)
            t.sdMidlineBallsIntakedAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.calculatedData.numBallsIntakedOffMidlineAuto)
            t.sdHighShotsAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numHighShotsMadeAuto)  # Checked
            t.sdLowShotsAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numLowShotsMadeAuto)  # Checked
            t.sdBallsKnockedOffMidlineAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numBallsKnockedOffMidlineAuto)  # Checked

            #Tele
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
                                    lambda timd: self.TIMDShotAccuracy(timd.numHighShotsMadeTele, timd.numHighShotsMissedTele))                           # Checked
            t.lowShotAccuracyTele = self.getAverageForDataFunctionForTeam(team, 
                                    lambda timd: self.TIMDShotAccuracy(timd.numLowShotsMadeTele, timd.numLowShotsMissedTele))
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

            t.avgNumTimesBeached = self.categoryAAverageDictForDataFunction(team, lambda timd: timd.numTimesBeached)
            t.avgNumTimesSlowed = { "pc" : self.avgNumTimesSlowed(team, "pc"), "cdf" : self.avgNumTimesSlowed(team, "cdf") }
            t.avgNumTimesUnaffected = self.categoryAAverageDictForDataFunction(team, lambda timd: timd.numTimesUnaffected)
            sumCategoryADataPointDict = utils.dictSum(t.avgNumTimesUnaffected, utils.dictSum(t.avgNumTimesBeached, t.avgNumTimesSlowed))
            
            t.beachedPercentage = utils.dictQuotient(t.avgNumTimesBeached, sumCategoryADataPointDict)
            
            t.slowedPercentage = utils.dictQuotient(t.avgNumTimesSlowed, sumCategoryADataPointDict)
            t.unaffectedPercentage = utils.dictQuotient(t.avgNumTimesUnaffected, sumCategoryADataPointDict)
            t.avgNumTimesCrossedDefensesAuto = self.getAverageForDataFunctionForTeam(team, lambda tm: tm.calculatedData.totalNumTimesCrossedDefensesAuto)
            self.setDefenseValuesForTeam(team, t.avgSuccessfulTimesCrossedDefensesTele, lambda tm: tm.timesSuccessfulCrossedDefensesTele, 
                lambda x: np.mean(x) if x!= None and len(x) > 0 else 0, lambda y: len(y) if y != None else 0)
            self.setDefenseValuesForTeam(team, t.avgSuccessfulTimesCrossedDefensesAuto, lambda tm: tm.timesSuccessfulCrossedDefensesAuto, 
                lambda x: np.mean(x) if x!= None and len(x) > 0 else 0, lambda y: len(y) if y != None else 0)
            self.setDefenseValuesForTeam(team, t.avgFailedTimesCrossedDefensesTele, lambda tm: tm.timesFailedCrossedDefensesTele, 
                lambda x: np.mean(x) if x!= None and len(x) > 0 else 0, lambda y: len(y) if y != None else 0)
            self.setDefenseValuesForTeam(team, t.avgFailedTimesCrossedDefensesAuto, lambda tm: tm.timesFailedCrossedDefensesAuto, 
                lambda x: np.mean(x) if x!= None and len(x) > 0 else 0, lambda y: len(y) if y != None else 0)
            self.setDefenseValuesForTeam(team, t.avgTimeForDefenseCrossTele, lambda tm: tm.timesSuccessfulCrossedDefensesTele, 
                lambda x: np.mean(x) if x!= None and len(x) > 0 else 0, lambda y: np.mean(y) if y != None and len(y) > 0 else 0)
            self.setDefenseValuesForTeam(team, t.avgTimeForDefenseCrossAuto, lambda tm: tm.timesSuccessfulCrossedDefensesAuto, 
                lambda x: np.mean(x) if x!= None and len(x) > 0 else 0, lambda y: np.mean(y) if y != None and len(y) > 0 else 0)
            self.setDefenseValuesForTeam(team, t.sdSuccessfulDefenseCrossesAuto, lambda tm: tm.timesSuccessfulCrossedDefensesAuto,
                lambda x: utils.rms(x) if x != None and len(x) > 0 else 0, lambda y: len(y) if y != None else 0)
            self.setDefenseValuesForTeam(team, t.sdSuccessfulDefenseCrossesTele, lambda tm: tm.timesSuccessfulCrossedDefensesTele,
                lambda x: utils.rms(x) if x != None and len(x) > 0 else 0, lambda y: len(y) if y != None else 0)
            self.setDefenseValuesForTeam(team, t.sdFailedDefenseCrossesAuto, lambda tm: tm.timesFailedCrossedDefensesAuto,
                lambda x: utils.rms(x) if x != None and len(x) > 0 else 0, lambda y: len(y) if y != None else 0)
            self.setDefenseValuesForTeam(team, t.sdFailedDefenseCrossesTele, lambda tm: tm.timesFailedCrossedDefensesTele,
                lambda x: utils.rms(x) if x != None and len(x) > 0 else 0, lambda y: len(y) if y != None else 0)
            print "Completed first calcs for " + str(team.number)
                
    def doBetweenFirstAndSecondCalculationsForTeams(self):
        map(self.doBetweenFirstAndSecondCalculationsForTeam, self.comp.teams)
        self.doBetweenFirstAndSecondCalculationsForTeam(self.averageTeam)

    def doBetweenFirstAndSecondCalculationsForTeam(self, team):
        if not len(self.getCompletedTIMDsForTeam(team)) <= 0:
            func = lambda dKey: utils.setDictionaryValue(team.calculatedData.predictedSuccessfulCrossingsForDefenseTele, dKey, self.predictedCrosses(team, dKey))
            map(func, self.defenseList)            

    def doSecondCalculationsForTeam(self, team):
        if not len(self.getCompletedTIMDsForTeam(team)) <= 0:
            t = team.calculatedData
            t.predictedNumRPs = self.predictedNumberOfRPs(team)
            t.actualNumRPs = self.getTeamRPsFromTBA(team)
            t.actualSeed = self.getTeamSeed(team)
            t.predictedSeed = self.cachedComp.predictedSeedings.index(team) + 1
            t.RScoreTorque = self.cachedComp.torqueZScores[team.number]
            t.RScoreSpeed = self.cachedComp.speedZScores[team.number]
            t.RScoreAgility = self.cachedComp.agilityZScores[team.number]
            t.RScoreDefense = self.cachedComp.defenseZScores[team.number]
            t.RScoreBallControl = self.cachedComp.ballControlZScores[team.number]
            t.RScoreDrivingAbility = self.cachedComp.drivingAbilityZScores[team.number]
            t.avgSuccessfulTimesCrossedDefenses = utils.dictSum(t.avgSuccessfulTimesCrossedDefensesAuto,
                                                          t.avgSuccessfulTimesCrossedDefensesTele)
            t.blockingAbility = (t.avgShotsBlocked - self.averageTeam.calculatedData.avgShotsBlocked) * self.averageTeam.calculatedData.highShotAccuracyTele * 5
            t.defensesCrossableAuto = self.defensesCrossableByTeamForDefenseDict(team, t.avgSuccessfulTimesCrossedDefensesAuto)
            t.defensesCrossableTele = self.defensesCrossableByTeamForDefenseDict(team, t.avgSuccessfulTimesCrossedDefensesTele)
            t.firstPickAbility = self.firstPickAbility(team) # Checked  
            t.overallSecondPickAbility = self.overallSecondPickAbility(team) # Checked
            print "Completed second calcs for team " + str(team.number)

    def doFirstCalculationsForMatch(self, match): #This entire thing being looped is what takes a while
        print "Performing calculations for match Q" + str(match.number)
        if self.matchIsCompleted(match):
            match.calculatedData.actualBlueRPs = self.RPsGainedFromMatchForAlliance(True, match)
            match.calculatedData.actualRedRPs = self.RPsGainedFromMatchForAlliance(False, match)
        match.calculatedData.blueBreachChance = self.breachChanceForAllianceNumbers(match.blueAllianceTeamNumbers)
        match.calculatedData.redBreachChance = self.breachChanceForAllianceNumbers(match.redAllianceTeamNumbers)
        match.calculatedData.blueCaptureChance = self.captureChanceForAllianceNumbers(match.blueAllianceTeamNumbers)
        match.calculatedData.redCaptureChance = self.captureChanceForAllianceNumbers(match.blueAllianceTeamNumbers)  
        match.calculatedData.predictedBlueScore = self.predictedScoreForAllianceWithNumbers(match.blueAllianceTeamNumbers)
        match.calculatedData.predictedRedScore = self.predictedScoreForAllianceWithNumbers(match.redAllianceTeamNumbers)
        match.calculatedData.sdPredictedBlueScore = self.stdDevPredictedScoreForAllianceNumbers(match.blueAllianceTeamNumbers)
        match.calculatedData.sdPredictedRedScore = self.stdDevPredictedScoreForAllianceNumbers(match.redAllianceTeamNumbers) 
        match.calculatedData.blueWinChance = self.winChanceForMatchForAllianceIsRed(match, False)
        match.calculatedData.redWinChance = self.winChanceForMatchForAllianceIsRed(match, True)
        match.calculatedData.predictedBlueRPs = self.predictedRPsForAllianceForMatch(False, match)
        match.calculatedData.predictedRedRPs = self.predictedRPsForAllianceForMatch(True, match)
        print "Done! Match " + str(match.number)

    def doFirstTeamCalculations(self):
        map(self.doFirstCalculationsForTeam, self.comp.teams)
        self.getFirstCalculationsForAverageTeam()

    def doSecondTeamCalculations(self):
        map(self.doSecondCalculationsForTeam, self.comp.teams)
        self.getSecondCalculationsForAverageTeam()

    def doMatchesCalculations(self):
        map(self.doFirstCalculationsForMatch, self.comp.matches)
    
    def writeCalculationDiagnostic(self, time):
        with open('./diagnostics.txt', 'a') as file:
            file.write('Time: ' + str(time) + '    TIMDs: ' + str(len(self.getCompletedTIMDsInCompetition())) + '\n')
            file.close()    

    def doCalculations(self, FBC):
        isData = len(self.getCompletedTIMDsInCompetition()) > 0
        if isData:
            startTime = time.time()
            threads = []
            manager = multiprocessing.Manager()
            calculatedTIMDs = manager.list()
            numTIMDsCalculating = 0

            for timd in self.comp.TIMDs:
                thread = FirstTIMDProcess(timd, calculatedTIMDs, self)
                threads.append(thread)
                thread.start()
            map(lambda t: t.join(), threads)
            self.comp.TIMDs = [timd for timd in calculatedTIMDs]
            self.cacheFirstTeamData()
            self.doFirstTeamCalculations()
            self.cacheSecondTeamData()
            self.doBetweenFirstAndSecondCalculationsForTeams()
            self.doMatchesCalculations()
            self.doSecondTeamCalculations()
            self.updateCurrentMatchNum()
            FBC.addCompInfoToFirebase()
            #map(FBC.addCalculatedTeamDataToFirebase, self.teamsWithMatchesCompleted())                            # If multiprocesses
            #map(FBC.addCalculatedTIMDataToFirebase, self.getCompletedTIMDsInCompetition())                        # fail, uncomment
            #map(FBC.addCalculatedMatchDataToFirebase, self.comp.matches)                    # these lines
            
            objects = self.teamsWithMatchesCompleted() + self.getCompletedTIMDsInCompetition() + self.comp.matches  # In case of 
            for ob in objects:                                                                                      # failure, comment
                process = FirebaseWriteObjectProcess(ob, FBC)                                                       # out these four 
                process.start()                                                                                     # lines
            
            endTime = time.time()

            self.writeCalculationDiagnostic(endTime - startTime)

        else:
            print "No Data"

    def adjustSchedule(self):
        surrogateTIMDs = []
        a = ""
        while True:
            a = raw_input("Enter surrogate team number and match number (e.g. 254Q23): ")
            if a == "f" or a == "": break
            surrogateTIMDs.append(self.getTIMDForTeamNumberAndMatchNumber(int(re.split('Q', a)[0]), int(re.split('Q', a)[1])))
        self.surrogateTIMDs = surrogateTIMDs

   
    def updateCurrentMatchNum(self):
        for m in sorted(self.comp.matches, key=lambda match: match.number, reverse=False):
            print m.number
            if m.redScore == None and m.blueScore == None:
                self.comp.currentMatchNum = m.number
		return m.number
        return 0


        
