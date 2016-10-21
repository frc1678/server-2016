import utils
import pdb

def getThirdTeamCalcDataKeys(calc):
	return {
		"predictedNumRPs" : lambda team: calc.predictedNumberOfRPs(team),
        "actualNumRPs" : lambda team: calc.getTeamRPsFromTBA(team),
        "actualSeed" : lambda team: calc.getTeamSeed(team),
        "predictedSeed" : lambda team: calc.cachedComp.predictedSeedings.index(team) + 1,
        "RScoreTorque" : lambda team: calc.cachedComp.torqueZScores[team.number],
        "RScoreSpeed" : lambda team: calc.cachedComp.speedZScores[team.number],
        "RScoreAgility" : lambda team: calc.cachedComp.agilityZScores[team.number],
        "RScoreDefense" : lambda team: calc.cachedComp.defenseZScores[team.number],
        "RScoreBallControl" : lambda team: calc.cachedComp.ballControlZScores[team.number],
        "RScoreDrivingAbility" : lambda team: calc.cachedComp.drivingAbilityZScores[team.number],
        "avgSuccessfulTimesCrossedDefenses" : lambda team: utils.dictSum(team.calculatedData.avgSuccessfulTimesCrossedDefensesAuto,
                                                      team.calculatedData.avgSuccessfulTimesCrossedDefensesTele),
        "blockingAbility" : lambda team: (team.calculatedData.avgShotsBlocked - calc.averageTeam.calculatedData.avgShotsBlocked) * calc.averageTeam.calculatedData.highShotAccuracyTele * 5,
        "defensesCrossableAuto" : lambda team: calc.defensesCrossableByTeamForDefenseDict(team, team.calculatedData.avgSuccessfulTimesCrossedDefensesAuto),
        "defensesCrossableTele" : lambda team: calc.defensesCrossableByTeamForDefenseDict(team, team.calculatedData.avgSuccessfulTimesCrossedDefensesTele),
        "firstPickAbility" : lambda team: calc.firstPickAbility(team),
        "overallSecondPickAbility" : lambda team: calc.overallSecondPickAbility(team)
	}

def getFirstTeamCalcDataKeys(calc):
	sumCategoryADataPointDict = lambda team: utils.dictSum(team.calculatedData.avgNumTimesUnaffected, utils.dictSum(team.calculatedData.avgNumTimesBeached, team.calculatedData.avgNumTimesSlowed))

	return {
		"avgTorque" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankTorque),  # Checked
        "avgSpeed" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankSpeed),
        "avgAgility" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankAgility),  # Checked
        "avgDefense" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankDefense),  # Checked
        "avgBallControl" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankBallControl),  # Checked
        "avgDrivingAbility" : lambda team: calc.drivingAbility(team),
        "disabledPercentage" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda timd: utils.convertFirebaseBoolean(timd.didGetDisabled)),
        "incapacitatedPercentage" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda timd: utils.convertFirebaseBoolean(timd.didGetIncapacitated)),
        "disfunctionalPercentage" : lambda team: team.calculatedData.disabledPercentage + team.calculatedData.incapacitatedPercentage,
        
        # Auto
        "autoAbility" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda timd: timd.calculatedData.autoAbility),
        "autoAbilityExcludeD" : lambda team: calc.getAverageForDataFunctionForTeam(team, 
                                lambda timd: calc.autoAbility(calc.timdHasDefenseExclusion(timd, calc.defenseDictionary['d']))),
        "autoAbilityExcludeLB" : lambda team: calc.getAverageForDataFunctionForTeam(team, 
                                lambda timd: calc.autoAbility(calc.timdHasDefenseExclusion(timd, calc.defenseDictionary['e']))),
        "avgHighShotsAuto" : lambda team: calc.getAverageForDataFunctionForTeam(team,  lambda timd: timd.numHighShotsMadeAuto),  # Checked
        "avgLowShotsAuto" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda timd: timd.numLowShotsMadeAuto),  # Checked   
        "reachPercentage" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda timd: utils.convertFirebaseBoolean(timd.didReachAuto)),
        "highShotAccuracyAuto" : lambda team: calc.getAverageForDataFunctionForTeam(team, 
                                lambda timd: calc.TIMDShotAccuracy(timd.numHighShotsMadeAuto, timd.numHighShotsMissedAuto)),# Checked
        "lowShotAccuracyAuto" : lambda team: calc.getAverageForDataFunctionForTeam(team, 
                                lambda timd: calc.TIMDShotAccuracy(timd.numLowShotsMadeAuto, timd.numLowShotsMissedAuto)), # Checked
        "avgMidlineBallsIntakedAuto" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda timd: timd.calculatedData.numBallsIntakedOffMidlineAuto),
        "sdMidlineBallsIntakedAuto" : lambda team: calc.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.calculatedData.numBallsIntakedOffMidlineAuto),
        "sdHighShotsAuto" : lambda team: calc.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numHighShotsMadeAuto),  # Checked
        "sdLowShotsAuto" : lambda team: calc.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numLowShotsMadeAuto),  # Checked
        "sdBallsKnockedOffMidlineAuto" : lambda team: calc.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numBallsKnockedOffMidlineAuto),
    
    #Tele
        "scalePercentage" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda timd: int(
            utils.convertFirebaseBoolean(timd.didScaleTele))),
        "challengePercentage" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda timd: int(
            utils.convertFirebaseBoolean(timd.didChallengeTele))),
        "avgGroundIntakes" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda
            timd: timd.numGroundIntakesTele),  # Checked
        "avgBallsKnockedOffMidlineAuto" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda
            timd: timd.numBallsKnockedOffMidlineAuto),  # Checked
        "avgShotsBlocked" : lambda team: calc.getAverageForDataFunctionForTeam(team,
                                                                  lambda timd: timd.numShotsBlockedTele),  # Checked
        "avgHighShotsTele" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda
            timd: timd.numHighShotsMadeTele),  # Checked
        "avgLowShotsTele" : lambda team: calc.getAverageForDataFunctionForTeam(team,
                                                                  lambda timd: timd.numLowShotsMadeTele),  # Checked
        "highShotAccuracyTele" : lambda team: calc.getAverageForDataFunctionForTeam(team, 
                                lambda timd: calc.TIMDShotAccuracy(timd.numHighShotsMadeTele, timd.numHighShotsMissedTele)),                          # Checked
        "lowShotAccuracyTele" : lambda team: calc.getAverageForDataFunctionForTeam(team, 
                                lambda timd: calc.TIMDShotAccuracy(timd.numLowShotsMadeTele, timd.numLowShotsMissedTele)),
        "teleopShotAbility" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda timd: timd.calculatedData.teleopShotAbility),  # Checked
        "siegeConsistency" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda timd: utils.convertFirebaseBoolean(timd.didChallengeTele) or utils.convertFirebaseBoolean(timd.didScaleTele)),  # Checked
        "siegeAbility" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda timd: timd.calculatedData.siegeAbility),  # Checked

        "sdHighShotsTele" : lambda team: calc.getStandardDeviationForDataFunctionForTeam(team, lambda
            timd: timd.numHighShotsMadeTele),  # Checked
        "sdLowShotsTele" : lambda team: calc.getStandardDeviationForDataFunctionForTeam(team, lambda
            timd: timd.numLowShotsMadeTele),  # Checked
        "sdGroundIntakes" : lambda team: calc.getStandardDeviationForDataFunctionForTeam(team, lambda
            timd: timd.numGroundIntakesTele),  # Checked
        "sdShotsBlocked" : lambda team: calc.getStandardDeviationForDataFunctionForTeam(team, lambda
            timd: timd.numShotsBlockedTele),  # Checked
        "sdTeleopShotAbility" : lambda team: calc.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.calculatedData.teleopShotAbility),
        "sdSiegeAbility" : lambda team: calc.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.calculatedData.siegeAbility),
        "sdAutoAbility" : lambda team: calc.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.calculatedData.autoAbility),
        "numScaleAndChallengePoints" : lambda team: calc.numScaleAndChallengePointsForTeam(team),  # Checked
        "breachPercentage" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda timd: 
            utils.convertFirebaseBoolean(lambda team: calc.teamDidBreachInMatch(team, lambda team: calc.su.getMatchForNumber(timd.matchNumber)))),
        "avgHighShotsAttemptedTele" : lambda team: calc.getAverageForDataFunctionForTeam(team,
            lambda timd: timd.calculatedData.highShotsAttemptedTele),
        "avgLowShotsAttemptedTele" : lambda team: calc.getAverageForDataFunctionForTeam(team,
            lambda timd: timd.calculatedData.lowShotsAttemptedTele),
        "twoBallAutoTriedPercentage" : lambda team: calc.twoBallAutoTriedPercentage(team),
        "twoBallAutoAccuracy" : lambda team: calc.twoBallAutoAccuracy(team),

        "avgNumTimesBeached" : lambda team: calc.categoryAAverageDictForDataFunction(team, lambda timd: timd.numTimesBeached),
        "avgNumTimesSlowed" : { "pc" : lambda team: calc.avgNumTimesSlowed(team, "pc"), "cdf" : lambda team: calc.avgNumTimesSlowed(team, "cdf") },
        "avgNumTimesUnaffected" : lambda team: calc.categoryAAverageDictForDataFunction(team, lambda timd: timd.numTimesUnaffected),
        
        "beachedPercentage" : lambda team: utils.dictQuotient(team.calculatedData.avgNumTimesBeached, sumCategoryADataPointDict(team)),
        
        "slowedPercentage" : lambda team: utils.dictQuotient(team.calculatedData.avgNumTimesSlowed, sumCategoryADataPointDict(team)),
        "unaffectedPercentage" : lambda team: utils.dictQuotient(team.calculatedData.avgNumTimesUnaffected, sumCategoryADataPointDict(team)),
        "avgNumTimesCrossedDefensesAuto" : lambda team: calc.getAverageForDataFunctionForTeam(team, lambda tm: tm.calculatedData.totalNumTimesCrossedDefensesAuto),
        "defenses" : [
            lambda team: calc.setDefenseValuesForTeam(team, team.calculatedData.avgSuccessfulTimesCrossedDefensesTele, lambda tm: tm.timesSuccessfulCrossedDefensesTele, 
                lambda x: np.mean(x) if x!= None and len(x) > 0 else 0, lambda y: len(y) if y != None else 0),
            lambda team: calc.setDefenseValuesForTeam(team, team.calculatedData.avgSuccessfulTimesCrossedDefensesAuto, lambda tm: tm.timesSuccessfulCrossedDefensesAuto, 
                lambda x: np.mean(x) if x!= None and len(x) > 0 else 0, lambda y: len(y) if y != None else 0),
            lambda team: calc.setDefenseValuesForTeam(team, team.calculatedData.avgFailedTimesCrossedDefensesTele, lambda tm: tm.timesFailedCrossedDefensesTele, 
                lambda x: np.mean(x) if x!= None and len(x) > 0 else 0, lambda y: len(y) if y != None else 0),
            lambda team: calc.setDefenseValuesForTeam(team, team.calculatedData.avgFailedTimesCrossedDefensesAuto, lambda tm: tm.timesFailedCrossedDefensesAuto, 
                lambda x: np.mean(x) if x!= None and len(x) > 0 else 0, lambda y: len(y) if y != None else 0),
            lambda team: calc.setDefenseValuesForTeam(team, team.calculatedData.avgTimeForDefenseCrossTele, lambda tm: tm.timesSuccessfulCrossedDefensesTele, 
                lambda x: np.mean(x) if x!= None and len(x) > 0 else 0, lambda y: np.mean(y) if y != None and len(y) > 0 else 0),
            lambda team: calc.setDefenseValuesForTeam(team, team.calculatedData.avgTimeForDefenseCrossAuto, lambda tm: tm.timesSuccessfulCrossedDefensesAuto, 
                lambda x: np.mean(x) if x!= None and len(x) > 0 else 0, lambda y: np.mean(y) if y != None and len(y) > 0 else 0),
            lambda team: calc.setDefenseValuesForTeam(team, team.calculatedData.sdSuccessfulDefenseCrossesAuto, lambda tm: tm.timesSuccessfulCrossedDefensesAuto,
                lambda x: utils.rms(x) if x != None and len(x) > 0 else 0, lambda y: len(y) if y != None else 0),
            lambda team: calc.setDefenseValuesForTeam(team, team.calculatedData.sdSuccessfulDefenseCrossesTele, lambda tm: tm.ti,mesSuccessfulCrossedDefensesTele,
                lambda x: utils.rms(x) if x != None and len(x) > 0 else 0, lambda y: len(y) if y != None else 0),
            lambda team: calc.setDefenseValuesForTeam(team, team.calculatedData.sdFailedDefenseCrossesAuto, lambda tm: tm.timesFailedCrossedDefensesAuto,
                lambda x: utils.rms(x) if x != None and len(x) > 0 else 0, lambda y: len(y) if y != None else 0),
            lambda team: calc.setDefenseValuesForTeam(team, team.calculatedData.sdFailedDefenseCrossesTele, lambda tm: tm.timesFailedCrossedDefensesTele,
                lambda x: utils.rms(x) if x != None and len(x) > 0 else 0, lambda y: len(y) if y != None else 0)
        ]


            }

def getMatchCalcDataKeys(calc):
	return {
	    "blueBreachChance" : lambda match: calc.breachChanceForAllianceNumbers(match.blueAllianceTeamNumbers),
        "redBreachChance" : lambda match: calc.breachChanceForAllianceNumbers(match.redAllianceTeamNumbers),
        "blueCaptureChance" : lambda match: calc.captureChanceForAllianceNumbers(match.blueAllianceTeamNumbers),
        "redCaptureChance" : lambda match: calc.captureChanceForAllianceNumbers(match.redAllianceTeamNumbers),
        "predictedBlueScore" : lambda match: calc.predictedScoreForAllianceWithNumbers(match.blueAllianceTeamNumbers),
        "predictedRedScore" : lambda match: calc.predictedScoreForAllianceWithNumbers(match.redAllianceTeamNumbers),
        "sdPredictedBlueScore" : lambda match: calc.stdDevPredictedScoreForAllianceNumbers(match.blueAllianceTeamNumbers),
        "sdPredictedRedScore" : lambda match: calc.stdDevPredictedScoreForAllianceNumbers(match.redAllianceTeamNumbers),
        "blueWinChance" : lambda match: calc.winChanceForMatchForAllianceIsRed(match, False),
        "redWinChance" : lambda match: calc.winChanceForMatchForAllianceIsRed(match, True),
        "predictedBlueRPs" : lambda match: calc.predictedRPsForAllianceForMatch(False, match),
        "predictedRedRPs" : lambda match: calc.predictedRPsForAllianceForMatch(True, match)
        }


