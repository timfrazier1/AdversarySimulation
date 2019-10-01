#!/usr/bin/python
import sys
import json
import base64
import requests
file_contents = open(sys.argv[1], 'rb').read()
encoded_contents = base64.b64encode(file_contents)
payload = {'app': encoded_contents}
r = requests.post('https://192.168.38.110/rest/app',
                auth=('admin', sys.argv[2]),
                data=json.dumps(payload),
                verify=False)
print r.status_code
print r.text
