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
	def __init__(self):
		super(CalculatedTeamData, self).__init__()
		self.driverAbility = -1

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

class Match(object):
	"""An FRC Match Object"""
	def __init__(self, **args):
		super(Match, self).__init__()
		self.number = -1
		self.redAllianceTeamNumbers = []
		self.blueAllianceTeamNumbers = []
		self.redScore = -1
		self.blueScore = -1
		self.redDefensePositions = [-1, -1, -1, -1]
		self.blueDefensePositions = [-1, -1, -1, -1]

		self.__dict__.update(args)
		
class TeamInMatchData(object):
	"""An FRC TeamInMatchData Object"""
	def __init__(self, **args):
		super(TeamInMatchData, self).__init__()
		self.teamNumber = -1
		self.matchNumber = -1

		self.didGetIncapacitated = False
		self.didGetDisabled = False

		self.rankCrossingEffeciveness = [-1, -1, -1, -1]
		self.rankTorque = -1
		self.rankSpeed = -1
		self.rankEvasion = -1
		self.rankDefense = -1
		self.rankBallControl = -1

		#Auto
		self.numBallsIntakenAuto = -1
		self.numBallsKnockedOffMidlineAuto = -1
		self.timesDefensesCrossedAuto = [-1, -1, -1, -1]
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
		self.timesDefensesCrossedTele = [-1, -1, -1, -1]
		

		self.__dict__.update(args)		

