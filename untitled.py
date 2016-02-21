class A(object):
	"""docstring for A"""
	def __init__(self, a, b):
		super(A, self).__init__()
		self.a = a
		self.b = b

class B(object):
	"""docstring for B"""
	def __init__(self):
		super(B, self).__init__()
	def rank(self, os):
		return sorted(os, key=lambda x: (self.getA(x), self.getB(x)), reverse=True)
	def getA(self, o):
		return o.a
	def getB(self, o):
		return o.b

c = [A(12, 10), A(12, 20)]
for d in c:
	print d.a, d.b

b = B()
e = b.rank(c)	
for f in e:
	print f.a, f.b