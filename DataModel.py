import firebaseCommunicator
import utils
# Classes That Reflect Firebase Data Structure

class Competition(object):
	"""docstring for Competition"""
	def __init__(self):
		super(Competition, self).__init__()
		self.code = ""
		self.teams = []
		self.matches = []
		self.TIMDs = []
	def updateTeamsAndMatchesFromFirebase(self):
		self.teams = utils.makeTeamsFromDicts(firebaseCommunicator.getPythonObjectForFirebaseDataAtLocation("/Teams"))
		self.matches = utils.makeMatchesFromDicts(firebaseCommunicator.getPythonObjectForFirebaseDataAtLocation("/Matches"))
	def updateTIMDsFromFirebase(self):
		self.TIMDs = utils.makeTIMDsFromDicts(firebaseCommunicator.getPythonObjectForFirebaseDataAtLocation("/TeamInMatchDatas"))
		

class CalculatedTeamData(object):
	"""The calculatedData for an FRC Team object"""
	def __init__(self, **args):
		super(CalculatedTeamData, self).__init__()
		self.driverAbility = -1
		self.highShotAccuracyAuto = -1.0
		self.lowShotAccuracyAuto = -1.0
		self.highShotAccuracyTele = -1.0
		self.lowShotAccuracyTele = -1.0
		self.avgGroundIntakes = -1.0
		self.avgHighShotsTele = -1.0
		self.avgLowShotsTele = -1.0
		self.avgShotsBlocked = -1.0
		self.avgHighShotsAuto = -1.0
		self.avgLowShotsAuto = -1.0
		self.avgMidlineBallsIntakedAuto = -1.0
		self.avgBallsKnockedOffMidlineAuto = -1.0
		self.avgTorque = -1.0
		self.avgSpeed = -1.0
		self.avgEvasion = -1.0
		self.avgDefense = -1.0
		self.avgBallControl = -1.0
		self.disfunctionalPercentage = -1.0
		self.reachPercentage = -1.0
		self.disabledPercentage = -1.0
		self.incapacitatedPercentage = -1.0
		self.scalePercentage = -1.0
		self.challengePercentage = -1.0
		self.avgDefenseCrossingEffectiveness = {
		 'pc' : -1, 
			'cdf' : -1, 
			'moat' :  -1,
			'ramparts' : -1,
			'sp' : -1,
			'db' : -1,
			'lb' : -1,
			'rt' : -1,
			'rw' : -1,
		}
		self.avgTimesCrossedDefensesAuto = {
		 	'pc' : -1, 
			'cdf' : -1,
			'moat' :  -1,
			'ramparts' : -1,
			'sp' : -1,
			'db' : -1,
			'lb' : -1,
			'rt' : -1
		}
		self.avgTimesCrossedDefensesTele = {
		 	'pc' : -1, 
			'cdf' : -1,
			'moat' :  -1,
			'ramparts' : -1,
			'sp' : -1,
			'db' : -1,
			'lb' : -1,
			'rt' : -1
		}
		self.siegePower = -1.0
		self.siegeConsistency = -1.0
		self.siegeAbility = -1.0
		self.__dict__.update(args)

		

class Team(object):
	"""An FRC Team object"""
	def __init__(self, **args):
		super(Team, self).__init__()
		self.name = "noName"
		self.number = -1
		self.matches = []
		self.teamInMatchDatas = []
		self.calculatedData = CalculatedTeamData()
		self.__dict__.update(args)

class CalculatedMatchData(object):
	"""docstring for CalculatedMatchData"""
	def __init__(self):
		super(CalculatedMatchData, self).__init__()
		self.predictedRedScore = -1.0
		self.predictedBlueScore = -1.0		

class Match(object):
	"""An FRC Match Object"""
	def __init__(self, **args):
		super(Match, self).__init__()
		self.number = -1
		self.calculatedData = CalculatedMatchData()
		self.redAllianceTeamNumbers = []
		self.blueAllianceTeamNumbers = []
		self.redScore = -1
		self.blueScore = -1
		self.redDefensePositions = ['', '', '', '']
		self.blueDefensePositions = ['', '', '', '']

		self.__dict__.update(args)
		
class TeamInMatchData(object):
	"""An FRC TeamInMatchData Object"""
	def __init__(self, **args):
		super(TeamInMatchData, self).__init__()
		self.teamNumber = -1
		self.matchNumber = -1

		self.didGetIncapacitated = False
		self.didGetDisabled = False

		self.rankDefenseCrossingEffectiveness = {
			'pc' : -1, 
			'cdf' : -1, 
			'moat':  -1,
			'ramparts' : -1,
			'sp' : -1,
			'db' : -1,
			'lb' : -1,
			'rt' : -1,
			'rw' : -1
		}
		self.rankTorque = -1
		self.rankSpeed = -1
		self.rankEvasion = -1
		self.rankDefense = -1
		self.rankBallControl = -1

		#Auto
		self.ballsIntakedAuto = [-1, -1, -1, -1, -1, -1]
		self.numBallsKnockedOffMidlineAuto = -1
		self.timesDefensesCrossedAuto = {
			'pc' : -1, 
			'cdf' : -1, 
			'mt' :  -1,
			'rp' : -1,
			'sp' : -1,
			'db' : -1,
			'lb' : -1,
			'rt' : -1,
			'rw' : -1
		}
		self.numHighShotsMadeAuto = -1
		self.numLowShotsMadeAuto = -1
		self.numHighShotsMissedAuto = -1
		self.numLowShotsMissedAuto = -1
		self.didReachAuto = False

		#Tele
		self.numHighShotsMadeTele = -1
		self.numLowShotsMadeTele = -1
		self.numHighShotsMissedTele = -1
		self.numLowShotsMissedTele = -1
		self.numGroundIntakesTele = -1
		self.numShotsBlockedTele = -1
		self.didScaleTele = False
		self.didChallengeTele = False
		self.timesDefensesCrossedTele = {
			'pc' : -1, 
			'cdf' : -1, 
			'moat' :  -1,
			'ramparts' : -1,
			'sp' : -1,
			'db' : -1,
			'lb' : -1,
			'rw' : -1
		}
		

		self.__dict__.update(args)		

