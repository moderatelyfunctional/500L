import dis

def loop():
	x = 1
	while x < 5:
		x = x + 1
	return x

print(dis.dis(loop))