class DBDB(object):

	def __init__(self, f):
		self._storage = Storage(f)
		self._tree = BinaryTree(self._storage)