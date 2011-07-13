#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
"""
kmeans.py

Created by Marcel Caraciolo on 2010-01-06.
e-mail: caraciol (at) gmail.com   twitter: marcelcaraciolo
Copyright (c) 2009 Federal University of Pernambuco. All rights reserved.
"""


''' My simple attempt to cluster the friends of the twitter and organize them in twitter lists '''



__author__ = 'caraciol@gmail.com'
__version__ = '0.1'


import xmlrpclib
import socket
import random
from math import sqrt


clust_vertexes = {}
dClusters = None
expanded_vertexes = []
G = None

#Pearson distance index
def pearson(v1,v2):
	#v1 = [item[1] for item in v1]
	v2 = [item[1] for item in v2]
	
	#Simple sums
	sum1 = sum(v1)
	sum2 = sum(v2)
	
	#Sums of the squares
	sum1Sq = sum([pow(v,2) for v in v1])
	sum2Sq = sum([pow(v,2) for v in v2])
	
	#Sum of the products
	pSum = sum([v1[i]*v2[i] for i in range(len(v1))])
	
	#Calculate r (Pearson score)
	num = pSum - (sum1*sum2/len(v1))
	den = sqrt((sum1Sq-pow(sum1,2)/len(v1)) * (sum2Sq-pow(sum2,2)/len(v1)))
	if den == 0: return 0
	
	return 1.0 - num/ den


def expand_vertex(v):
	global clust_vertexes
	if v not in clust_vertexes.values() and v not in expanded_vertexes:
		return 0
	
	new_vertex = G.new_vertex()
	G.set_vertex_attribute(new_vertex,'shape','torus')
	edge = G.new_edge(v,new_vertex)
	G.set_edge_attribute(edge,'strength','0.1')
	expanded_vertexes.append(new_vertex)
	
	index = 0
	for key,value in clust_vertexes.items():
		if v == value:
			index = key
			break
			
	data = dClusters[index][0:5]
	for word,count in data:
		new_vt = G.new_vertex()
		G.set_vertex_attribute(new_vt,'label',str(word) + ' (' + str(count) + ')')
		G.set_vertex_attribute(new_vt,'fontsize','10')	
		G.set_edge_attribute(edge,'strength','0.3')
		dg = G.new_edge(new_vertex,new_vt)
	
	return 0

def showResults(dataClusters):
	global dClusters
	dClusters = dataClusters
	myPort = random.randint(20700,30000)
	G.set_vertex_style_attribute(0, "callback_left_doubleclick",
	"http://127.0.0.1:" + str(myPort) + "/expand_vertex")
	from SimpleXMLRPCServer import SimpleXMLRPCServer
	server = SimpleXMLRPCServer(("localhost", myPort))
	server.register_introspection_functions()
	server.register_function(expand_vertex)
	print "Listening for callbacks from ubigraph on the port %d..." % (myPort,)
	server.serve_forever()



def open_ubigraph_server(url='http://127.0.0.1:20738/RPC2'):
	''' Open connection to Ubigraph XML-RPC server '''
	server_url = url
	server = xmlrpclib.Server(server_url)
	
	G = server.ubigraph
	
	try:
		G.clear()
	except socket.error,msg:
		print "error:\tcan't connected to the Ubigraph server, the server is running ?\n\terror message:%s\n" % msg
		exit()
	
	return G


def getColors(k):
	''' Get the colors based on the k colors
		Params:
			k: the number of colors
		Returns:
			the list of colors
	'''
	colors = ["#00ff00", "#ff0000", "#ffff00", "#0000ff" , "#FF00FF", '#FF9900', '#FF66CC', '#FF00FF','#33FF00', '#33FFFF']  * 2
	colorsList = []
	
	for i in range(k):
		colorsList.append(colors[i])
		
	return colorsList
	
def kcluster(ubi_server,users,rows,distance=pearson,k=4):
	''' Run the K-means algorithm
		Parameters:
			ubi_server: the ubi server link.
			users: The users 
			rows: the data
			distance: the distance measure
			k: the number of clusters
	'''
	global clust_vertexes
	global G
	
	G = ubi_server
	vertexes = {}
	clust_vertexes = {}
	
	colors = getColors(k)
	
	#Determine the minimum and maximum values for each point
	ranges = [(min([row[i][1] for row in rows]), max([row[i][1] for row in rows])) for i in range(len(rows[0]))]


	#Create k randomly placed centroids
	clusters = [[random.random()* (ranges[i][1]-ranges[i][0]) + ranges[i][0] for i in range(len(rows[0]))] 
					for j in range(k)]
	
	
	#Draw the users
	v = 0
	for user in users:
		new_vertex = ubi_server.new_vertex()
		ubi_server.set_vertex_attribute(new_vertex,'label',user)
		ubi_server.set_vertex_attribute(new_vertex,'shape','sphere')
		ubi_server.set_vertex_attribute(new_vertex,'fontsize','10')		
		vertexes.update({v: new_vertex})
		v+=1

	#Draw the clusters
	for l in range(k):
		new_vertex = ubi_server.new_vertex()
		ubi_server.set_vertex_attribute(new_vertex,'shape','cube')
		ubi_server.set_vertex_attribute(new_vertex, "color", colors[l])
		clust_vertexes.update({l: new_vertex})
	

	lastmatches = None
	matches = {}
	for t in range(100):
		print 'Iteration %d' %t
		bestmatches = [ [] for i in range(k)]
		#Find which centroid is the closest for each row
		for j in range(len(rows)):
			row = rows[j]
			bestmatch = 0
			for i in range(k):
				d =  distance(clusters[i],row)
				if d < distance(clusters[bestmatch],row): bestmatch = i
			bestmatches[bestmatch].append(j)
			

			if (j,bestmatch) not in matches:
				ubi_server.set_vertex_attribute(vertexes[j], "color", colors[bestmatch])
				e_id = ubi_server.new_edge(vertexes[j],clust_vertexes[bestmatch])
				ubi_server.set_edge_attribute(e_id,'strength','0.3')
				matches.update({(j,bestmatch): e_id})
			
			
			if lastmatches:
				for p in range(len(lastmatches)):
					if j in lastmatches[p] and j not in bestmatches[p]:
						ep_id = matches.get((j,p),None)
						ubi_server.remove_edge(ep_id)
						del matches[(j,p)]
						break
	
			
		#If the results are the same as last time, this is complete
		if bestmatches == lastmatches: break
		lastmatches = bestmatches
		
		#Move the centroids to the average of their members
		for i in range(k):
			avgs = [0.0]*len(rows[0])
			if len(bestmatches[i]) > 0:
				for rowid in bestmatches[i]:
					for m in range(len(rows[rowid])):
						avgs[m]+=rows[rowid][m][1]
				for j in range(len(avgs)):
					avgs[j]/=len(bestmatches[i])
				clusters[i]=avgs
	
	return bestmatches, clust_vertexes