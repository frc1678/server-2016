import random
from operator import attrgetter

class Animal(object):
	"""docstring for Animal"""
	def __init__(self, strength, speed):
		super(Animal, self).__init__()
		self.age = 0
		self.strength = strength
		self.speed = speed
		self.SI = strength + speed
		
	
class Generation(object):
	"""docstring for Generation"""
	def __init__(self, first):
		super(Generation, self).__init__()
		self.pop = []		
		self.first = first
		if self.first:
			for i in range(50):
				self.pop.append(Animal(random.randint(0, 100), random.randint(0, 100)))
	def breed(self, a1, a2):
		return Animal((a1.strength + a2.strength / 2), (a1.speed + a2.speed / 2))
		
	def breedNewGeneration(self):
		newGen = Generation(False)
		for i in range(len(self.pop) - 1):
			newGen.pop.append(self.breed(self.pop[i],self.pop[i+1]))
			newGen.pop.append(self.breed(self.pop[i],self.pop[i+1]))

		newGen.pop = sorted(newGen.pop, key=attrgetter("SI"))
		for j in range((len(newGen.pop) - 1) / 2):
			print len(newGen.pop)
			newGen.pop.remove(newGen.pop[j])
		return newGen
		
firstGen = Generation(True)
gen = 0
while True:
	if gen == 0:
		newGen = firstGen.breedNewGeneration()
		previousGen = newGen
	else:
		newGen = previousGen.breedNewGeneration()
		for animal in newGen.pop: print animal.SI()
		previousGen = newGen

	gen += 1