import urllib3
import DataModel
import firebaseCommunicator
import utils

############# Getting TBA Data ###################
basicURL = "http://www.thebluealliance.com/api/v2/"
headerKey = "X-TBA-App-Id"
headerValue = "blm:serverProof1678:004" # set to "<your initials>:TBA_communicator:0"
eventCode = 'casj'
year = 2015

competition = DataModel.Competition()
competition.eventCode = eventCode

def makeYearEventKeyRequestURL(year, event, key):
	return basicURL + 'event/' + str(year) + event + '/' + key + '?' + headerKey + '=' + headerValue

def makeRequest(url):
	http = urllib3.PoolManager()
	r = http.request('GET', url)
	return r.data

def getEventTeamsRequestKey(competition, year):
	return "event/{year}{competition}/teams".format(competition = competition, year = year)

def makeEventTeamsRequest(competition, year):
	return makeRequest(makeYearEventKeyRequestURL(year, competition, 'teams'))

def makeFakeDatabase(eventCode='casj', year=2015):
	FBC = firebaseCommunicator.FirebaseCommunicator(competition)
	FBC.JSONteams = utils.readJSONFromString(makeEventTeamsRequest(eventCode, year))
	FBC.JSONmatches = utils.readJSONFromString(makeRequest(makeYearEventKeyRequestURL(year, eventCode, 'matches')))
	#FBC.wipeDatabase()
	FBC.addTeamsToFirebase()
	FBC.addScorelessMatchesToFirebase()
	competition.updateTeamsAndMatchesFromFirebase()
	FBC.addTIMDsToFirebase(competition.matches) #You need to create the matches and teams before you call this


makeFakeDatabase()
