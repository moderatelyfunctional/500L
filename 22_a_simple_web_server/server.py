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

	def create_page(self):
		values = {
			'date_time'   : self.date_time_string(),
			'client_host' : self.client_address[0],
			'client_port' : self.client_address[1],
			'command'     : self.command,
			'path'        : self.path
		}

	def send_page(self, page):
		self.send_response(200)
		self.send_header("Content-Type", "text/html")
		self.send_header("Content-Length", str(len(self.Page)))
		self.end_headers()
		self.wfile.write(self.Page.encode('utf-8')) # Strings in Python3 are Unicode so have to convert to binary

	# Handles a GET request
	def do_GET(self):
		page = self.create_page()
		self.send_page(page)

if __name__ == '__main__':
	serverAddress = ('', 8080) # run on the current machine with port 8080
	server = http.server.HTTPServer(serverAddress, RequestHandler)
	server.serve_forever()

	'''
	a browser requesting http://localhost:8080 sends a GET request for the server and
	another request for /favicon.ico, an icon to put on the browser tab
	'''