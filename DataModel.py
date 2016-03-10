import firebaseCommunicator
import utils
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
		# if doneCallback == None: return 
		# while 1: 
		# 	if len(self.teams) > 0 and len(self.matches) > 0: doneCallback()

	def updateTIMDsFromFirebase(self):
		self.TIMDs = utils.makeTIMDsFromDicts(firebaseCommunicator.getPythonObjectForFirebaseDataAtLocation("/TeamInMatchDatas"))

class CalculatedTeamData(object):
	"""The calculatedData for an FRC Team object"""
	def __init__(self, **args):
		super(CalculatedTeamData, self).__init__()
		self.secondPickAbility = {
		}
		self.avgSuccessfulTimesCrossedDefenses = {
			'pc' : None,
			'cdf' : None,
			'mt' : None,
			'rp' : None,
			'sp' : None,
			'db' : None,
			'rt' : None,
			'rw' : None,
			'lb' : None
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
		self.avgDrivingAbility = None
		self.blockingAbility = None
		self.disfunctionalPercentage = None
		self.reachPercentage = None
		self.disabledPercentage = None
		self.incapacitatedPercentage = None
		self.scalePercentage = None
		self.challengePercentage = None
		self.breachPercentage = None
		self.teleopShotAbility = None
		self.avgSuccessfulTimesCrossedDefensesAuto = { #Works
		  	'pc' : None,
			'cdf' : None,
			'mt' : None,
			'rp' : None,
			'sp' : None,
			'db' : None,
			'rt' : None,
			'rw' : None,
			'lb' : None
		}
		self.avgSuccessfulTimesCrossedDefensesTele = { #Works
		  	'pc' : None,
			'cdf' : None,
			'mt' : None,
			'rp' : None,
			'sp' : None,
			'db' : None,
			'rt' : None,
			'rw' : None,
			'lb' : None
		}
		self.avgFailedTimesCrossedDefensesAuto = {
		 	'pc' : None,
			'cdf' : None,
			'mt' : None,
			'rp' : None,
			'sp' : None,
			'db' : None,
			'rt' : None,
			'rw' : None,
			'lb' : None
		}
		self.avgFailedTimesCrossedDefensesTele = {
		 	'pc' : None,
			'cdf' : None,
			'mt' : None,
			'rp' : None,
			'sp' : None,
			'db' : None,
			'rt' : None,
			'rw' : None,
			'lb' : None
		}
		self.avgTimeForDefenseCrossAuto = {
			'pc' : None,
			'cdf' : None,
			'mt' : None,
			'rp' : None,
			'sp' : None,
			'db' : None,
			'rt' : None,
			'rw' : None,
			'lb' : None
		}
		self.avgTimeForDefenseCrossTele = {
			'pc' : None,
			'cdf' : None,
			'mt' : None,
			'rp' : None,
			'sp' : None,
			'db' : None,
			'rt' : None,
			'rw' : None,
			'lb' : None
		}
		self.predictedSuccessfulCrossingsForDefenseTele = {
			'pc' : None,
			'cdf' : None,
			'mt' : None,
			'rp' : None,
			'sp' : None,
			'db' : None,
			'rt' : None,
			'rw' : None,
			'lb' : None
		}
		self.siegeConsistency = None
		self.siegeAbility = None
		self.autoAbility = None
		self.predictedNumRPs = None
		self.numRPs = None
		self.numAutoPoints = None
		self.numScaleAndChallengePoints = None
		self.sdHighShotsAuto = None
		self.sdHighShotsTele = None
		self.sdLowShotsAuto = None
		self.sdSiegeAbility = None
		self.sdLowShotsTele = None
		self.sdGroundIntakes = None
		self.sdTeleopShotAbility = None
		self.sdAutoAbility = None
		self.sdShotsBlocked = None
		self.sdMidlineBallsIntakedAuto = None
		self.sdBallsKnockedOffMidlineAuto = None
		self.sdSuccessfulDefenseCrossesAuto = {
			'pc' : None,
			'cdf' : None,
			'mt' : None,
			'rp' : None,
			'sp' : None,
			'db' : None,
			'rt' : None,
			'rw' : None,
			'lb' : None		}
		self.sdSuccessfulDefenseCrossesTele = {
			'pc' : None,
			'cdf' : None,
			'mt' : None,
			'rp' : None,
			'sp' : None,
			'db' : None,
			'rt' : None,
			'rw' : None,
			'lb' : None
		}
		self.sdFailedDefenseCrossesAuto = {
			'pc' : None,
			'cdf' : None,
			'mt' : None,
			'rp' : None,
			'sp' : None,
			'db' : None,
			'rt' : None,
			'rw' : None,
			'lb' : None
		}
		self.sdFailedDefenseCrossesTele = {
			'pc' : None,
			'cdf' : None,
			'mt' : None,
			'rp' : None,
			'sp' : None,
			'db' : None,
			'rt' : None,
			'rw' : None,
			'lb' : None
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
		self.selectedImageUrl = None
		self.otherImageUrls = {
			 'not0' : None
		}
		self.pitHeightOfBallLeavingShooter = None
		self.pitLowBarCapability = None
		self.pitPotentialLowBarCapability = None
		#self.pitPotentialCDFAndPCCapability = None
		self.pitPotentialMidlineBallCapability = None
		#self.pitFrontBumperWidth = None
		self.pitDriveBaseWidth = None
		self.pitDriveBaseLength = None
		self.pitBumperHeight = None
		self.pitPotentialShotBlockerCapability = None
		self.pitNotes = None
		self.pitOrganization = None
		self.pitNumberOfWheels = None
		#self.pitHeightOfRobot = None
		self.__dict__.update(args)


class CalculatedMatchData(object):
	"""docstring for CalculatedMatchData"""
	def __init__(self, **args):
		super(CalculatedMatchData, self).__init__()
		self.predictedRedScore = None
		self.predictedBlueScore = None
		self.sdPredictedRedScore = None
		self.sdPredictedBlueScore = None

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
		self.ballsIntakedAuto = []
		self.numBallsKnockedOffMidlineAuto = None

		self.timesSuccessfulCrossedDefensesAuto = {
			'pc' : None,
			'cdf' : None,
			'mt' : None,
			'rp' : None,
			'sp' : None,
			'db' : None,
			'rt' : None,
			'rw' : None,
			'lb' : None
		}

		self.timesFailedCrossedDefensesAuto = {
			'pc' : None,
			'cdf' : None,
			'mt' : None,
			'rp' : None,
			'sp' : None,
			'db' : None,
			'rt' : None,
			'rw' : None,
			'lb' : None
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

		self.timesSuccessfulCrossedDefensesTele = {
			'pc' : None,
			'cdf' : None,
			'mt' : None,
			'rp' : None,
			'sp' : None,
			'db' : None,
			'rt' : None,
			'rw' : None,
			'lb' : None
		}

		self.timesFailedCrossedDefensesTele = {
			'pc' : None,
			'cdf' : None,
			'mt' : None,
			'rp' : None,
			'sp' : None,
			'db' : None,
			'rt' : None,
			'rw' : None,
			'lb' : None
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
		self.teleopShotAbility = None
		self.siegeAbility = None#
		self.autoAbility = None
		self.siegeConsistency = None#
		self.numRPs = None#
		self.drivingAbility = None#
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
		}
		# self.numTimesSuccesfulCrossedDefensesTele = {
		# 	'pc' : None,
		# 	'cdf' : None,
		# 	'mt' : None,
		# 	'rp' : None,
		# 	'sp' : None,
		# 	'db' : None,
		# 	'rt' : None,
		# 	'rw' : None,
		# 	'lb' : None
		# }
		# self.numTimesSuccessfulCrossedDefensesAuto = {
		# 	'pc' : None,
		# 	'cdf' : None,
		# 	'mt' : None,
		# 	'rp' : None,
		# 	'sp' : None,
		# 	'db' : None,
		# 	'rt' : None,
		# 	'rw' : None,
		# 	'lb' : None
		# }
		# self.numTimesFailedCrossedDefensesTele = {
		# 	'pc' : None,
		# 	'cdf' : None,
		# 	'mt' : None,
		# 	'rp' : None,
		# 	'sp' : None,
		# 	'db' : None,
		# 	'rt' : None,
		# 	'rw' : None,
		# 	'lb' : None
		# }
		# self.numTimesFailedCrossedDefensesAuto = {
		# 	'pc' : None,
		# 	'cdf' : None,
		# 	'mt' : None,
		# 	'rp' : None,
		# 	'sp' : None,
		# 	'db' : None,
		# 	'rt' : None,
		# 	'rw' : None,
		# 	'lb' : None
		# }
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
