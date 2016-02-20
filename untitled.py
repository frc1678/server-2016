class A(object):
	"""docstring for A"""
	def __init__(self, a, b):
		super(A, self).__init__()
		self.a = a
		self.b = b

class B(object):
	"""docstring for B"""
	def __init__(self, a):
		super(B, self).__init__()
		self.a = a
	def getA(self, o):
		return o.a
	def getB(self, o):
		return o.b
	def rank(self, os):
		return sorted(os, key=lambda x: (self.getA(x), getB(x)))
a = [A(1, 2), A(1, 3)]
b = B(10)
c = B.rank(a)
for d in c:
	print c.a, c.b

