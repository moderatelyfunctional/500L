class Interpreter:

	def __init__(self):
		self.stack = []
		self.environment = {}

	def LOAD_VALUE(self, number):
		self.stack.append(number)

	def PRINT_ANSWER(self):
		answer = self.stack.pop()
		print(answer)

	def ADD_TWO_VALUES(self):
		first_num = self.stack.pop()
		second_num = self.stack.pop()
		result = first_num + second_num
		self.stack.append(result)

	def STORE_NAME(self, name):
		value = self.stack.pop()
		self.environment[name] = value

	def LOAD_NAME(self, name):
		value = self.environment[name]
		self.stack.append(value)

	def parse_argument(self, instruction, argument, what_to_execute):
		''' Understand what the argument to each instruction means.'''
		numbers = ['LOAD_VALUE']
		names = ['LOAD_NAME', 'STORE_NAME']

		if instruction in numbers:
			argument = what_to_execute['numbers'][argument]
		elif instruction in names:
			argument = what_to_execute['names'][argument]

		return argument

	def run_code(self, what_to_execute):
		instructions = what_to_execute['instructions']
		numbers = what_to_execute['numbers']
		for each_step in instructions:
			instruction, argument = each_step # argument is an instruction specific index
			argument = self.parse_argument(instruction, argument, what_to_execute) # argument is now an instruction parameter
			
			bytecode_method = getattr(self, instruction)
			if not argument:
				bytecode_method()
			else:
				bytecode_method(argument)

two_sum_executions = {
	'instructions': [('LOAD_VALUE', 0),
					 ('LOAD_VALUE', 1),
					 ('ADD_TWO_VALUES', None),
					 ('PRINT_ANSWER', None)],
	'numbers': [7, 5]
}

three_sum_executions = {
	'instructions': [('LOAD_VALUE', 0),
					 ('LOAD_VALUE', 1),
					 ('ADD_TWO_VALUES', None),
					 ('LOAD_VALUE', 2),
					 ('ADD_TWO_VALUES', None),
					 ('PRINT_ANSWER', None)],
	'numbers': [7, 5, 8]
}

'''
	a = 1
	b = 2
	print(a + b)
	Python code for bytecode below

'''
variable_executions = {
	'instructions': [('LOAD_VALUE', 0),
					 ('STORE_NAME', 0),
					 ('LOAD_VALUE', 1),
					 ('STORE_NAME', 1),
					 ('LOAD_NAME', 0),
					 ('LOAD_NAME', 1),
					 ('ADD_TWO_VALUES', None),
					 ('PRINT_ANSWER', None)],
	'numbers': [1, 2],
	'names': ['a', 'b']
}

interpreter = Interpreter()
interpreter.run_code(two_sum_executions)
interpreter.run_code(three_sum_executions)
interpreter.run_code(variable_executions)






