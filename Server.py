# by Bryton Moeller (2015-2016)

import json
import sys

#Our Modules
import DataModel
import utils
import firebaseCommunicator
import Math
import unicodedata



comp = DataModel.Competition()
comp.updateTeamsAndMatchesFromFirebase()
comp.updateTIMDsFromFirebase()

calculator = Math.Calculator(comp)
calculator.doCalculations()

''' # DEBUG
teams = []
for i in teams:
	updateFirebaseWithTeam(makeTeamObjectWithNumberAndName(i, "none"))
'''