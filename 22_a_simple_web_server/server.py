import os
import http.server

class ServerException(Exception):
	'''For internal error reporting.'''
	pass

'''
BaseHTTPRequestHandler parses incoming HTTP requests and calls 
do_x where x in (GET|POST|PUT).

Overriding the appropriate do_x function calls that function instead 
for the given HTTP request.
'''
class RequestHandler(http.server.BaseHTTPRequestHandler):
	'''Handles HTTP requests by returning a fixed 'page'.'''

	# Page to send back
	Page = '''\
		<html>
			<body>
				<table>
					<tr> <td>Header</td>      <td>Value</td>          </tr>
					<tr> <td>Date</td>        <td>{date_time}</td>    </tr>
					<tr> <td>Client Host</td> <td>{client_host}</td>  </tr>
					<tr> <td>Client Port</td> <td>{client_port}s</td> </tr>
					<tr> <td>Command</td>     <td>{command}</td>      </tr>
					<tr> <td>Path</td>        <td>{path}</td>         </tr>
				</table>
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

			# figure out what exactly is being requested
			absolute_path = os.getcwd() + self.path

			# if it doesn't exist...
			if not os.path.exists(absolute_path):
				raise ServerException("'{0}' not found".format(self.path))

			# ...it's a file...
			elif os.path.isfile(absolute_path):
				self.handle_file(absolute_path)

			# ...it's something else
			else:
				raise ServerException("Unknown object '{0}'".format(self.path))

		# handle errors
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