# Classes That Reflect Firebase Data Structure
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
		self.__dict__.update(args)
		
class TeamInMatchData(object):
	"""An FRC TeamInMatchData Object"""
	def __init__(self, **args):
		super(TeamInMatchData, self).__init__()
		self.teamNumber = -1
		self.matchNumber = -1
		self.__dict__.update(args)		

