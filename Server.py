# by Bryton Moeller (2015-2016)

import json
import sys

#Our Modules
import DataModel
import utils
import firebaseCommunicator
import Math
import unicodedata
import time



comp = DataModel.Competition()
comp.updateTeamsAndMatchesFromFirebase()
comp.updateTIMDsFromFirebase()

FBC = firebaseCommunicator.FirebaseCommunicator(comp)

calculator = Math.Calculator(comp)

while(1):
	calculator.doCalculations(FBC)
	time.sleep(10)
	print("Calcs...")


''' # DEBUG
teams = []
for i in teams:
	updateFirebaseWithTeam(makeTeamObjectWithNumberAndName(i, "none"))
'''