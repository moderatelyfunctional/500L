import os
import subprocess
import http.server

class ServerException(Exception):
	'''For internal error reporting.'''
	pass


class base_case(object):
	'''Parent class for case handlers.'''

	def handle_file(self, handler, absolute_path):
		try:
			with open(absolute_path, 'rb') as reader: # reading the file as binary
				content = reader.read() # for GB sized data (videos), consider streaming data
			handler.send_content(content)
		except IOError as msg:
			msg = "'{0}' cannot be read: {1}".format(self.path, msg)
			self.handle_error(msg)

	def list_dir(self, handler, absolute_path):
		try:
			entries = os.listdir(absolute_path)
			bullets = ['<li>{0}</li>'.format(e) for e in entries 
					   if not e.startswith('.')]
			page = handler.Listing_Page.format('\n'.join(bullets)).encode('utf-8')
			handler.send_content(page)
		except OSError as msg:
			msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
			self.handle_error(msg)

	def run_cgi(self, handler, absolute_path):
		cmd = ['python', absolute_path]
		p = subprocess.Popen(cmd, stdin=subprocess.PIPE,stdout=subprocess.PIPE)
		output, err = p.communicate()
		handler.send_content(output)

	def index_path(self, handler):
		return os.path.join(handler.absolute_path, 'index.html')

	def test(self, handler):
		assert False, 'Not Implemented.'

	def act(self, handler):
		assert False, 'Not Implemented.'

class case_no_file(base_case):
	'''File or directory does not exist.'''

	def test(self, handler):
		return not os.path.exists(handler.absolute_path)

	def act(self, handler):
		raise ServerException("'{0}' not found".format(handler.path))

class case_existing_file(base_case):
	'''File exists.'''

	def test(self, handler):
		return os.path.isfile(handler.absolute_path)

	def act(self, handler):
		self.handle_file(handler, handler.absolute_path)

class case_directory_index_file(base_case):
	'''Server index.html page for a directory.'''

	def test(self, handler):
		return os.path.isdir(handler.absolute_path) and \
			   os.path.isfile(self.index_path(handler))

	def act(self, handler):
		self.handle_file(handler, self.index_path(handler))

class case_directory_no_index_file(base_case):
	'''Serve listing for a directory without an index.html page.'''

	def test(self, handler):
		return os.path.isdir(handler.absolute_path) and \
			   not os.path.isfile(self.index_path(handler))

	def act(self, handler):
		self.list_dir(handler, handler.absolute_path)

class case_cgi_file(base_case):
	'''Something executable.'''

	def test(self, handler):
		return os.path.isfile(handler.absolute_path) and \
			   handler.absolute_path.endswith('.py')

	def act(self, handler):
		self.run_cgi(handler, handler.absolute_path)

class case_always_fail(base_case):
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
			 case_cgi_file(),
			 case_existing_file(),
			 case_directory_index_file(),
			 case_directory_no_index_file(),
			 case_always_fail()]

	Listing_Page = '''\
		<html>
			<body>
				<ul>{0}</ul>
			</body>
		</html>
	'''

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