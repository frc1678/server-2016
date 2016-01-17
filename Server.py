# by Bryton Moeller (2015-2016)

import json
import sys

#Our Modules
import DataModel
import utils
import firebaseCommunicator
import Math
import unicodedata

a = ['frc3333', 'frc343434343', 'frc6']
ar = []
for s in a:
	s = s.replace('frc', '')
	ar.append(s)

print ar


comp = DataModel.Competition()
comp.updateTeamsAndMatchesFromFirebase()
comp.updateTIMDsFromFirebase()

calculator = Math.Calculator(comp)
calculator.averageTIMDObjectOverMatches(254, 'rankTorque', 1)

''' # DEBUG
teams = []
for i in teams:
	updateFirebaseWithTeam(makeTeamObjectWithNumberAndName(i, "none"))
'''