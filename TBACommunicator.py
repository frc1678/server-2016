import urllib3
import utils
import requests

class TBACommunicator(object):
	"""docstring for TBACommunicator"""
	def __init__(self):
		super(TBACommunicator, self).__init__()
		self.eventCode = 'hop'
		self.year = 2016
		self.eventCodeYear = str(self.year) + self.eventCode
		self.basicURL = "http://www.thebluealliance.com/api/v2/"
		self.headerKey = "X-TBA-App-Id"
		self.headerValue = "blm:server1678:004"
		
	def makeYearEventKeyRequestURL(self, key):
		return self.basicURL + 'event/' + self.eventCodeYear + '/' + key + '?' + self.headerKey + '=' + self.headerValue

	def makeRequest(self, url):
		http = urllib3.PoolManager()
		r = http.request('GET', url)
		return r.data

	def getEventTeamsRequestKey(self):
		return "event/{fullCode}/teams".format(fullCode = self.eventCodeYears)

	def makeEventTeamsRequest(self):
		return self.makeRequest(self.makeYearEventKeyRequestURL('teams'))
		return utils.readJSONFromString(self.makeRequest(self.makeYearEventKeyRequestURL('teams')))

	def makeTeamMediaRequest(self, key, year):
		return utils.readJSONFromString(self.makeRequest(self.basicURL + "team/" + key + "/" + str(year) + "/media" + '?' + self.headerKey + '=' + self.headerValue))

	def makeEventRankingsRequest(self):
		try: 
			requestResult = utils.readJSONFromString(self.makeRequest(self.makeYearEventKeyRequestURL('rankings')))[1:]
			return requestResult
		except: pass

	def makeSingleMatchRequest(self, matchNum):
		url = self.basicURL + "/match" + self.eventCodeYear + "_qm" + matchNum + + '?' + self.headerKey + '=' + self.headerValue
		return utils.readJSONFromString(self.makeRequest(url))

	def makeEventMatchesRequest(self):
		return utils.readJSONFromString(self.makeRequest(self.makeYearEventKeyRequestURL('matches')))

	def TBAIsBehind(self, matches):
		TBACompletedMatches = len(filter(lambda m: m["comp_level"] == 'qm' and m['score_breakdown'] != None, self.makeEventMatchesRequest()))
		return abs(len(matches) - TBACompletedMatches) >= 3

	def makeTBAMatches(self, matches):
		TBAMatches = {}
	   	func = lambda m: utils.setDictionaryValue(TBAMatches, m.number, self.makeSingleMatchRequest(m.number))
	   	map(func, matches)
	   	return TBAMatches
