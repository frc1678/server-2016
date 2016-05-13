import requests
import numpy as np

basicURL = "http://www.thebluealliance.com/api/v2/"
headerKey = "X-TBA-App-Id"		
headerValue = "blm:OPRs:004"

einsteinTeams = requests.get(basicURL + "event/2016cmp/teams", headers={headerKey:headerValue}) 
einsteinTeams = einsteinTeams.json()
einsteinTeams = 

def getTeamAvgOPR(team):
	teamNum = str(team["team_number"])
	teamEvents = requests.get(basicURL + "team/" + team["key"] + "/2016/events",headers={headerKey:headerValue}).json() 
	remove = lambda e: teamEvents.remove(e) if e["event_code"] == "cmp" else None
	map(remove, teamEvents)
	getStats = lambda e: requests.get(basicURL + "event/" + e["key"] + "/stats" ,headers={headerKey:headerValue}).json()["oprs"][teamNum]
	return np.mean(map(getStats, teamEvents))

x = [lambda t: getTeamAvgOPR(t)]
teams = sorted(einsteinTeams,key=lambda t:(x[0](t)), reverse=True)
a = [118, 1241, 5830,3494, 3966, 3061, 846, 3250, 180, 503, 3284, 3494, 360]
teams = [t for t in teams if int(t["team_number"]) not in a]
for t in teams: print str(teams.index(t) + 1) + ": " + str(t["team_number"]) + " - " + str(getTeamAvgOPR(t))
