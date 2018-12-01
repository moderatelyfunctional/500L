class Frame(object):

	def __init__(self, code_obj, global_names, local_names, prev_frame):
		self.code_obj = code_obj			# created by the compiler
		self.global_names = global_names
		self.local_names = local_names
		self.prev_frame = prev_frame
		self.stack = []						# the data stack
		if prev_frame:
			self.builtin_names = prev_frame.builtin_names
		else:
			self.builtin_names = local_names['__builtins__']
			if hasattr(self.builtin_names, '__dict__'):
				self.builtin_names = self.builtin_names.__dict__

		self.last_instruction = 0			# represents the instruction pointer
		self.block_stack = []