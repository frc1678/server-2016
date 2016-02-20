import firebaseCommunicator
import utils
import random
import Math
# Classes That Reflect Firebase Data Structure

class Competition(object):
	"""docstring for Competition"""
	def __init__(self):
		super(Competition, self).__init__()
		self.code = ""
		self.teams = TeamList([])
		self.matches = []
		self.TIMDs = []
		self.averageScore = None
		self.predictedSeeding = []
		self.actualSeeding = []
		self.sdRScores = []
	def updateTeamsAndMatchesFromFirebase(self):
		self.teams = utils.makeTeamsFromDicts(firebaseCommunicator.getPythonObjectForFirebaseDataAtLocation("/Teams"))
		self.matches = utils.makeMatchesFromDicts(firebaseCommunicator.getPythonObjectForFirebaseDataAtLocation("/Matches"))
	def updateTIMDsFromFirebase(self):
		self.TIMDs = utils.makeTIMDsFromDicts(firebaseCommunicator.getPythonObjectForFirebaseDataAtLocation("/TeamInMatchDatas"))

class CalculatedTeamData(object):
	"""The calculatedData for an FRC Team object"""
	def __init__(self, **args):
		super(CalculatedTeamData, self).__init__()
		self.secondPickAbility = {
			None : None
		}
		self.avgSuccessfulTimesCrossedDefenses = {
			'a' : {'pc' : None, 'cdf' : None},
			'b' : {'mt' : None, 'rp' : None},
			'c' : {'db' : None, 'sp' : None},
			'd' : {'rw' : None, 'rt' : None},
			'e' : {'lb' : None}
		}
		self.firstPickAbility = None
		self.overallSecondPickAbility = None
		self.citrusDPR = None
		self.highShotAccuracyAuto = None #Works
		self.lowShotAccuracyAuto = None #Works
		self.highShotAccuracyTele = None #Works
		self.lowShotAccuracyTele = None #Works
		self.avgGroundIntakes = None #Works
		self.avgHighShotsTele = None #Works
		self.avgLowShotsTele = None #Works
		self.avgShotsBlocked = None #Works
		self.avgHighShotsAuto = None #Works
		self.avgLowShotsAuto = None #Works
		self.avgMidlineBallsIntakedAuto = None #Works
		self.avgBallsKnockedOffMidlineAuto = None #Works
		self.avgTorque = None
		self.avgSpeed = None
		self.avgEvasion = None
		self.avgDefense = None
		self.avgBallControl = None
		self.blockingAbility = None
		self.disfunctionalPercentage = None
		self.reachPercentage = None
		self.disabledPercentage = None
		self.incapacitatedPercentage = None
		self.scalePercentage = None
		self.challengePercentage = None
		self.breachPercentage = None
		self.avgSuccessfulTimesCrossedDefensesAuto = { #Works
		  	'a' : {'pc' : None, 'cdf' : None},
			'b' : {'mt' : None, 'rp' : None},
			'c' : {'db' : None, 'sp' : None},
			'd' : {'rw' : None, 'rt' : None},
			'e' : {'lb' : None}
		}
		self.avgSuccessfulTimesCrossedDefensesTele = { #Works
		  	'a' : {'pc' : None, 'cdf' : None},
			'b' : {'mt' : None, 'rp' : None},
			'c' : {'db' : None, 'sp' : None},
			'd' : {'rw' : None, 'rt' : None},
			'e' : {'lb' : None}
		}
		self.avgFailedTimesCrossedDefensesAuto = {
		 	'a' : {'pc' : None, 'cdf' : None},
			'b' : {'mt' : None, 'rp' : None},
			'c' : {'db' : None, 'sp' : None},
			'd' : {'rw' : None, 'rt' : None},
			'e' : {'lb' : None}
		}
		self.avgFailedTimesCrossedDefensesTele = {
		 	'a' : {'pc' : None, 'cdf' : None},
			'b' : {'mt' : None, 'rp' : None},
			'c' : {'db' : None, 'sp' : None},
			'd' : {'rw' : None, 'rt' : None},
			'e' : {'lb' : None}
		}
		self.siegePower = None
		self.siegeConsistency = None
		self.siegeAbility = None
		self.predictedNumRPs = None
		self.numRPs = None
		self.numAutoPoints = None
		self.numScaleAndChallengePoints = None
		self.rankingAutoPoints = None
		self.rankingSiegePoints = None
		self.sdHighShotsAuto = None
		self.sdHighShotsTele = None
		self.sdLowShotsAuto = None
		self.sdLowShotsTele = None
		self.sdGroundIntakes = None
		self.sdShotsBlocked = None
		self.sdMidlineBallsIntakedAuto = None
		self.sdBallsKnockedOffMidlineAuto = None
		self.sdSuccessfulDefenseCrossesAuto = {
			'a' : {'pc' : None, 'cdf' : None},
			'b' : {'mt' : None, 'rp' : None},
			'c' : {'db' : None, 'sp' : None},
			'd' : {'rw' : None, 'rt' : None},
			'e' : {'lb' : None}
		}
		self.sdSuccessfulDefenseCrossesTele = {
			'a' : {'pc' : None, 'cdf' : None},
			'b' : {'mt' : None, 'rp' : None},
			'c' : {'db' : None, 'sp' : None},
			'd' : {'rw' : None, 'rt' : None},
			'e' : {'lb' : None}
		}
		self.sdFailedDefenseCrossesAuto = {
			'a' : {'pc' : None, 'cdf' : None},
			'b' : {'mt' : None, 'rp' : None},
			'c' : {'db' : None, 'sp' : None},
			'd' : {'rw' : None, 'rt' : None},
			'e' : {'lb' : None}
		}
		self.sdFailedDefenseCrossesTele = {
			'a' : {'pc' : None, 'cdf' : None},
			'b' : {'mt' : None, 'rp' : None},
			'c' : {'db' : None, 'sp' : None},
			'd' : {'rw' : None, 'rt' : None},
			'e' : {'lb' : None}
		}
		self.RScoreTorque = None
		self.RScoreSpeed = None
		self.RScoreEvasion = None		
		self.RScoreDefense = None
		self.RScoreBallControl = None
		self.RScoreDrivingAbility = None
		self.predictedSeed = None
		self.actualSeed = None
		self.__dict__.update(args)

		

class Team(object):
	"""An FRC Team object"""
	def __init__(self, **args):
		super(Team, self).__init__()
		self.name = None
		self.number = None
		self.teamInMatchDatas = None
		self.calculatedData = CalculatedTeamData()
		self.selectedImageUrl = '-1'
		self.otherImageUrls = {
			 'not0' : '-1'
		}
		self.pitHeightOfBallLeavingShooter = -1.0
		self.pitLowBarCapability = -1
		self.pitPotentialLowBarCapability = -1
		#self.pitPotentialCDFAndPCCapability = None
		self.pitPotentialMidlineBallCapability = -1
		#self.pitFrontBumperWidth = None
		self.pitDriveBaseWidth = -1.0
		self.pitDriveBaseLength = -1.0
		self.pitBumperHeight = -1.0
		self.pitPotentialShotBlockerCapability = -1
		self.pitNotes = '-1'
		self.pitOrganization = -1
		self.pitNumberOfWheels = -1
		#self.pitHeightOfRobot = None
		self.__dict__.update(args)


class CalculatedMatchData(object):
	"""docstring for CalculatedMatchData"""
	def __init__(self, **args):
		super(CalculatedMatchData, self).__init__()
		self.predictedRedScore = None
		self.predictedBlueScore = None	

		self.numDefensesCrossedByBlue = None
		self.numDefensesCrossedByRed = None 
		self.redScoresForDefenses = {None : None}
		self.redWinningChanceForDefenses = {None : None}
		self.redBreachChanceForDefenses = {None : None}
		self.redRPsForDefenses = {None : None}
		self.blueScoresForDefenses = {None : None}
		self.blueWinningChanceForDefenses = {None : None}
		self.blueBreachChanceForDefenses = {None : None}
		self.blueRPsForDefenses = {None: None}
		self.redWinChance = None
		self.redBreachChance = None
		self.redCaptureChance = None
		self.blueWinChance = None
		self.blueBreachChance = None
		self.blueCaptureChance = None
		self.predictedBlueRPs = None
		self.actualBlueRPs = None
		self.predictedRedRPs = None
		self.actualRedRPs = None	
		self.redAllianceDidBreach = None
		self.blueAllianceDidBreach = None
		self.optimalRedDefenses = None
		self.optimalBlueDefenses = None

		self.__dict__.update(args)


class Match(object):
	"""An FRC Match Object"""
	def __init__(self, **args):
		super(Match, self).__init__()
		self.number = None
		self.calculatedData = CalculatedMatchData()
		self.redAllianceTeamNumbers = None
		self.blueAllianceTeamNumbers = None
		self.redScore = None
		self.blueScore = None
		self.redDefensePositions = None
		self.blueDefensePositions = None
		self.redAllianceDidCapture = None
		self.blueAllianceDidCapture = None
		self.blueAllianceDidBreach = None
		self.redAllianceDidBreach = None
		self.TIMDs = []
		self.__dict__.update(args)
		
class TeamInMatchData(object):
	"""An FRC TeamInMatchData Object"""
	def __init__(self, **args):
		super(TeamInMatchData, self).__init__()
		
		self.calculatedData = CalculatedTeamInMatchData()
		self.teamNumber = None
		self.matchNumber = None
		self.scoutName = None

		self.didGetIncapacitated = None
		self.didGetDisabled = None
		self.rankTorque = None
		self.rankSpeed = None
		self.rankEvasion = None
		self.rankDefense = None
		self.rankBallControl = None

		#Auto
		self.ballsIntakedAuto = None
		self.numBallsKnockedOffMidlineAuto = None
		# self.timesCrossedDefensesAuto = {
		# 	'a' : {'pc' : {'successes' : None, 'fails' : None}, 'cdf' : {'successes' : None, 'fails' : None}},
		# 	'b' : {'mt' : {'successes' : None, 'fails' : None}, 'rp' : {'successes' : None, 'fails' : None}},
		# 	'c' : {'db' : {'successes' : None, 'fails' : None}, 'sp' : {'successes' : None, 'fails' : None}},
		# 	'd' : {'rw' : {'successes' : None, 'fails' : None}, 'rt' : {'successes' : None, 'fails' : None}},
		# 	'e' : {'lb' : {'successes' : None, 'fails' : None}}
		# }

		self.timesSuccessfulCrossedDefensesAuto = {
			'a' : {'pc' : None, 'cdf' : None},
			'b' : {'mt' : None, 'rp' : None},
			'c' : {'db' : None, 'sp' : None},
			'd' : {'rw' : None, 'rt' : None},
			'e' : {'lb' : None}
		}

		self.timesFailedCrossedDefensesAuto = {
			'a' : {'pc' : None, 'cdf' : None},
			'b' : {'mt' : None, 'rp' : None},
			'c' : {'db' : None, 'sp' : None},
			'd' : {'rw' : None, 'rt' : None},
			'e' : {'lb' : None}
		}

		self.numHighShotsMadeAuto = None
		self.numLowShotsMadeAuto = None
		self.numHighShotsMissedAuto = None
		self.numLowShotsMissedAuto = None
		self.didReachAuto = None

		#Tele
		self.numHighShotsMadeTele = None
		self.numLowShotsMadeTele = None
		self.numHighShotsMissedTele = None
		self.numLowShotsMissedTele = None
		self.numGroundIntakesTele = None
		self.numShotsBlockedTele = None
		self.didScaleTele = None
		self.didChallengeTele = None
		# self.timesCrossedDefensesTele = {
	 # 		'a' : {'pc' : {'successes' : None, 'fails' : None}, 'cdf' : {'successes' : None, 'fails' : None}},
	 # 		'b' : {'mt' : {'successes' : None, 'fails' : None}, 'rp' : {'successes' : None, 'fails' : None}},
	 # 		'c' : {'db' : {'successes' : None, 'fails' : None}, 'sp' : {'successes' : None, 'fails' : None}},
	 # 		'd' : {'rw' : {'successes' : None, 'fails' : None}, 'rt' : {'successes' : None, 'fails' : None}},
		# 	'e' : {'lb' : {'successes' : None, 'fails' : None}}
		#  }

		self.timesSuccessfulCrossedDefensesTele = {
			'a' : {'pc' : None, 'cdf' : None},
			'b' : {'mt' : None, 'rp' : None},
			'c' : {'db' : None, 'sp' : None},
			'd' : {'rw' : None, 'rt' : None},
			'e' : {'lb' : None}
		}

		self.timesFailedCrossedDefensesTele = {
			'a' : {'pc' : None, 'cdf' : None},
			'b' : {'mt' : None, 'rp' : None},
			'c' : {'db' : None, 'sp' : None},
			'd' : {'rw' : None, 'rt' : None},
			'e' : {'lb' : None}
		}
		self.superNotes = None

		self.__dict__.update(args)		

class CalculatedTeamInMatchData(object):
	"""docstring for CalculatedTeamInMatchData"""
	def __init__(self, **args):
		super(CalculatedTeamInMatchData, self).__init__()
		self.highShotAccuracyAuto = None #
		self.lowShotAccuracyAuto = None #
		self.highShotAccuracyTele = None #
		self.lowShotAccuracyTele = None #
		self.siegeAbility = None#
		self.siegeConsistency = None#
		self.numRPs = None#
		self.numAutoPoints = None#
		self.numScaleAndChallengePoints = None#
		self.numBallsIntakedOffMidlineAuto = None
		self.RScoreTorque = None
		self.RScoreSpeed = None
		self.RScoreEvasion = None		
		self.RScoreDefense = None
		self.RScoreBallControl = None
		self.RScoreDrivingAbility = None
		self.citrusDPR = None 
		self.firstPickAbility = None
		self.secondPickAbility = {
			None: None
		}
		self.overallSecondPickAbility = None
		self.scoreContribution = None #

		self.__dict__.update(args)

#Making Fake Type safety is very much NOT A PYTHON PRACTICE, but may be needed. 
class TeamList(list):
    def __init__(self, iterable=None):
        """Override initializer which can accept iterable"""
        super(TeamList, self).__init__()
        if iterable:
            for item in iterable:
                self.append(item)

    def append(self, item):
        if isinstance(item, Team):
            super(TeamList, self).append(item)
        else:
            raise ValueError('Teams allowed only')

    def insert(self, index, item):
        if isinstance(item, Team):
            super(TeamList, self).insert(index, item)
        else:
            raise ValueError('Teams allowed only')

    def __add__(self, item):
        if isinstance(item, Team):
            super(TeamList, self).__add__(item)
        else:
            raise ValueError('Teams allowed only')

    def __iadd__(self, item):
        if isinstance(item, Team):
            super(TeamList, self).__iadd__(item)
        else:
            raise ValueError('Teams allowed only')
