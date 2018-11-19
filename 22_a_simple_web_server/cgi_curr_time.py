from datetime import datetime

html_output = '''\
	<html>
		<body>
			<p>Generated {0}</p>
		</body>
	</html>
'''

print(html_output.format(datetime.now()))