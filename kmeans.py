import sys
import random
import math

class Kmeans:
	def __init__(self, filename, k):
		self.f = open(filename)
		self.restrictions = [] 
		self.data = []
		self.k = k
		self.iterations = 0

		self.centroids = []

		self.clusters = []
		
		self.getRestrictions()
		self.getData()
		self.f.close()
	
	def getRestrictions(self):
		"""Parse the first line of the csv file"""
		lst = self.f.readline().strip().split(",")
		self.restrictions = map(int, lst)

	def getData(self):
		"""Parse data, convert eligible data to floats"""

		numOfColumns = len(self.restrictions)

		for line in self.f:
			lst = line.strip().split(',')
			for i in range(numOfColumns):
				if self.restrictions[i] == 1:
					lst[i] = float(lst[i])
			self.data.append(lst)

	def getInitialCentroids(self):
		"""Randomly get the initial centroids"""

		numLines = len(self.data)

		indexes = []
		while len(indexes) != self.k:
			index = random.randint(0, numLines - 1)
			if index not in indexes:
				indexes.append(index)

		for i in indexes:
			self.centroids.append(self.data[i][:])

	def run(self):
		self.getInitialCentroids()

		self.iterations = 0
		change = True
		while (change):

			sums = []
			clusterCounts = []
			newClusters = []
			for i in range(self.k):
				sums.append([0 for i in range(len(self.restrictions))])
				clusterCounts.append(0)
				newClusters.append([])


			change = False
			for i, record in enumerate(self.data):

				j = self.bestCentroid(record)


				newClusters[j].append(i) 

				# check if any reassignment happens
				if self.clusters == [] or i not in self.clusters[j]:
					change = True
				self.addToSums(sums, j, record)
				clusterCounts[j] += 1

			self.updateCentroids(sums, clusterCounts)
			self.clusters = newClusters
			self.iterations += 1

	
	def bestCentroid(self, record):
		"""Return the index of the closest centroid to the record"""
		j = -1
		minDistance = None

		for index in range(len(self.centroids)):
			d = self.distance(record, self.centroids[index])

			if minDistance == None or d < minDistance:
				minDistance = d
				j = index

		return j
	
	def addToSums(self, sums, j, record):
		"""Add the record to the appropriate sum"""

		for i in range(len(self.restrictions)):
			if self.restrictions[i] == 1:
				sums[j][i] += record[i]


	def updateCentroids(self, sums, clusterCounts):
		"""Calculate the new centroid"""

		for i in range(len(self.centroids)):
			# if no assignments occurred, skip the centroid
			if clusterCounts[i] == 0:
				continue

			for j in range(len(self.restrictions)):
				if self.restrictions[j] == 1:
					self.centroids[i][j] = sums[i][j] / clusterCounts[i]


	def distance(self, x1, x2):
		"""Return the distance between two vectors"""

		result = 0

		for i in range(len(self.restrictions)):
			if self.restrictions[i] == 1:
				result += (x2[i] - x1[i]) ** 2

		return math.sqrt(result)

	def printStats(self):
		"""Print out stats of each cluster"""

		for i in range(len(self.clusters)):
			print 'Cluster', str(i) +  ':'
			print 'Center:', self.centerOfCluster(i)
			maxDist, minDist, avgDist, sumOfSquaredErrors = self.clusterDistances(i)
			print 'Max Dist. to Center:', maxDist
			print 'Min Dist. to Center:', minDist
			print 'Avg Dist. to Center:', avgDist
			print 'Sum Of Squared Errors:', sumOfSquaredErrors

			print len(self.clusters[i]), 'Points:'

			for index in self.clusters[i]:
				print ','.join(str(x) for x in self.data[index])
			print


	def centerOfCluster(self, i):
		"""return string representation of center of cluster"""

		centroid = self.centroids[i]
		result = ""
		for i in range(len(self.restrictions)):
			if self.restrictions[i] == 1:
				result += str(centroid[i]) + ","

		if result != "":
			result = result[:-1]
		
		return result


	def clusterDistances(self, i):
		"""Return the max, min, and average distance in a cluster"""

		maxDist = None
		minDist = None
		avgDist = 0
		sumOfSquaredErrors = 0
		numOfPoints = len(self.clusters[i])

		for j in self.clusters[i]: 
			d = self.distance(self.centroids[i], self.data[j])

			if maxDist == None or d > maxDist:
				maxDist = d;

			if minDist == None or d < minDist:
				minDist = d

			avgDist += d
			sumOfSquaredErrors += d ** 2

		avgDist /= float(numOfPoints)

		return maxDist, minDist, avgDist, sumOfSquaredErrors


if __name__ == '__main__':
	# set seed for testing
	random.seed(1)

	if len(sys.argv) != 3:
		print 'Usage: python kmeans.py <Filename> <k>'
		sys.exit(1)
	
	filename = sys.argv[1]
	k = int(sys.argv[2])

	kmeans = Kmeans(filename, k)
	kmeans.run()
	print 'Iterations:', kmeans.iterations
	kmeans.printStats()
