import sys
import re
import math
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

class Cluster:
	def __init__(self, label):
		self.children = []
		self.point = []
		self.all = []
		self.label = label
		self.height = '0'

	def addPoint(self, value):
		self.point.append(value)

	def setAll(self, point):
		self.all.append(point)

	def getAll(self):
		return self.all

	def appendAll(self, all):
		for a in all:
			self.all.append(a)

	def addChild(self, child):
		self.children.append(child)

	def setHeight(self, height):
		self.height = height

	def getHeight(self):
		return self.height

	def getLabel(self):
		return self.label

	def getChildren(self):
		return self.children

	def getPoint(self):
		return self.point

	def pointToString(self):
		return ', '.join(str(p) for p in self.point)


def euclideanDist(p1, p2):
	""" Get the Euclidean distance between two clusters """

	dist = 0

	for i, val in enumerate(p1):
		dist += (val - p2[i]) ** 2

	return math.sqrt(dist)

def completeLink(c1, c2):
	maxDist = -1

	for p1 in c1.getAll():
		for p2 in c2.getAll():
			dist = euclideanDist(p1, p2)

			if dist > maxDist:
				maxDist = dist

	return maxDist

def agglomerative(clusters):
	""" Cluster using the agglomerative hierarchy method """

	s = None
	r = None
	
	while len(clusters) > 1:
		minDist = None
		for i, c1 in enumerate(clusters):
			for c2 in clusters[i + 1:]:
				dist = completeLink(c1, c2)

				if minDist is None or dist < minDist:
					s = c1
					r = c2
					minDist = dist

		newClusters = []
		for cluster in clusters:
			if cluster != r and cluster != s:
				newClusters.append(cluster)
			elif cluster == r:
				newCluster = Cluster(r)
				newCluster.addChild(r)
				newCluster.addChild(s)
				newCluster.appendAll(r.getAll())
				newCluster.appendAll(s.getAll())
				newCluster.setHeight(str("{0:.3f}".format(minDist)))
				newClusters.append(newCluster)
		clusters = newClusters

	return clusters

def cutDendrogram(cluster, thresh):
	cut = []

	if float(cluster.getHeight()) <= float(thresh):
		return [cluster]
	else:
		for cluster in cluster.getChildren():
			cut += cutDendrogram(cluster, thresh)

	return cut

def buildXML(tree, cluster):
	if cluster.getPoint():
		ET.SubElement(tree, 'leaf', {'height': cluster.getHeight(), 'data': cluster.pointToString()})

	for child in cluster.getChildren():
		if not child.getPoint():
			node = ET.SubElement(tree, 'node', {'height': child.getHeight()})
			buildXML(node, child)
		else:
			ET.SubElement(tree, 'leaf', {'height': child.getHeight(), 'data': child.pointToString()})

	return tree

def createDendrogram(cluster):
	tree = ET.Element('tree', {'height': cluster.getHeight()})
	
	tree = buildXML(tree, cluster)

	return ET.tostring(tree)



def readData(raw_data):
	""" Parse data """

	fp = open(raw_data, 'r')
	data = fp.read().splitlines()

	restrictions = re.split(r',', data.pop(0))

	clusters = []

	for label, line in enumerate(data):
		line = re.split(r',', line)
		cluster = Cluster(label)
		
		for i, col in enumerate(line):
			if int(restrictions[i]) == 1:
				cluster.addPoint(float(col))

		cluster.setAll(cluster.getPoint())
		clusters.append(cluster)

	return clusters
		

if __name__ == '__main__':
	raw_data = sys.argv[1]
	thresh = None
	if len(sys.argv) > 2:
		thresh = sys.argv[2]

	clusters = readData(raw_data)
	clusters = agglomerative(clusters)
	tree = createDendrogram(clusters[0])

	cut = None
	if thresh:
		cut = cutDendrogram(clusters[0], thresh)

	print minidom.parseString(tree).toprettyxml(indent="   ")

	if cut:
		for c in cut:
			cDom = createDendrogram(c)
			print
			print
			print minidom.parseString(cDom).toprettyxml(indent="   ")




