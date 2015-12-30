import json
import urllib3
from StringIO import StringIO
from subprocess import call

basicURL = "http://www.thebluealliance.com/api/v2/"
headerKey = "X-TBA-App-Id"
headerValue = "blm:pitscout:001" # set to "<your initials>:TBA_communicator:0"
dropboxFolderToCreateFoldersIn = "/Users/brytonmoeller/Dropbox/ScoutingPhotos2016/"

def jprint(JSON):
	print(json.dumps(JSON, sort_keys=True, indent=4))

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

def readJSONFromString(string):
	return json.load(StringIO(string))

teamsRequestResult = readJSONFromString(makeEventTeamsRequest('casj', 2015))
for team in teamsRequestResult:
	folderName = str(team['team_number'])
	call(["mkdir", dropboxFolderToCreateFoldersIn + folderName])
