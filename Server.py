				if isinstance(team.calculatedData, {}.__class__): team.calculatedData = DataModel.CalculatedTeamData(**team.calculatedData) #We shouldnt have to do this here, it should already be done. Don't have time to figure out why right now.
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
import DataValidator


comp = DataModel.Competition()
comp.updateTeamsAndMatchesFromFirebase()
comp.updateTIMDsFromFirebase()
dv = DataValidator.DataValidator(comp)

FBC = firebaseCommunicator.FirebaseCommunicator(comp)

calculator = Math.Calculator(comp)

while(1):
	calculator.doCalculations(FBC)
	dv.validateFirebase()
	time.sleep(10)
	print("Calcs...")


''' # DEBUG
teams = []
for i in teams:
	updateFirebaseWithTeam(makeTeamObjectWithNumberAndName(i, "none"))
'''