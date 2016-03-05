class CachedTeamData(object):
	def __init__(self, teamNumber):
		super(CachedTeamData, self).__init__()
		self.number = teamNumber
		self.alphas = {}
		self.defensesFaced = []

class CachedCompetitionData(object):
	def __init__(self):
		super(CachedCompetitionData, self).__init__()
		self.defenseSightings = None