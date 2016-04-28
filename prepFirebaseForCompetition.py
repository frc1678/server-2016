import DataModel
import firebaseCommunicator
import TBACommunicator
import utils
import time

############# Getting TBA Data ###################
 # set to "<your initials>:TBA_communicator:0"

TBAC = TBACommunicator.TBACommunicator()
competition = DataModel.Competition()
competition.eventCode = TBAC.eventCode



def makeFakeDatabase():
	FBC = firebaseCommunicator.FirebaseCommunicator(competition)
	FBC.JSONteams = utils.readJSONFromString(TBAC.makeEventTeamsRequest())
	FBC.JSONmatches = utils.readJSONFromString(TBAC.makeRequest(TBAC.makeYearEventKeyRequestURL('matches')))
	FBC.wipeDatabase()
	FBC.addTeamsToFirebase()
	FBC.addScorelessMatchesToFirebase()
	competition.updateTeamsAndMatchesFromFirebase()
	FBC.addTIMDsToFirebase(competition.matches) #You need to create the matches and teams before you call this

#makeFakeDatabase()
