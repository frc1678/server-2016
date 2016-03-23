# by Bryton Moeller (2015-2016)

import json
import sys

#Our Modules
import DataModel
import firebaseCommunicator
import Math
import unicodedata
import time
import DataValidator
import CSVExporter
import pdb

shouldCacheJSONCopies = False

comp = DataModel.Competition()
comp.updateTeamsAndMatchesFromFirebase()
comp.updateTIMDsFromFirebase()

CSVExporter.TSVExport(comp)
dv = DataValidator.DataValidator(comp)

FBC = firebaseCommunicator.FirebaseCommunicator(comp)

calculator = Math.Calculator(comp)

secsBetweenCalc = 0
shouldCacheSecsCounter = 0
cycle = 1

numHoursBetweenCaches = 1.0/360.0

while(1):
	if((shouldCacheSecsCounter / (numHoursBetweenCaches * 3600)) == 1):
		shouldCacheSecsCounter = 0
	if(shouldCacheSecsCounter == 0):
		FBC.cacheFirebase()
	shouldCacheSecsCounter += secsBetweenCalc
	dv.validateFirebase()
	comp.updateTeamsAndMatchesFromFirebase()
	comp.updateTIMDsFromFirebase()
	calculator.doCalculations(FBC)
	time.sleep(secsBetweenCalc)
	cycle += 1
	print("\nCalcs Cycle " + str(cycle) + "...")

# # DEBUG
# teams = []
# for i in teams:
# 	updateFirebaseWithTeam(makeTeamObjectWithNumberAndName(i, "none"))
