import dis
import operator

from block import Block
from frame import Frame
from function import Function

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

	# Data stack manipulations

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

	def jump(self, jump):
		self.frame.last_instruction = jump

	# Block stack manipulations

	def push_block(self, b_type, handler = None):
		stack_height = len(self.frame.stack)
		self.frame.block_stack.append(Block(b_type, handler, stack_height))

	def pop_block(self):
		self.frame.block_stack.pop()

	def unwind_block(self, block):
		# Unwind the value on the data stack corresponding to a given block.
		if block.type == 'except-handler':
			# The exception itself is on the data stack as type, value, traceback
			offset = 3
		else:
			offset = 0

		while len(self.frame.stack) > block.level + offset:
			self.pop()

		if block.type == 'except-handler':
			traceback, value, exctype = self.popn(3):
			self.last_exception = exctype, value, traceback

	def manage_block_stack(self, why):
		frame = self.frame
		block = frame.block_stack[-1]
		if block.type == 'loop' and why == 'continue':
			self.jump(self.return_value)
			why = None
			return why

		self.pop_block()
		self.unwind_block(block)

		if block.type == 'loop' and why == 'break':
			why = None
			self.jump(block.handler)
			return why

		if (block.type in ['setup-except', 'finally']) and why == 'exception':
			self.push_block('except-handler')
			exctype, value, tb = self.last_exception
			self.push(tb, value, exctype)
			self.push(tb, value, exctype) # yes, twice
			why = None
			self.jump(block.handler)
			return why

		elif block.type == 'finally':
			if why in ('return', 'continue'):
				self.push(return_value)

			self.push(why)
			why = None
			self.jump(block.handler)
			return why
		return why

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

	# Stack manipulations

	def byte_LOAD_CONST(self, const):
		self.push(const)

	def byte_POP_TOP(self):
		self.pop()

	# Names
	def byte_LOAD_NAME(self, name):
		frame = self.frame
		if name in frame.f_locals:
			val = frame.f_locals[name]
		elif name in frame.f_globals:
			val = frame.f_globals[name]
		elif name in frame.f_builtins:
			val = frame.f_builtins[name]
		else:
			raise NameError("name '%s' is not defined" % name)
		self.push(val)

	def byte_STORE_NAME(self, name):
		self.frame.f_locals[name] = self.pop()

	def byte_LOAD_FAST(self, name):
		if name in self.frame.f_locals:
			val = self.frame.f_locals[name]
		else:
			raise UnboundLocalError("local variable '%s' referenced before assignment" % name)
		self.push(val)

	def byte_STORE_FAST(self, name):
		self.frame.f_locals[name] = self.pop()

	def byte_LOAD_GLOBAL(self, name):
		f = self.frame
		if name in f.f_globals:
			val = f.f_globals[name]
		elif name in f.f_builtins:
			val = f.f_builtins[name]
		else:
			raise NameError("global name '%s' is not defined" % name)
		self.push(val)

	# Operators

	BINARY_OPERATORS = {
		'POWER': pow,
		'MULTIPLY', operator.mul,
		'FLOOR_DIVIDE': operator.floordiv,
		'TRUE_DIVIDE': operator.truediv,
		'MODULO': operator.mod,
		'ADD': operator.add,
		'SUBTRACT': operator.sub,
		'SUBSCR': operator.getitem,
		'LSHIFT': operator.lshift,
		'RSHIFT': operator.rshift,
		'AND': operator.and_,
		'XOR': operator.xor,
		'OR': operator.or_,
	}

	def binary_operator(self, op):
		x, y = self.popn(2)
		self.push(self.BINARY_OPERATORS[op](x, y))

	COMPARE_OPERATORS = [
		operator.lt,
		operator.le,
		operator.eq,
		operator.ne,
		operator.gt,
		operator.ge,
		lambda x, y: x in y,
		lambda x, y: x not in y,
		lambda x, y: x is y,
		lambda x, y: x is not y,
		lambda x, y: issubclass(x, Exception) and issubclass(x, y),
	]

	def byte_COMPARE_OP(self, opnum):
		x, y = self.popn(2)
		self.push(self.COMPARE_OPERATORS[opnum](x, y))

	# Attributes and indexing

	def byte_LOAD_ATTR(self, attr):
		obj = self.pop()
		val = getattr(obj, attr)
		self.push(val)

	def byte_STORE_ATTR(self, name):
		val, obj = self.popn(2)
		setattr(obj, name, val)

	# Building

	def byte_BUILD_LIST(self, count):
		elts = self.popn(count)
		self.push(elts)

	def byte_BUILD_MAP(self, size):
		self.push({})

	def byte_STORE_MAP(self):
		the_map, val, key = self.popn(3)
		the_map[key] = val
		self.push(the_map)

	def byte_LIST_APPEND(self, count): 
		val = self.pop()
		the_list = self.frame.stack[-count] # peek
		the_list.append(val)

	# Jumps

	def byte_JUMP_FORWARD(self, jump):
		self.jump(jump)

	def byte_JUMP_ABSOLUTE(self, jump):
		self.jump(jump)

	def byte_POP_JUMP_IF_TRUE(self, jump):
		val = self.pop()
		if val:
			self.jump(jump)

	def byte_POP_JUMP_IF_FALSE(self, jump):
		val = self.pop()
		if not val:
			self.jump(jump)

	# Blocks

	def byte_SETUP_LOOP(self, dest):
		self.push_block('loop', dest)

	def byte_GET_ITER(self):
		self.push(iter(self.pop()))

	def byte_FOR_ITER(self, jump):
		iterobj = self.top()
		try:
			v = next(iterobj)
			self.push(v)
		except StopIteration:
			self.pop()
			self.jump(jump)

	def byte_BREAK_LOOP(self):
		return 'break'

	def byte_POP_BLOCK(self):
		self.pop_block()

	# Functions

	def byte_MAKE_FUNCTION(self, argc):
		name = self.pop()
		code = self.pop()
		defaults = self.popn(argc)
		globs = self.frame.f_globals
		fn = Function(name, code, globs, defaults, None, self)
		self.push(fn)

	def byte_CALL_FUNCTION(self, arg):
		lenKw, lenPos = divmod(arg, 256) #KWargs not supported here
		posargs = self.popn(lenPos)

		func = self.pop()
		frame = self.frame
		retval = func(*posargs)
		self.push(retval)

	def byte_RETURN_VALUE(self):
		self.return_value = self.pop()
		return 'return'

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
					self.unary_operator(byte_name[6:])
				elif byte_name.startswith('BINARY_'):
					self.binary_operator(byte_name[7:])
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

