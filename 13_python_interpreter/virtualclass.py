class VirtualMachineError(Exception):
	pass

'''
	The VirtualMachine stores the call stack, the exception state,
	and return values while they're being passed between frames.
	The run_code function takes compiled code as an argument and 
	runs an initial frame. The call stack may expand and shrink from here
	as the program executes and when the first frame returns (at some point),
	execution is finished.
'''
class VirtualMachine(object):

	def __init__(self):
		self.frames = []	# the call stack of frames
		self.frame = None	# the current frame
		self.return_value = None
		self.last_exception = None

	def run_code(self, code, global_names = None, local_names = None):
		''' An entry point to execute code with the virtual machine'''
		frame = self.make_frame(code, 
								global_names = global_names,
								local_names = local_names)
		self.run_frame(frame)

