#-*-coding:utf-8-*-

#Scipy Conference Crawler


__author__ = 'Marcel Caraciolo'

import os, re, sys
from Queue import Queue
from BeautifulSoup import BeautifulSoup
import urllib2, urllib
import pickle


class Scraper(object):

	def __init__(self,http_client=urllib2):
		self.url = "http://conference.scipy.org/scipy2011/schedule.php"
		self.http_client = http_client
		self.opener = self.http_client.build_opener()
		self.headers = {}


	def parse_lectures(self):
		request = self.opener.open(self.url)
		data = request.read()
		soup = BeautifulSoup(data)
		lectures = []
		resp = soup.findAll('td')
		for item in resp:
			pl = {}
			if not item.attrs:
				if not item.getString():
					if item.contents:
						#print item.contents
						items = [item.string for item in item.contents if item.string and item.string not in ['DS', 'CT','Schedule', 'Sign-up'] and
										not item.string.startswith('16') and  not item.string.startswith('17')]
						if items:
							if items[0]!= ' ':
								pl['authors'] = items[1].split(',')
								pl['title'] = items[0].replace('&nbsp;','')
							else:
								pl['authors'] = items[2].split(',')
								pl['title'] = items[1].replace('&nbsp;','')
							
							lectures.append(pl)
			
		return lectures



if __name__ == '__main__':
	info = Scraper()
	lectures  = info.parse_lectures()
	output = open('scipydata.pk1','wb')
	pickle.dump(lectures,output)
	output.close()