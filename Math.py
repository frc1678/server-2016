# Math.py
import utils

class Calculator(object):
	"""docstring for Calculator"""
	def __init__(self, competition):
		super(Calculator, self).__init__()
		self.comp = competition
		
	def getTeamForNumber(self, num):
		for team in self.comp.teams:
			if team.number == num:
				return team

	def getMatchForNumber(self, num):
		for match in self.comp.matches:
			if match.number == num:
				return match

	def getTIMDsForTeamNumber(self, num):
		timds = []
		for timd in self.comp.TIMDs:
			if timd.teamNumber == num:
				timds.append(timd)
		return timds

	# Calculated Team Data
	def averageTIMDObjectOverMatches(self, teamNumber, key, coefficient):
		timds = self.getTIMDsForTeamNumber(teamNumber)
		total = 0.0
		for timd in timds:
			print utils.makeDictFromTIMD(timd)[key]


