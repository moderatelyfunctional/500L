import dis

from frame import Frame

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

	def make_frame(self, code, callargs = {}, global_names = None, local_names = None):
		if global_names and local_names:
			local_names = global_names
		elif self.frames:
			global_names = self.frame.global_names
			local_names = {}
		else:
			global_names = local_names = {
				'__builtins__'	: 	__builtins__,
				'__name__'		:   '__main__',
				'__doc__'		: 	None,
				'__package__'	: 	None,
			}
		local_names.update(callargs)
		frame = Frame(code, global_names, local_names, self.frame)
		return frame

	def top(self):
		return self.frame.stack[-1]

	def pop(self):
		return self.frame.stack.pop()

	def push(self, *vals):
		self.frame.stack.extend(vals)

	def popn(self, n):
		'''
			Pops a number of values from the value stack.
			A list of n values is returned, the deepest value first
		'''
		if n:
			ret = self.frame.stack[-n:]
			self.frame.stack[-n:] = []
			return ret
		else:
			return []

	def push_frame(self, frame):
		self.frames.append(frame)
		self.frame = frame

	def pop_frame(self):
		self.frames.pop()
		if self.frames:
			self.frame = self.frames[-1]
		else:
			self.frame = None

	def run_frame(self):
		'''
			Run a frame until it returns
			Exceptions are raised, the return value is returned.
		'''
		self.push_frame(frame)
		while True:
			byte_name, arguments = self.parse_byte_and_args()
			why = self.dispatch(byte_name, arguments)

			# Deal with any block management
			while why and frame.block_stack:
				why = self.manage_block_stack(why)

			if why:
				break

		self.pop_frame()
		
		if why == 'exception':
			exc, val, tb = self.last_exception
			e = exc(val)
			e.__traceback__ = tb
			raise e

		return self.return_value

	def parse_byte_and_args(self):
		f = self.frame
		op_offset = f.last_instruction
		bytecode = f.code_obj.co_code[op_offset]
		f.last_instruction += 1
		byte_name = dis.opname[bytecode]

		if bytecode >= dis.HAVE_ARGUMENT:
			# index into the bytecode
			arg = f.code_obj.co_code[f.last_instruction:f.last_instruction + 2]
			f.last_instruction += 2 # advance the instruction pointer
			arg_val = arg[0] + (arg[1] * 256)
			if bytecode in dis.hasconst:
				arg = f.code_obj.co_consts[arg_val]
			elif bytecode in dis.hasname:
				arg = f.code_obj.co_names[arg_val]
			elif bytecode in dis.haslocal:
				arg = f.code_obj.co_varnames[arg_val]
			elif bytecode in dis.hasjrel:
				arg = f.last_instruction + arg_val
			else:
				arg = arg_val
			argument = [arg]
		else:
			argument = []

		return byte_name, argument

	def dispatch(self, byte_name, argument):
		'''
			Dispatch by byte_name to the corresponding methods.
			Exceptions are caught and set on the virtual machine
		'''
		why = None
		try:
			bytecode_fn = getattr(self, 'byte_%s' % byte_name, None)
			if not bytecode_fn:
				if byte_name.startswith('UNARY_'):
					self.unaryOperator(byte_name[6:])
				elif byte_name.startswith('BINARY_'):
					self.binaryOperator(byte_name[7:])
				else:
					raise VirtualMachineError('unsupported bytecode type %s' % byte_name)
			else:
				why = bytecode_fn(*argument)
		except:
			self.last_exception = sys.exc_info()[:2] + (None,)
			why = 'exception'

		return why

	def run_code(self, code, global_names = None, local_names = None):
		''' An entry point to execute code with the virtual machine'''
		frame = self.make_frame(code, 
								global_names = global_names,
								local_names = local_names)
		self.run_frame(frame)

