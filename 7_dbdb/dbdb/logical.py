class LogicalBase(object):

	def set(self, key, value):
		if self._storage.lock():
			self._refresh_tree_ref()
		self._tree_ref = self._insert(
			self._follow(self._tree_ref), key, self.value_ref_class(value))

	def get(self, key):
		if not self._storage.locked:
			self._refresh_tree_ref()
		return self._get(self._follow(self._tree_ref), key)

	def _refresh_tree_ref(self):
		self._tree_ref = self.node_ref_class(
			address = self._storage.get_root_address())