import Math
import DataModel
import utils
import numpy as np
import prepFirebaseForCompetition
import CacheModel as cache
import pdb

# Scout Performance Analysis
class ScoutPerformance(object):
	"""docstring for ScoutPerformance"""
	def __init__(self, comp):
		super(ScoutPerformance, self).__init__()
		self.comp = comp
		self.calculator = Math.Calculator(comp)
		self.correctionalMatches = {}

	