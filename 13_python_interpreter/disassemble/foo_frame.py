def bar(y):
	z = y + 3			# <--- (3) and the interpreter is here
	return z

def foo():
	a = 1
	b = 2
	return a + bar(b)   # <--- (2) which is returning a call to bar

foo()					# <--- (1) imagine we're in a call to foo


'''
	Imagine the interpreter is at (3). The call stack looks like the following.

	bar Frame (newest)				Block Stack: [], Data Stack: [2, 3]
	foo Frame 						Block Stack: [], Data Stack: [1]
	main (module) Frame (oldest)	Block Stack: [], Data Stack: []
'''