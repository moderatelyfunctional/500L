import http.server

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
				<p>Hello, web!</p>
			</body>
		</html>
	'''

	# def create_page(self):
	# 	pass

	# def send_page(self, page):

	# Handles a GET request
	def do_GET(self):
		self.send_response(200)
		self.send_header("Content-Type", "text/html")
		self.send_header("Content-Length", str(len(self.Page)))
		self.end_headers()
		self.wfile.write(self.Page.encode('utf-8')) # Strings in Python3 are Unicode so have to convert to binary

if __name__ == '__main__':
	serverAddress = ('', 8080) # run on the current machine with port 8080
	server = http.server.HTTPServer(serverAddress, RequestHandler)
	server.serve_forever()

	'''
	a browser requesting http://localhost:8080 sends a GET request for the server and
	another request for /favicon.ico, an icon to put on the browser tab
	'''