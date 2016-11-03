# by Bryton Moeller (2015-2016)

import json
import sys
import traceback

#Our Modules
import DataModel
import firebaseCommunicator
import Math
import unicodedata
import time
import DataValidator
import CSVExporter
import utils
import pdb
import scoutPerformance
import CrashReporter
import numpy as np

shouldCacheJSONCopies = False

comp = DataModel.Competition()
comp.code = 'hop'
print "Competition Code: " + comp.code 
comp.updateTeamsAndMatchesFromFirebase()
comp.updateTIMDsFromFirebase()

CSVExporter.TSVExportCMP(comp)

dv = DataValidator.DataValidator(comp)

FBC = firebaseCommunicator.FirebaseCommunicator(comp)
calculator = Math.Calculator(comp)
secsBetweenCalc = 0
shouldCacheSecsCounter = 0
cycle = 1
shouldEmail = False

numHoursBetweenCaches = 1.0/360.0
emailer = CrashReporter.EmailThread()

scoutCalculator = scoutPerformance.ScoutPerformance(comp, calculator)
scoutCalculator.start()


def checkForMissingData():
	with open('missing_data.txt', 'w') as missingDataFile:
		missingDatas = calculator.getMissingDataString()
		print missingDatas
		missingDataFile.write(str(missingDatas))

while(True):
	print("\nCalcs Cycle " + str(cycle) + "...")
	if((shouldCacheSecsCounter / (numHoursBetweenCaches * 3600)) == 1):
		shouldCacheSecsCounter = 0
	if(shouldCacheSecsCounter == 0):
		FBC.cacheFirebase()
	shouldCacheSecsCounter += secsBetweenCalc
	dv.validateFirebase()

	comp.updateTeamsAndMatchesFromFirebase()
	comp.updateTIMDsFromFirebase()
	# print comp.teams, comp.matches
	checkForMissingData()
	if shouldEmail:
		try:
			calculator.doCalculations(FBC)
		except:
			emailer.reportServerCrash(traceback.format_exc())
			sys.exit(0)
	else: 
		print "calc"
		calculator.doCalculations(FBC)
	time.sleep(secsBetweenCalc)
	cycle += 1