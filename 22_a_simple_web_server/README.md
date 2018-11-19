Project for a simple webserver based on http://aosabook.org/en/500L/a-simple-web-server.html

Language: Python3  
Libraries: os, subprocess, http.server

To run  
`python3 server.py`

There are a few cases of interest covered below that are handled by the webserver.

#### case_no_file
http://localhost:8080/doesntexist

#### case_existing_file
http://localhost:8080/index.html

#### case_directory_index_file
http://localhost:8080/

#### case_directory_no_index_file
http://localhost:8080/no_index/

#### case_cgi_file
http://localhost:8080/cgi_curr_time.py
