import os
import http.server

class ServerException(Exception):
	'''For internal error reporting.'''
	pass

class case_no_file(object):
	'''File or directory does not exist.'''

	def test(self, handler):
		return not os.path.exists(handler.absolute_path)

	def act(self, handler):
		raise ServerException("'{0}' not found".format(handler.path))

class case_existing_file(object):
	'''File exists.'''

	def test(self, handler):
		return os.path.isfile(handler.absolute_path)

	def act(self, handler):
		handler.handle_file(handler.absolute_path)

class case_always_fail(object):
	'''Base case if nothing else worked.'''

	def test(self, handler):
		return True

	def act(self, handler):
		raise ServerException("Unknown object '{0}'".format(handler.path))

'''
BaseHTTPRequestHandler parses incoming HTTP requests and calls 
do_x where x in (GET|POST|PUT).

Overriding the appropriate do_x function calls that function instead 
for the given HTTP request.
'''
class RequestHandler(http.server.BaseHTTPRequestHandler):
	'''
	If the requested path maps to a file, that file is served.
	If anything goes wrong, an error page is constructed.
	'''

	Cases = [case_no_file(),
			 case_existing_file(),
			 case_always_fail()]

	Error_Page = '''\
		<html>
			<body>
				<h1>Error accessing {path}</h1>
				<p>{msg}</p>
			</body>
		</html>
	'''

	def send_content(self, content, status=200):
		self.send_response(status)
		self.send_header("Content-Type", "text/html")
		self.send_header("Content-Length", str(len(content)))
		self.end_headers()
		self.wfile.write(content) # Strings in Python3 are Unicode so have to convert to binary

	def handle_file(self, absolute_path):
		try:
			with open(absolute_path, 'rb') as reader: # reading the file as binary
				content = reader.read() # for GB sized data (videos), consider streaming data
			self.send_content(content)
		except IOError as msg:
			msg = "'{0}' cannot be read: {1}".format(self.path, msg)
			self.handle_error(msg)

	def handle_error(self, msg):
		content = self.Error_Page.format(path = self.path, msg = msg).encode('utf-8')
		self.send_content(content, 404)

	# Handles a GET request
	def do_GET(self):
		try:

			# figure out what exactly is being requested.
			self.absolute_path = os.getcwd() + self.path

			# figure out how to handle it
			for case in self.Cases: # for loop replaces a series of if statements
				if case.test(self):
					case.act(self)
					break

		# handle exceptions
		except Exception as msg:
			self.handle_error(msg)

if __name__ == '__main__':
	serverAddress = ('', 8080) # run on the current machine with port 8080
	server = http.server.HTTPServer(serverAddress, RequestHandler)
	server.serve_forever()

	'''
	a browser requesting http://localhost:8080 sends a GET request for the server and
	another request for /favicon.ico, an icon to put on the browser tab
	'''