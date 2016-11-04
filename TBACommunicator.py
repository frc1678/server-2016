import requests
import json
import utils
import urllib3


class TBACommunicator(object):
	"""docstring for TBACommunicator"""
	def __init__(self):
		super(TBACommunicator, self).__init__()
		self.code = 'hop'
		self.year = 2016
		self.key = str(self.year) + self.code
		self.basicURL = "http://www.thebluealliance.com/api/v2/"
		self.headerKey = "X-TBA-App-Id"
		self.headerValue = "blm:server-1678:004"


	def makeYearEventKeyRequestURL(self, key):
		return basicURL + 'event/' + str(self.year) + self.code + '/' + key + '?' + headerKey + '=' + headerValue

	def makeRequest(self, url):
		http = urllib3.PoolManager()
		r = http.request('GET', url)
		return r.data

	def makeRequest(self, url):
		return utils.makeASCIIFromJSON(requests.get(url, headers={self.headerKey: self.headerValue}).json())

	def makeEventKeyRequestURL(self, key):
		return self.basicURL + 'event/' + self.key + '/' + key

	def makeEventTeamsRequest(self):
		return self.makeRequest(self.makeYearEventKeyRequestURL('teams'))

	def makeTeamMediaRequest(self, teamKey):
		return self.makeRequest(self.basicURL+'team/'+teamKey+"/"+str(self.year)+'/media' + '?' +headerKey + '=' + headerValue)

	def makeEventRankingsRequest(self):
		return self.makeRequest(self.makeEventKeyRequestURL('rankings'))[1:]

	def makeEventMatchesRequest(self):
		return self.makeRequest(self.makeEventKeyRequestURL('matches'))
		
	def makeSingleMatchRequest(self, matchNum):
		url = self.basicURL + "match/" + str(self.key) + "_qm" + str(matchNum)
		return utils.makeASCIIFromJSON(self.makeRequest(url))

	def TBAIsBehind(self, matches):
		TBACompletedMatches = len(filter(lambda m: m["comp_level"] == 'qm' and m['score_breakdown'] != None, self.makeEventMatchesRequest()))
		return abs(len(matches) - TBACompletedMatches) >= 3


